"""Shared utility module for agent-creator scripts."""

import re
from pathlib import Path


# The 10 required sections of an agent profile
REQUIRED_SECTIONS = [
    "Role Name",
    "Mission",
    "Responsibilities",
    "Authority & Limits",
    "Input",
    "Output",
    "Decision Principles",
    "Stop / Abort Rules",
    "Communication Rules",
    "Tone & Style",
]

# Section-matching patterns (English headers)
# NOTE: matching is anchored to the section word right after "#\s*" (search over the
# full body and match over a stripped line). \b on Mission/Input/Output prevents
# false positives like "# Outputting" while still matching real "# Output" headers,
# and a mid-header word such as "## Required Output Format" never matches.
SECTION_PATTERNS = {
    "Role Name": re.compile(r"#\s*Role\s*Name", re.IGNORECASE),
    "Mission": re.compile(r"#\s*Mission\b", re.IGNORECASE),
    "Responsibilities": re.compile(r"#\s*Responsibilities", re.IGNORECASE),
    "Authority & Limits": re.compile(r"#\s*Authority\s*&\s*Limits", re.IGNORECASE),
    "Input": re.compile(r"#\s*Input\b", re.IGNORECASE),
    "Output": re.compile(r"#\s*Output\b", re.IGNORECASE),
    "Decision Principles": re.compile(r"#\s*Decision\s*Principles", re.IGNORECASE),
    "Stop / Abort Rules": re.compile(r"#\s*Stop\s*/\s*Abort\s*Rules", re.IGNORECASE),
    "Communication Rules": re.compile(r"#\s*Communication\s*Rules", re.IGNORECASE),
    "Tone & Style": re.compile(r"#\s*Tone\s*(&|and)\s*Style", re.IGNORECASE),
}

# ─────────────────────────────────────────────────────────────
# frontmatter format definitions — supports both Claude Code / OpenCode
#
# The two environments use different agent frontmatter formats:
#   - OpenCode    : mode(subagent) required, lowercase tools (read/write/...)
#   - Claude Code : name required, model(inherit) is fine, uppercase tools (Read/Write/...) + Web/MCP tools
# The format is detected with detect_profile_format() and its rules looked up with get_format_spec().
# When a new format is added, add a branch to the constants below and to get_format_spec().
# ─────────────────────────────────────────────────────────────

# OpenCode format
OPENCODE_REQUIRED_FIELDS = ["description", "mode"]
OPENCODE_VALID_TOOLS = ["read", "write", "edit", "glob", "grep", "bash"]
VALID_MODES = ["subagent"]

# Claude Code format
CLAUDE_REQUIRED_FIELDS = ["name", "description"]
CLAUDE_VALID_TOOLS = [
    "Read", "Write", "Edit", "Glob", "Grep", "Bash",
    "WebSearch", "WebFetch", "Task", "TodoWrite",
    "NotebookEdit", "BashOutput", "KillShell", "SlashCommand",
]

RECOMMENDED_FRONTMATTER_FIELDS = ["temperature", "tools", "permission"]

# Backward compatibility: keep existing import paths (OpenCode defaults)
REQUIRED_FRONTMATTER_FIELDS = OPENCODE_REQUIRED_FIELDS
VALID_TOOLS = OPENCODE_VALID_TOOLS

# Format-agnostic use (e.g., tool-usage aggregation): all tools from both
ALL_VALID_TOOLS = OPENCODE_VALID_TOOLS + CLAUDE_VALID_TOOLS


def detect_profile_format(frontmatter: dict) -> str:
    """Detect the profile format from the frontmatter.

    Returns: 'opencode' | 'claude' | 'unknown'
    - 'mode' field present → OpenCode (mode is an OpenCode-only required field)
    - 'name' field present (no mode) → Claude Code
    - neither present → unknown (falls back to OpenCode rules during validation)
    """
    if "mode" in frontmatter:
        return "opencode"
    if "name" in frontmatter:
        return "claude"
    return "unknown"


def get_format_spec(fmt: str) -> dict:
    """Return the validation spec for a format. unknown falls back to OpenCode rules."""
    if fmt == "claude":
        return {
            "label": "Claude Code",
            "required_fields": CLAUDE_REQUIRED_FIELDS,
            "valid_tools": CLAUDE_VALID_TOOLS,
            "check_mode": False,       # Claude Code does not use the mode field
            "warn_on_model": False,    # model: inherit is normal
            "allow_mcp_tools": True,   # allow mcp__* tools
        }
    # opencode / unknown
    return {
        "label": "OpenCode",
        "required_fields": OPENCODE_REQUIRED_FIELDS,
        "valid_tools": OPENCODE_VALID_TOOLS,
        "check_mode": True,
        "warn_on_model": True,
        "allow_mcp_tools": False,
    }


