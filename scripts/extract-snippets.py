#!/usr/bin/env python3
"""
extract-snippets.py

Walks Speakeasy-generated SDK output directories for Python and TypeScript,
finds usage examples, maps them to OpenAPI operationIds, and writes snippets.json.

Usage:
    python3 scripts/extract-snippets.py \
        [--python-dir ./speakeasy-python] \
        [--typescript-dir ./speakeasy-typescript] \
        [--output ./snippets.json]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_example_files(root: Path) -> list[Path]:
    """Return all files that are likely to contain usage examples."""
    candidates = []
    if not root.exists():
        return candidates

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        name_lower = path.name.lower()
        # Include: docs/ folder files, README, test/example files, usage.py/ts
        if (
            "docs" in path.parts
            or name_lower in ("readme.md",)
            or re.search(r"(example|usage|sample|test)", name_lower)
            or path.suffix in (".md", ".mdx")
        ):
            candidates.append(path)
    return candidates


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Code block extraction
# ---------------------------------------------------------------------------

PYTHON_FENCE_RE = re.compile(
    r"```python\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
TS_FENCE_RE = re.compile(
    r"```(?:typescript|ts|javascript|js)\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def extract_fenced_blocks(text: str, fence_re: re.Pattern) -> list[str]:
    return [m.group(1).strip() for m in fence_re.finditer(text)]


# ---------------------------------------------------------------------------
# OperationId detection
# ---------------------------------------------------------------------------

# Speakeasy tends to turn operationIds into method names on SDK objects.
# e.g. operationId "sendChatCompletionRequest" → sdk.chat.send_chat_completion_request()
# We look for the camelCase or snake_case form of the id in the snippet.

def camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snippet_mentions_operation(snippet: str, operation_id: str) -> bool:
    snake = camel_to_snake(operation_id)
    camel = operation_id
    # Check for the function/method name in various forms
    patterns = [
        snake,
        camel,
        # kebab-case (rare but possible in TS imports)
        snake.replace("_", "-"),
    ]
    snippet_lower = snippet.lower()
    for p in patterns:
        if p.lower() in snippet_lower:
            return True
    return False


# ---------------------------------------------------------------------------
# Per-language extraction
# ---------------------------------------------------------------------------

def extract_for_language(
    sdk_dir: Path,
    operation_ids: list[str],
    lang: str,
) -> dict[str, str]:
    """Return {operationId: best_snippet} for a given language SDK directory."""
    fence_re = PYTHON_FENCE_RE if lang == "python" else TS_FENCE_RE
    results: dict[str, str] = {}

    example_files = find_example_files(sdk_dir)
    if not example_files:
        print(f"  [{lang}] No example files found in {sdk_dir}", file=sys.stderr)
        return results

    # Build a pool: [(file_path, snippet_text)]
    pool: list[tuple[Path, str]] = []
    for f in example_files:
        text = read_text(f)
        blocks = extract_fenced_blocks(text, fence_re)
        # If no fenced blocks and it's a raw .py/.ts file, treat whole file as a snippet
        if not blocks and f.suffix in (".py", ".ts", ".js"):
            blocks = [text.strip()]
        for block in blocks:
            if block:
                pool.append((f, block))

    # Match snippets to operation IDs (first match wins per operation)
    for op_id in operation_ids:
        for _path, snippet in pool:
            if snippet_mentions_operation(snippet, op_id):
                results[op_id] = snippet
                break

    print(
        f"  [{lang}] Scanned {len(example_files)} files, "
        f"found {len(pool)} snippets, "
        f"matched {len(results)}/{len(operation_ids)} operations",
        file=sys.stderr,
    )
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract code snippets from Speakeasy SDK output")
    parser.add_argument("--python-dir", default="./speakeasy-python", help="Path to Python SDK output")
    parser.add_argument("--typescript-dir", default="./speakeasy-typescript", help="Path to TypeScript SDK output")
    parser.add_argument("--openapi", default="./openrouter-openapi.yaml", help="Path to OpenAPI spec (to read operationIds)")
    parser.add_argument("--output", default="./snippets.json", help="Output path for snippets.json")
    args = parser.parse_args()

    # Read operationIds from spec
    try:
        import yaml
        with open(args.openapi) as f:
            spec = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Could not read OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)

    operation_ids: list[str] = []
    for _path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method in ("get", "post", "put", "patch", "delete", "head", "options"):
                op_id = op.get("operationId")
                if op_id:
                    operation_ids.append(op_id)

    print(f"Found {len(operation_ids)} operations in spec", file=sys.stderr)

    py_dir = Path(args.python_dir)
    ts_dir = Path(args.typescript_dir)

    py_snippets = extract_for_language(py_dir, operation_ids, "python") if py_dir.exists() else {}
    ts_snippets = extract_for_language(ts_dir, operation_ids, "typescript") if ts_dir.exists() else {}

    # Merge into combined structure
    snippets: dict[str, dict] = {}
    all_ops_with_snippets = set(py_snippets) | set(ts_snippets)
    for op_id in all_ops_with_snippets:
        snippets[op_id] = {}
        if op_id in py_snippets:
            snippets[op_id]["python"] = py_snippets[op_id]
        if op_id in ts_snippets:
            snippets[op_id]["typescript"] = ts_snippets[op_id]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(snippets, f, indent=2)

    print(
        f"Wrote {len(snippets)} operations with snippets to {output_path}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
