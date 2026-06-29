"""CLI script that generates a catalog of the entire agent organization.

Usage:
    python -m scripts.catalog [--dirs DIR ...] [--output catalog.md] [--json]

Behavior:
    1. Discover and parse all agent profiles
    2. Summarize each agent's role name, description, key responsibilities, temperature, tools
    3. Validation score (based on section count / 10)
    4. Overlap analysis (Jaccard similarity computed directly)
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from scripts.utils import (
    ALL_VALID_TOOLS,
    extract_keywords,
    find_agent_profiles,
    parse_agent_profile,
)


def _extract_role_name(profile: dict) -> str:
    """Extract the role name from a profile."""
    # Try extracting from the role-name section
    role_content = profile["sections_content"].get("Role Name", "")
    if role_content:
        # Use the first non-empty line as the role name
        for line in role_content.split("\n"):
            stripped = line.strip().strip("*#-").strip()
            if stripped:
                return stripped
    # Fallback: use the filename
    return profile["filename"].replace(".md", "")


def _extract_tools_list(profile: dict) -> list[str]:
    """Extract the tools list from a profile's frontmatter."""
    raw_tools = profile["frontmatter"].get("tools", "")
    if not raw_tools:
        return []

    if isinstance(raw_tools, str):
        return [t.strip().strip("[]'\"") for t in raw_tools.replace(",", " ").split() if t.strip()]
    elif isinstance(raw_tools, dict):
        return list(raw_tools.keys())
    elif isinstance(raw_tools, list):
        return [str(t).strip() for t in raw_tools]
    return []


def _extract_key_responsibilities(profile: dict, max_items: int = 3) -> list[str]:
    """Extract key items from the responsibilities section (up to max_items)."""
    content = profile["sections_content"].get("Responsibilities", "")
    if not content:
        return []

    items: list[str] = []
    for line in content.split("\n"):
        stripped = line.strip()
        # List item patterns (-, *, number.)
        if stripped and (stripped.startswith("-") or stripped.startswith("*") or
                         (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in ".)")):
            item = stripped.lstrip("-*0123456789.) ").strip()
            if item and len(item) > 3:
                items.append(item)
            if len(items) >= max_items:
                break

    return items


def _compute_jaccard(set_a: set[str], set_b: set[str]) -> float:
    """Compute the Jaccard similarity of two sets."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def _extract_agent_keywords(profile: dict) -> set[str]:
    """Extract keywords from a profile's description + responsibilities."""
    texts: list[str] = []
    desc = profile["frontmatter"].get("description", "")
    if isinstance(desc, str) and desc:
        texts.append(desc)
    responsibility = profile["sections_content"].get("Responsibilities", "")
    if responsibility:
        texts.append(responsibility)
    return extract_keywords(" ".join(texts))


def build_catalog(
    directories: list[Path] | None = None,
    overlap_threshold: float = 0.3,
) -> dict:
    """Build the full agent catalog data.

    Returns:
        {
            "generated_date": str,
            "total_agents": int,
            "agents": list[dict],
            "overlaps": list[dict],
            "tools_usage": dict[str, list[str]],
        }
    """
    profiles_paths = find_agent_profiles(directories)
    today = date.today().isoformat()

    agents_data: list[dict] = []
    keywords_map: dict[str, set[str]] = {}
    # Track which agents use each tool (aggregates both Claude Code/OpenCode tools)
    tools_usage: dict[str, list[str]] = {tool: [] for tool in ALL_VALID_TOOLS}

    for path in profiles_paths:
        profile = parse_agent_profile(path)
        filename = profile["filename"]

        role_name = _extract_role_name(profile)
        description = profile["frontmatter"].get("description", "")
        if isinstance(description, dict):
            description = str(description)
        temperature = profile["frontmatter"].get("temperature", "")
        tools_list = _extract_tools_list(profile)
        key_responsibilities = _extract_key_responsibilities(profile)

        # Section completeness (section count / 10)
        sections_found_count = len(profile["sections_found"])
        completeness = f"{sections_found_count}/10"

        # Update tool usage
        for tool in tools_list:
            if tool in tools_usage:
                tools_usage[tool].append(filename)

        # Extract keywords (for overlap analysis)
        keywords_map[filename] = _extract_agent_keywords(profile)

        agents_data.append({
            "filename": filename,
            "role_name": role_name,
            "description": description,
            "temperature": temperature,
            "tools": tools_list,
            "sections_found": sections_found_count,
            "completeness": completeness,
            "key_responsibilities": key_responsibilities,
        })

    # Overlap analysis (Jaccard similarity computed directly)
    overlaps: list[dict] = []
    agent_names = [a["filename"] for a in agents_data]

    for i in range(len(agent_names)):
        for j in range(i + 1, len(agent_names)):
            name_a = agent_names[i]
            name_b = agent_names[j]
            sim = _compute_jaccard(keywords_map[name_a], keywords_map[name_b])

            if sim >= overlap_threshold:
                shared = sorted(keywords_map[name_a] & keywords_map[name_b])
                overlaps.append({
                    "agent_a": name_a,
                    "agent_b": name_b,
                    "similarity": round(sim, 4),
                    "shared_keywords": shared,
                })

    overlaps.sort(key=lambda x: x["similarity"], reverse=True)

    # Drop tools that are not used
    tools_usage = {k: v for k, v in tools_usage.items() if v}

    return {
        "generated_date": today,
        "total_agents": len(agents_data),
        "agents": agents_data,
        "overlaps": overlaps,
        "tools_usage": tools_usage,
    }