def parse_agent_profile(filepath: Path) -> dict:
    """Parse an agent profile markdown file and return a structured dict.

    Returns:
        {
            "path": Path,
            "filename": str,
            "frontmatter": dict,
            "frontmatter_raw": str,
            "body": str,
            "sections_found": list[str],
            "sections_missing": list[str],
            "sections_content": dict[str, str],
        }
    """
    content = filepath.read_text(encoding="utf-8")
    result = {
        "path": filepath,
        "filename": filepath.name,
        "frontmatter": {},
        "frontmatter_raw": "",
        "body": "",
        "sections_found": [],
        "sections_missing": [],
        "sections_content": {},
    }

    # Extract frontmatter
    if content.startswith("---"):
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            result["frontmatter_raw"] = match.group(1)
            result["body"] = content[match.end():].strip()
            result["frontmatter"] = _parse_yaml_simple(match.group(1))
        else:
            result["body"] = content
    else:
        result["body"] = content

    # Find sections
    for section_name, pattern in SECTION_PATTERNS.items():
        if pattern.search(result["body"]):
            result["sections_found"].append(section_name)
        else:
            result["sections_missing"].append(section_name)

    # Extract content per section
    result["sections_content"] = _extract_sections(result["body"])

    return result


def _parse_yaml_simple(yaml_text: str) -> dict:
    """Simple YAML parsing (without external dependencies). Nested structures are preserved as strings."""
    data = {}
    current_key = None
    current_value_lines = []

    for line in yaml_text.split("\n"):
        # Top-level key: value pattern
        top_match = re.match(r"^([a-z_-]+)\s*:\s*(.*)", line)
        if top_match and not line.startswith(" ") and not line.startswith("\t"):
            # Save previous key
            if current_key is not None:
                data[current_key] = _finalize_value(current_value_lines)
            current_key = top_match.group(1)
            current_value_lines = [top_match.group(2).strip()]
        elif current_key is not None:
            current_value_lines.append(line)

    # Save last key
    if current_key is not None:
        data[current_key] = _finalize_value(current_value_lines)

    return data


def _finalize_value(lines: list[str]) -> str | dict:
    """Convert a YAML value into a string or a simple dict."""
    first = lines[0] if lines else ""

    # Single-line value
    if len(lines) == 1 or (len(lines) > 1 and all(not l.strip() for l in lines[1:])):
        return first.strip("'\"")

    # Multi-line: try to parse the nested structure into a dict
    nested = {}
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        kv_match = re.match(r"([a-z_*\"-]+)\s*:\s*(.*)", stripped)
        if kv_match:
            k = kv_match.group(1).strip("'\"")
            v = kv_match.group(2).strip("'\"")
            nested[k] = v

    if nested:
        return nested
    return first.strip("'\"")


def _extract_sections(body: str) -> dict[str, str]:
    """Extract the content of each section from the body."""
    sections = {}
    lines = body.split("\n")
    current_section = None
    current_lines = []

    for line in lines:
        is_heading = False
        for section_name, pattern in SECTION_PATTERNS.items():
            if pattern.match(line.strip()):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = section_name
                current_lines = []
                is_heading = True
                break
        if not is_heading and current_section:
            current_lines.append(line)

    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def find_agent_profiles(directories: list[Path] | None = None) -> list[Path]:
    """Find agent profile files.

    Default search paths:
    - ~/.claude/agents/
    - ~/.config/opencode/agents/
    """
    if directories is None:
        home = Path.home()
        directories = [
            home / ".claude" / "agents",
            home / ".config" / "opencode" / "agents",
        ]

    profiles = []
    seen_real: set[Path] = set()
    seen_name: set[str] = set()
    for d in directories:
        if d.exists() and d.is_dir():
            for f in sorted(d.glob("*.md")):
                # Collect the same real file (symlink) or the same filename
                # (the same agent placed under a different path) only once. E.g., even if
                # Claude/OpenCode copies of the same agent exist as separate files in
                # ~/.claude/agents and ~/.config/opencode/agents, count it once so it is not
                # flagged as a 100% self-overlap in overlap analysis/aggregation.
                # (Earlier directory wins — by default order ~/.claude/agents comes first)
                real = f.resolve()
                if real in seen_real or f.name in seen_name:
                    continue
                seen_real.add(real)
                seen_name.add(f.name)
                profiles.append(f)
    return profiles


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text (for overlap analysis)."""
    # Extract Korean + English words
    words = re.findall(r"[가-힣]+|[a-zA-Z]{2,}", text.lower())
    # Remove stopwords
    stopwords = {
        "the", "and", "for", "that", "this", "with", "are", "from", "have",
        "하는", "하고", "한다", "있는", "있다", "없는", "없다", "이다",
        "위한", "대한", "통해", "모든", "각각", "또는", "때문",
    }
    return {w for w in words if w not in stopwords and len(w) > 1}
