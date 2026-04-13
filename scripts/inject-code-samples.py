#!/usr/bin/env python3
"""
inject-code-samples.py

Reads openrouter-openapi.yaml and snippets.json, injects x-codeSamples into
each operation that has a matching operationId, and writes the enriched spec.

Usage:
    python3 scripts/inject-code-samples.py \
        [--input ./openrouter-openapi.yaml] \
        [--snippets ./snippets.json] \
        [--output ./openrouter-openapi-enriched.yaml]
"""

import argparse
import json
import sys
from pathlib import Path


LANG_META = {
    "python": {"label": "Python", "lang": "python"},
    "typescript": {"label": "TypeScript", "lang": "typescript"},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject x-codeSamples into OpenAPI spec")
    parser.add_argument("--input", default="./openrouter-openapi.yaml", help="Input OpenAPI spec")
    parser.add_argument("--snippets", default="./snippets.json", help="snippets.json from extract-snippets.py")
    parser.add_argument("--output", default="./openrouter-openapi-enriched.yaml", help="Enriched output spec")
    args = parser.parse_args()

    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    # Load spec
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input spec not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        spec = yaml.safe_load(f)

    # Load snippets
    snippets_path = Path(args.snippets)
    if not snippets_path.exists():
        print(f"WARNING: snippets.json not found at {snippets_path}. Writing spec unchanged.", file=sys.stderr)
        snippets: dict = {}
    else:
        with open(snippets_path) as f:
            snippets = json.load(f)

    injected = 0
    skipped = 0

    for _path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method not in ("get", "post", "put", "patch", "delete", "head", "options"):
                continue
            if not isinstance(op, dict):
                continue

            op_id = op.get("operationId")
            if not op_id or op_id not in snippets:
                skipped += 1
                continue

            op_snippets = snippets[op_id]
            if not op_snippets:
                skipped += 1
                continue

            code_samples = []
            for lang_key in ("python", "typescript"):
                if lang_key in op_snippets:
                    meta = LANG_META[lang_key]
                    code_samples.append({
                        "lang": meta["lang"],
                        "label": meta["label"],
                        "source": op_snippets[lang_key],
                    })

            if code_samples:
                op["x-codeSamples"] = code_samples
                injected += 1
            else:
                skipped += 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Injected code samples into {injected} operations ({skipped} had none)", file=sys.stderr)
    print(f"Wrote enriched spec to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