def format_markdown(catalog: dict) -> str:
    """Format the catalog as markdown."""
    lines: list[str] = []

    lines.append("# Agent Catalog")
    lines.append("")
    lines.append(f"**Total agents**: {catalog['total_agents']}")
    lines.append(f"**Generated**: {catalog['generated_date']}")
    lines.append("")

    # ── Agent list table ──
    lines.append("## Agents")
    lines.append("")
    lines.append("| # | Agent | Description | Section completeness | temperature |")
    lines.append("|---|----------|------|-------------|-------------|")

    for i, agent in enumerate(catalog["agents"], 1):
        desc = agent["description"]
        # Truncate the description if it is too long
        if len(desc) > 50:
            desc = desc[:47] + "..."
        temp = agent["temperature"] if agent["temperature"] else "-"
        lines.append(
            f"| {i} | {agent['filename']} | {desc} | {agent['completeness']} | {temp} |"
        )

    lines.append("")

    # ── Overlap warnings ──
    lines.append("## Overlap Warnings")
    lines.append("")

    if catalog["overlaps"]:
        lines.append("| Agent A | Agent B | Similarity | Shared keywords |")
        lines.append("|-----------|-----------|--------|------------|")

        for overlap in catalog["overlaps"]:
            pct = f"{int(overlap['similarity'] * 100)}%"
            kw = ", ".join(overlap["shared_keywords"][:5])
            if len(overlap["shared_keywords"]) > 5:
                kw += f" +{len(overlap['shared_keywords']) - 5} more"
            lines.append(
                f"| {overlap['agent_a']} | {overlap['agent_b']} | {pct} | {kw} |"
            )
    else:
        lines.append("No overlap warnings.")

    lines.append("")

    # ── Tool usage ──
    lines.append("## Tool Usage")
    lines.append("")

    tools_usage = catalog["tools_usage"]
    if tools_usage:
        lines.append("| Tool | Agents using it | Agent list |")
        lines.append("|------|-----------------|-------------|")

        for tool in sorted(tools_usage.keys()):
            agent_list = tools_usage[tool]
            agents_str = ", ".join(agent_list)
            lines.append(f"| {tool} | {len(agent_list)} | {agents_str} |")
    else:
        lines.append("No agents use any tools.")

    lines.append("")

    return "\n".join(lines)


def format_text(catalog: dict) -> str:
    """Format the catalog as terminal text (same as markdown)."""
    return format_markdown(catalog)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a catalog of the entire agent organization.",
        usage="python -m scripts.catalog [--dirs DIR ...] [--output catalog.md] [--json]",
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        type=Path,
        default=None,
        help="Directories to search for agent profiles (default: ~/.claude/agents/, ~/.config/opencode/agents/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="File path to save the markdown catalog (prints to stdout if omitted)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="Overlap warning threshold (default: 0.3)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output the result in JSON format",
    )

    args = parser.parse_args()

    catalog = build_catalog(
        directories=args.dirs,
        overlap_threshold=args.threshold,
    )

    if args.output_json:
        output = json.dumps(catalog, ensure_ascii=False, indent=2)
    else:
        output = format_markdown(catalog)

    # Write to file or stdout
    if args.output and not args.output_json:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"Catalog saved: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
