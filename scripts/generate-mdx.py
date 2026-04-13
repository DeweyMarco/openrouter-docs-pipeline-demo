#!/usr/bin/env python3
"""
generate-mdx.py

Reads openrouter-openapi-enriched.yaml (or falls back to the raw spec) and
generates one MDX file per operation, grouped by tag into subfolders.

Output layout:
    ./docs-output/api-reference/<tag-slug>/<operation-slug>.mdx

Usage:
    python3 scripts/generate-mdx.py \
        [--input ./openrouter-openapi-enriched.yaml] \
        [--fallback ./openrouter-openapi.yaml] \
        [--output-dir ./docs-output/api-reference]
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Slug helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert a string to a lowercase kebab-case slug."""
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    return text.lower()


def operation_slug(op_id: str) -> str:
    """Convert a camelCase operationId to kebab-case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", op_id)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1)
    return s2.lower()


# ---------------------------------------------------------------------------
# MDX rendering
# ---------------------------------------------------------------------------

def indent(text: str, spaces: int = 0) -> str:
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())


def render_code_samples(code_samples: list[dict]) -> str:
    """Render x-codeSamples as a Mintlify <CodeGroup> block."""
    blocks = []
    for sample in code_samples:
        lang = sample.get("lang", "")
        label = sample.get("label", lang)
        source = sample.get("source", "")
        blocks.append(f"```{lang} {label}\n{source}\n```")
    inner = "\n\n".join(blocks)
    return f"<CodeGroup>\n{inner}\n</CodeGroup>"


def render_mdx(
    path: str,
    method: str,
    op: dict,
) -> str:
    summary = op.get("summary", f"{method.upper()} {path}")
    description = op.get("description", "")
    code_samples = op.get("x-codeSamples", [])

    # Frontmatter
    # Escape double-quotes inside title/description
    safe_title = summary.replace('"', '\\"')
    safe_desc = description.replace('"', '\\"').replace("\n", " ").strip()

    lines = ['---']
    lines.append(f'title: "{safe_title}"')
    if safe_desc:
        lines.append(f'description: "{safe_desc}"')
    lines.append(f'openapi: "{method.upper()} {path}"')
    lines.append('---')

    if code_samples:
        lines.append("")
        lines.append("## Code Examples")
        lines.append("")
        lines.append(render_code_samples(code_samples))

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_spec(path: Path) -> dict:
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MDX files from enriched OpenAPI spec")
    parser.add_argument("--input", default="./openrouter-openapi-enriched.yaml", help="Enriched OpenAPI spec")
    parser.add_argument("--fallback", default="./openrouter-openapi.yaml", help="Raw spec to fall back to if enriched missing")
    parser.add_argument("--output-dir", default="./docs-output/api-reference", help="Output directory for MDX files")
    args = parser.parse_args()

    try:
        import yaml  # noqa: F401
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    # Pick spec file
    spec_path = Path(args.input)
    if not spec_path.exists():
        spec_path = Path(args.fallback)
        if not spec_path.exists():
            print(f"ERROR: Neither {args.input} nor {args.fallback} found.", file=sys.stderr)
            sys.exit(1)
        print(f"WARNING: Enriched spec not found; using fallback {spec_path}", file=sys.stderr)
    else:
        print(f"Using spec: {spec_path}", file=sys.stderr)

    spec = load_spec(spec_path)
    output_dir = Path(args.output_dir)

    generated = 0
    with_snippets = 0

    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method not in ("get", "post", "put", "patch", "delete", "head", "options"):
                continue
            if not isinstance(op, dict):
                continue

            op_id = op.get("operationId") or slugify(f"{method}-{path}")
            tags = op.get("tags", ["default"])
            # Use first tag for folder grouping
            tag_slug = slugify(tags[0])
            op_file = operation_slug(op_id) + ".mdx"

            out_path = output_dir / tag_slug / op_file
            out_path.parent.mkdir(parents=True, exist_ok=True)

            mdx = render_mdx(path, method, op)
            out_path.write_text(mdx, encoding="utf-8")
            generated += 1

            if op.get("x-codeSamples"):
                with_snippets += 1

    print(f"Generated {generated} MDX files ({with_snippets} with code snippets) in {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
