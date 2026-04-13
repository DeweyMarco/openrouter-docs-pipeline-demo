#!/usr/bin/env python3
"""
scaffold-mint.py

Writes:
  - docs-output/docs.json          (Mintlify config with OpenAPI nav)
  - docs-output/introduction.mdx
  - docs-output/<spec-filename>    (copy of the enriched spec)

Mintlify auto-generates all API reference pages from the spec — no MDX
files per endpoint are needed.

Usage:
    python3 scripts/scaffold-mint.py \
        [--output-dir ./docs-output] \
        [--openapi ./openrouter-openapi-enriched.yaml] \
        [--fallback ./openrouter-openapi.yaml]
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


PRIMARY_COLOR = "#0D9373"
LIGHT_COLOR = "#07C983"


def load_spec(spec_path: Path, fallback_path: Path) -> tuple[dict, Path]:
    for p in (spec_path, fallback_path):
        if p.exists():
            import yaml
            with open(p) as f:
                return yaml.safe_load(f), p
    return {}, fallback_path


def build_docs_json(api_title: str, spec_filename: str) -> dict:
    return {
        "$schema": "https://mintlify.com/docs.json",
        "name": api_title,
        "theme": "mint",
        "colors": {
            "primary": PRIMARY_COLOR,
            "light": LIGHT_COLOR,
        },
        "navigation": {
            "tabs": [
                {
                    "tab": "Introduction",
                    "groups": [
                        {
                            "group": "Get Started",
                            "pages": ["introduction"],
                        }
                    ],
                },
                {
                    "tab": "API Reference",
                    "openapi": spec_filename,
                },
            ],
            "global": {
                "anchors": [
                    {
                        "anchor": "API Reference",
                        "href": "/api-reference",
                        "icon": "rectangle-terminal",
                    }
                ]
            },
        },
    }


def build_introduction(api_title: str, api_description: str) -> str:
    safe_desc = (api_description or "").replace('"', '\\"').replace("\n", " ").strip()
    lines = [
        "---",
        'title: "Introduction"',
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
        "<Note>",
        "  **Get Started** — Pick an endpoint from the sidebar to explore the API.",
        "</Note>",
        "",
    ]
    return "\n".join(line for line in lines if line is not None) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold docs.json and introduction.mdx")
    parser.add_argument("--output-dir", default="./docs-output")
    parser.add_argument("--openapi", default="./openrouter-openapi-enriched.yaml")
    parser.add_argument("--fallback", default="./openrouter-openapi.yaml")
    args = parser.parse_args()

    try:
        import yaml  # noqa: F401
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    spec, used_path = load_spec(Path(args.openapi), Path(args.fallback))
    info = spec.get("info", {})
    api_title = info.get("title", "API Reference")
    api_description = info.get("description", "")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy spec into docs-output so `mintlify dev` can find it
    spec_dest = output_dir / used_path.name
    shutil.copy2(used_path, spec_dest)

    docs_config = build_docs_json(api_title, used_path.name)
    docs_path = output_dir / "docs.json"
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(docs_config, f, indent=2)

    legacy_mint_path = output_dir / "mint.json"
    if legacy_mint_path.exists():
        legacy_mint_path.unlink()

    intro_path = output_dir / "introduction.mdx"
    intro_path.write_text(build_introduction(api_title, api_description), encoding="utf-8")


if __name__ == "__main__":
    main()
