#!/usr/bin/env python3
"""
extract-snippets.py

Walks the Speakeasy-generated SDK docs/sdks/ folder for Python and TypeScript,
extracts code examples using the <!-- UsageSnippet operationID="..." --> markers,
and writes snippets.json.

Usage:
    python3 scripts/extract-snippets.py \
        [--python-dir ./mintlify-demo-python] \
        [--typescript-dir ./mintlify-demo-typescript] \
        [--output ./snippets.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Matches: <!-- UsageSnippet language="python" operationID="listModelsCount" ... -->
USAGE_SNIPPET_RE = re.compile(
    r'<!--\s*UsageSnippet\s[^>]*operationID="([^"]+)"[^>]*-->',
    re.IGNORECASE,
)

# Matches the first fenced code block after a marker
CODE_BLOCK_RE = re.compile(
    r'```(?:python|typescript|ts|javascript|js)[^\n]*\n(.*?)```',
    re.DOTALL | re.IGNORECASE,
)


def extract_snippets_from_readme(text: str) -> dict[str, str]:
    """Parse a README and return {operationId: code_snippet} using UsageSnippet markers."""
    results = {}
    for marker_match in USAGE_SNIPPET_RE.finditer(text):
        op_id = marker_match.group(1)
        # Find the very next code block after this marker
        rest = text[marker_match.end():]
        code_match = CODE_BLOCK_RE.search(rest)
        if code_match:
            code = code_match.group(1).strip()
            if code and op_id not in results:
                results[op_id] = code
    return results


def extract_for_language(sdk_dir: Path, lang: str) -> dict[str, str]:
    """Walk docs/sdks/ in the SDK dir and extract all snippets."""
    results = {}
    sdk_docs_dir = sdk_dir / "docs" / "sdks"

    if not sdk_docs_dir.exists():
        print(f"  [{lang}] docs/sdks/ not found in {sdk_dir}", file=sys.stderr)
        return results

    readme_files = list(sdk_docs_dir.rglob("README.md"))
    if not readme_files:
        print(f"  [{lang}] No README.md files found in {sdk_docs_dir}", file=sys.stderr)
        return results

    for readme_path in sorted(readme_files):
        try:
            text = readme_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [{lang}] Could not read {readme_path}: {e}", file=sys.stderr)
            continue
        snippets = extract_snippets_from_readme(text)
        results.update(snippets)

    print(
        f"  [{lang}] Scanned {len(readme_files)} README files, "
        f"found {len(results)} snippets",
        file=sys.stderr,
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract code snippets from Speakeasy SDK docs")
    parser.add_argument(
        "--python-dir", default="./mintlify-demo-python",
        help="Path to Python SDK output (must contain docs/sdks/)"
    )
    parser.add_argument(
        "--typescript-dir", default="./mintlify-demo-typescript",
        help="Path to TypeScript SDK output (must contain docs/sdks/)"
    )
    parser.add_argument("--output", default="./snippets.json", help="Output path for snippets.json")
    args = parser.parse_args()

    py_dir = Path(args.python_dir)
    ts_dir = Path(args.typescript_dir)

    py_snippets = extract_for_language(py_dir, "python") if py_dir.exists() else {}
    if not py_dir.exists():
        print(f"  [python] Directory not found: {py_dir}", file=sys.stderr)

    ts_snippets = extract_for_language(ts_dir, "typescript") if ts_dir.exists() else {}
    if not ts_dir.exists():
        print(f"  [typescript] Directory not found: {ts_dir}", file=sys.stderr)

    # Merge into combined structure
    snippets: dict[str, dict] = {}
    for op_id in set(py_snippets) | set(ts_snippets):
        snippets[op_id] = {}
        if op_id in py_snippets:
            snippets[op_id]["python"] = py_snippets[op_id]
        if op_id in ts_snippets:
            snippets[op_id]["typescript"] = ts_snippets[op_id]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(snippets, f, indent=2)

    print(f"Wrote {len(snippets)} operations with snippets to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
