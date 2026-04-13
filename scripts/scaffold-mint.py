#!/usr/bin/env python3
"""
scaffold-mint.py

Reads the docs-output/api-reference/ folder structure and generates:
  - docs-output/mint.json   (Mintlify config)
  - docs-output/introduction.mdx

Usage:
    python3 scripts/scaffold-mint.py \
        [--api-ref-dir ./docs-output/api-reference] \
        [--output-dir ./docs-output] \
        [--openapi ./openrouter-openapi-enriched.yaml] \
        [--fallback ./openrouter-openapi.yaml]
"""

import argparse
import json
import re
import sys
from pathlib import Path


PRIMARY_COLOR = "#0D9373"
LIGHT_COLOR = "#07C983"


def title_case(slug: str) -> str:
    """Convert a kebab-case slug to Title Case."""
    return " ".join(word.capitalize() for word in slug.replace("-", " ").split())


def load_spec(spec_path: Path, fallback_path: Path) -> dict:
    for p in (spec_path, fallback_path):
        if p.exists():
            import yaml
            with open(p) as f:
                return yaml.safe_load(f)
    return {}


def build_navigation(api_ref_dir: Path) -> list[dict]:
    """Build the navigation array by scanning the api-reference folder."""
    if not api_ref_dir.exists():
        return []

    groups = []
    # Sort tag folders alphabetically for deterministic output
    for tag_dir in sorted(api_ref_dir.iterdir()):
        if not tag_dir.is_dir():
            continue
        tag_label = title_case(tag_dir.name)
        pages = []
        for mdx_file in sorted(tag_dir.glob("*.mdx")):
            # Mintlify page paths are relative to the docs root, no extension
            rel = f"api-reference/{tag_dir.name}/{mdx_file.stem}"
            pages.append(rel)
        if pages:
            groups.append({"group": tag_label, "pages": pages})

    return groups


def build_mint_json(api_title: str, nav_groups: list[dict]) -> dict:
    return {
        "name": api_title,
        "colors": {
            "primary": PRIMARY_COLOR,
            "light": LIGHT_COLOR,
        },
        "anchors": [
            {
                "name": "API Reference",
                "icon": "rectangle-terminal",
                "url": "api-reference",
            }
        ],
        "navigation": [
            {
                "group": "Get Started",
                "pages": ["introduction"],
            },
            {
                "group": "API Reference",
                "pages": nav_groups,
            },
        ],
    }


def build_introduction(api_title: str, api_description: str) -> str:
    safe_title = api_title.replace('"', '\\"')
    safe_desc = (api_description or "").replace('"', '\\"').replace("\n", " ").strip()
    lines = [
        "---",
        f'title: "Introduction"',
        f'description: "{safe_desc}"' if safe_desc else "",
        "---",
        "",
        f"# {api_title}",
        "",
    ]
    if api_description:
        lines.append(api_description.strip())
        lines.append("")

    lines += [
        '<Note>',
        "  **Get Started** — Pick an endpoint from the sidebar to explore the API,",
        "  or jump straight to the [Chat Completions](/api-reference/chat/send-chat-completion-request) endpoint.",
        '</Note>',
        "",
    ]
    return "\n".join(line for line in lines if line is not None) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold mint.json and introduction.mdx")
    parser.add_argument("--api-ref-dir", default="./docs-output/api-reference", help="api-reference output folder")
    parser.add_argument("--output-dir", default="./docs-output", help="Root output folder (where mint.json goes)")
    parser.add_argument("--openapi", default="./openrouter-openapi-enriched.yaml", help="Enriched OpenAPI spec")
    parser.add_argument("--fallback", default="./openrouter-openapi.yaml", help="Fallback raw spec")
    args = parser.parse_args()

    try:
        import yaml  # noqa: F401
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    spec = load_spec(Path(args.openapi), Path(args.fallback))
    info = spec.get("info", {})
    api_title = info.get("title", "API Reference")
    api_description = info.get("description", "")

    api_ref_dir = Path(args.api_ref_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nav_groups = build_navigation(api_ref_dir)
    mint_config = build_mint_json(api_title, nav_groups)

    mint_path = output_dir / "mint.json"
    with open(mint_path, "w") as f:
        json.dump(mint_config, f, indent=2)
    print(f"Wrote {mint_path}", file=sys.stderr)

    intro_path = output_dir / "introduction.mdx"
    intro_path.write_text(build_introduction(api_title, api_description), encoding="utf-8")
    print(f"Wrote {intro_path}", file=sys.stderr)

    total_pages = sum(len(g["pages"]) for g in nav_groups)
    print(f"Navigation: {len(nav_groups)} tag groups, {total_pages} pages", file=sys.stderr)


if __name__ == "__main__":
    main()
