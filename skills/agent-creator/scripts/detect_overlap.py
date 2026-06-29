"""CLI script that analyzes responsibility overlap between existing agents.

Usage:
    python -m scripts.detect_overlap [--dirs DIR ...] [--threshold 0.3] [--json]

Behavior:
    1. Discover all agent profiles in the given directories
    2. Extract keywords from each profile's description + responsibilities section
    3. Compute Jaccard similarity for each agent pair
    4. Report pairs at or above the threshold as overlap warnings
"""

import argparse
import json
import sys
from pathlib import Path

from scripts.utils import (
    extract_keywords,
    find_agent_profiles,
    parse_agent_profile,
)


def compute_jaccard(set_a: set[str], set_b: set[str]) -> float:
    """Compute the Jaccard similarity of two sets: |A ∩ B| / |A ∪ B|."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def extract_agent_keywords(profile: dict) -> set[str]:
    """Extract keywords from a profile's description + responsibilities section."""
    texts: list[str] = []

    # description (frontmatter)
    desc = profile["frontmatter"].get("description", "")
    if isinstance(desc, str) and desc:
        texts.append(desc)

    # Responsibilities section
    responsibility = profile["sections_content"].get("Responsibilities", "")
    if responsibility:
        texts.append(responsibility)

    combined = " ".join(texts)
    return extract_keywords(combined)


def analyze_overlaps(
    directories: list[Path] | None = None,
    threshold: float = 0.3,
) -> dict:
    """Analyze overlap between agents and return a result dict.

    Returns:
        {
            "agents": list[str],
            "overlaps": list[dict],
            "matrix": list[list[float]],
        }
    """
    profiles_paths = find_agent_profiles(directories)

    if not profiles_paths:
        return {
            "agents": [],
            "overlaps": [],
            "matrix": [],
        }

    # Extract keywords for each agent
    agents: list[str] = []
    keywords_map: dict[str, set[str]] = {}

    for path in profiles_paths:
        profile = parse_agent_profile(path)
        name = profile["filename"]
        agents.append(name)
        keywords_map[name] = extract_agent_keywords(profile)

    n = len(agents)

    # Compute the similarity matrix
    matrix: list[list[float]] = [[0.0] * n for _ in range(n)]
    overlaps: list[dict] = []

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
                continue
            sim = compute_jaccard(keywords_map[agents[i]], keywords_map[agents[j]])
            matrix[i][j] = round(sim, 4)

            # Only warn on the upper triangle of the matrix (avoid duplicates)
            if i < j and sim >= threshold:
                shared = sorted(keywords_map[agents[i]] & keywords_map[agents[j]])
                pct = int(sim * 100)
                overlaps.append({
                    "agent_a": agents[i],
                    "agent_b": agents[j],
                    "similarity": round(sim, 4),
                    "shared_keywords": shared,
                    "warning": f"Overlap is high ({pct}%)",
                })

    # Sort by descending similarity
    overlaps.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "agents": agents,
        "overlaps": overlaps,
        "matrix": matrix,
    }


def format_text(result: dict, threshold: float) -> str:
    """Format the analysis result as human-readable text."""
    lines: list[str] = []
    agents = result["agents"]

    lines.append("=== Agent Responsibility Overlap Analysis ===")
    lines.append("")
    lines.append(f"Analyzed: {len(agents)} agents")
    lines.append(f"Threshold: {threshold}")
    lines.append("")

    if not agents:
        lines.append("No agent profiles found.")
        return "\n".join(lines)

    # Agent list
    lines.append("Agents:")
    for i, name in enumerate(agents, 1):
        lines.append(f"  {i}. {name}")
    lines.append("")

    # Overlap warnings
    overlaps = result["overlaps"]
    if overlaps:
        lines.append(f"Overlap warnings ({len(overlaps)}):")
        lines.append("")
        for overlap in overlaps:
            pct = int(overlap["similarity"] * 100)
            lines.append(f"  ⚠️  {overlap['agent_a']} ↔ {overlap['agent_b']}: {pct}%")
            if overlap["shared_keywords"]:
                kw_str = ", ".join(overlap["shared_keywords"][:10])
                if len(overlap["shared_keywords"]) > 10:
                    kw_str += f" +{len(overlap['shared_keywords']) - 10} more"
                lines.append(f"      Shared keywords: {kw_str}")
            lines.append("")
    else:
        lines.append("No overlap warnings. Responsibilities are well separated across agents.")
        lines.append("")

    # Similarity matrix (shown only when there are few agents)
    if len(agents) <= 10:
        lines.append("Similarity matrix:")
        # Header: shorten agent names
        short_names = [name.replace(".md", "")[:12] for name in agents]
        header = "            " + "  ".join(f"{n:>12}" for n in short_names)
        lines.append(header)
        for i, name in enumerate(short_names):
            row_vals = "  ".join(f"{result['matrix'][i][j]:>12.2f}" for j in range(len(agents)))
            lines.append(f"{name:>12}{row_vals}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze responsibility overlap between agents.",
        usage="python -m scripts.detect_overlap [--dirs DIR ...] [--threshold 0.3] [--json]",
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        type=Path,
        default=None,
        help="Directories to search for agent profiles (default: ~/.claude/agents/, ~/.config/opencode/agents/)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="Overlap warning threshold (default: 0.3, range: 0.0~1.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output the result in JSON format",
    )

    args = parser.parse_args()

    # Validate the threshold range
    if not (0.0 <= args.threshold <= 1.0):
        print(f"Error: threshold must be in the range 0.0~1.0 (got: {args.threshold})", file=sys.stderr)
        sys.exit(1)

    result = analyze_overlaps(
        directories=args.dirs,
        threshold=args.threshold,
    )

    if args.output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result, args.threshold))

    # Exit code 1 if there are overlap warnings
    sys.exit(1 if result["overlaps"] else 0)


if __name__ == "__main__":
    main()
