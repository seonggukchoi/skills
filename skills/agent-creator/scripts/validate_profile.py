"""CLI script that checks the structural validity of an agent profile.

Usage:
    python -m scripts.validate_profile <agent-profile.md> [--json]

Checks:
    1. frontmatter presence and YAML validity
    2. presence of required fields (description, mode)
    3. whether mode is "subagent"
    4. temperature range (0.0~1.0)
    5. whether the tools field contains only valid tools
    6. warning when the model field is present
    7. presence of the 10 required sections
    8. cross-section consistency check (keyword-based)
"""

import argparse
import json
import sys
from pathlib import Path

from scripts.utils import (
    REQUIRED_SECTIONS,
    VALID_MODES,
    detect_profile_format,
    extract_keywords,
    get_format_spec,
    parse_agent_profile,
)


def validate(filepath: Path) -> dict:
    """Validate a profile and return a result dict.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "sections": {"found": list[str], "missing": list[str]},
            "score": int,
        }
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check that the file exists
    if not filepath.exists():
        return {
            "valid": False,
            "errors": [f"File not found: {filepath}"],
            "warnings": [],
            "sections": {"found": [], "missing": list(REQUIRED_SECTIONS)},
            "score": 0,
        }

    profile = parse_agent_profile(filepath)
    fm = profile["frontmatter"]

    # Detect the format (Claude Code / OpenCode) — apply per-format rules
    fmt = detect_profile_format(fm)
    spec = get_format_spec(fmt)

    # ── Score components ──
    field_score = 0       # Required fields: 20 points max
    section_score = 0     # Section completeness: 50 points max (5 per section)
    consistency_score = 0  # Consistency: 30 points max

    # ────────────────────────────────────────────
    # 1. frontmatter presence and YAML validity
    # ────────────────────────────────────────────
    if not profile["frontmatter_raw"]:
        errors.append("frontmatter is missing (a --- ... --- block is required)")
    elif not fm:
        errors.append("Failed to parse the frontmatter YAML")

    # ────────────────────────────────────────────
    # 2. Presence of required fields (description, mode)
    # ────────────────────────────────────────────
    required_fields = spec["required_fields"]
    per_field = 20 // len(required_fields) if required_fields else 0
    for field in required_fields:
        if field in fm:
            field_score += per_field  # required fields total 20 points
        else:
            errors.append(f"Missing required frontmatter field: {field} ({spec['label']} format)")

    # ────────────────────────────────────────────
    # 3. Whether mode is "subagent"
    # ────────────────────────────────────────────
    if spec["check_mode"] and "mode" in fm:
        mode_val = str(fm["mode"]).strip().lower()
        if mode_val not in VALID_MODES:
            errors.append(
                f"Invalid mode value: '{fm['mode']}' "
                f"(allowed: {', '.join(VALID_MODES)})"
            )

    # ────────────────────────────────────────────
    # 4. temperature range (0.0~1.0)
    # ────────────────────────────────────────────
    if "temperature" in fm:
        try:
            temp = float(fm["temperature"])
            if not (0.0 <= temp <= 1.0):
                errors.append(
                    f"temperature is out of range: {temp} (0.0~1.0 required)"
                )
        except (ValueError, TypeError):
            errors.append(f"Cannot convert the temperature value to a number: {fm['temperature']}")

    # ────────────────────────────────────────────
    # 5. Whether the tools field contains only valid tools
    # ────────────────────────────────────────────
    tools_list: list[str] = []
    if "tools" in fm:
        raw_tools = fm["tools"]
        if isinstance(raw_tools, str):
            # String separated by commas or whitespace
            tools_list = [t.strip().strip("[]'\"") for t in raw_tools.replace(",", " ").split() if t.strip()]
        elif isinstance(raw_tools, dict):
            tools_list = list(raw_tools.keys())
        elif isinstance(raw_tools, list):
            tools_list = [str(t).strip() for t in raw_tools]

        valid_tools = spec["valid_tools"]
        invalid_tools = []
        for t in tools_list:
            if not t:
                continue
            if spec["allow_mcp_tools"] and t.startswith("mcp__"):
                continue  # MCP tools (mcp__server__tool) are allowed
            if t not in valid_tools:
                invalid_tools.append(t)
        if invalid_tools:
            errors.append(
                f"Invalid tools: {', '.join(invalid_tools)} "
                f"(allowed: {', '.join(valid_tools)})"
            )

    # ────────────────────────────────────────────
    # 6. Warning when the model field is present
    # ────────────────────────────────────────────
    if spec["warn_on_model"] and "model" in fm:
        warnings.append(
            "The model field is set. "
            "Model selection is decided at runtime, so removing it is recommended."
        )

    # ────────────────────────────────────────────
    # 7. Presence of the 10 required sections
    # ────────────────────────────────────────────
    sections_found = profile["sections_found"]
    sections_missing = profile["sections_missing"]
    section_score = len(sections_found) * 5  # 5 points per section, up to 50

    for section in sections_missing:
        errors.append(f"Missing required section: {section}")

    # ────────────────────────────────────────────
    # 8. Cross-section consistency check (keyword-based)
    # ────────────────────────────────────────────
    sections_content = profile["sections_content"]

    # 8-a. Whether the Mission keywords also appear in Responsibilities
    mission_consistency = _check_keyword_overlap(
        sections_content.get("Mission", ""),
        sections_content.get("Responsibilities", ""),
        "Mission",
        "Responsibilities",
        warnings,
    )

    # 8-b. Whether the tools enabled in tools are referenced in Authority & Limits
    tools_consistency = _check_tools_in_authority(
        tools_list,
        sections_content.get("Authority & Limits", ""),
        warnings,
    )

    # Compute consistency score (30 points max: mission-responsibility 15, tools-authority 15)
    consistency_score = int(mission_consistency * 15 + tools_consistency * 15)

    # ── Final score ──
    total_score = field_score + section_score + consistency_score
    total_score = max(0, min(100, total_score))

    # Invalid if there is any error
    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "format": spec["label"],
        "errors": errors,
        "warnings": warnings,
        "sections": {
            "found": sections_found,
            "missing": sections_missing,
        },
        "score": total_score,
    }


def _check_keyword_overlap(
    source_text: str,
    target_text: str,
    source_name: str,
    target_name: str,
    warnings: list[str],
) -> float:
    """Return the keyword-overlap ratio between two sections (0.0~1.0).

    The fraction of source_text keywords that also appear in target_text.
    """
    if not source_text or not target_text:
        return 0.0

    source_kw = extract_keywords(source_text)
    target_kw = extract_keywords(target_text)

    if not source_kw:
        return 0.0

    overlap = source_kw & target_kw
    ratio = len(overlap) / len(source_kw)

    if ratio < 0.2 and source_kw:
        warnings.append(
            f"The core keywords of '{source_name}' are barely reflected in '{target_name}' "
            f"(overlap: {len(overlap)}/{len(source_kw)})"
        )

    return ratio


def _check_tools_in_authority(
    tools_list: list[str],
    authority_text: str,
    warnings: list[str],
) -> float:
    """Return the fraction of tools listed in tools that are referenced in the Authority & Limits section (0.0~1.0)."""
    if not tools_list:
        # No tools means no check is needed → treat as full score
        return 1.0

    if not authority_text:
        warnings.append(
            "tools is set but there is no 'Authority & Limits' section, so consistency cannot be verified"
        )
        return 0.0

    authority_lower = authority_text.lower()
    found_count = 0
    missing_tools: list[str] = []

    for tool in tools_list:
        if tool.lower() in authority_lower:
            found_count += 1
        else:
            missing_tools.append(tool)

    ratio = found_count / len(tools_list)

    if missing_tools:
        warnings.append(
            f"Tools defined in tools are not mentioned in 'Authority & Limits': "
            f"{', '.join(missing_tools)}"
        )

    return ratio


def format_text(result: dict, filepath: Path) -> str:
    """Format the validation result as human-readable text."""
    lines: list[str] = []
    lines.append(f"=== Profile validation: {filepath.name} ===")
    lines.append("")

    # Score and validity
    status = "✅ Valid" if result["valid"] else "❌ Invalid"
    lines.append(f"Format: {result.get('format', '-')}")
    lines.append(f"Status: {status}")
    lines.append(f"Score: {result['score']}/100")
    lines.append("")

    # Section status
    found = result["sections"]["found"]
    missing = result["sections"]["missing"]
    lines.append(f"Sections: {len(found)}/10 complete")
    if found:
        lines.append(f"  Found: {', '.join(found)}")
    if missing:
        lines.append(f"  Missing: {', '.join(missing)}")
    lines.append("")

    # Errors
    if result["errors"]:
        lines.append(f"Errors ({len(result['errors'])}):")
        for i, err in enumerate(result["errors"], 1):
            lines.append(f"  {i}. {err}")
        lines.append("")

    # Warnings
    if result["warnings"]:
        lines.append(f"Warnings ({len(result['warnings'])}):")
        for i, warn in enumerate(result["warnings"], 1):
            lines.append(f"  {i}. {warn}")
        lines.append("")

    if not result["errors"] and not result["warnings"]:
        lines.append("No problems found.")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check the structural validity of an agent profile.",
        usage="python -m scripts.validate_profile <agent-profile.md> [--json]",
    )
    parser.add_argument(
        "profile",
        type=Path,
        help="Path to the agent profile file to validate (.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output the result in JSON format",
    )

    args = parser.parse_args()
    filepath = args.profile.resolve()

    result = validate(filepath)

    if args.output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result, filepath))

    # Exit code 1 if invalid
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
