#!/usr/bin/env bash
# =============================================================================
#  run-demo.sh — OpenRouter docs pipeline
#  Stages: SDK snippet extraction → spec enrichment → docs.json
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Args ─────────────────────────────────────────────────────────────────────
if [ "$#" -gt 0 ]; then
  echo "Unknown argument(s): $*" >&2
  exit 1
fi

# ── Paths ────────────────────────────────────────────────────────────────────
OPENAPI_INPUT="./openrouter-openapi.yaml"
OPENAPI_ENRICHED="./openrouter-openapi-enriched.yaml"
SNIPPETS_JSON="./snippets.json"
DOCS_OUTPUT="./docs-output"

# Pre-built SDK dirs with Speakeasy docs
PY_SDK_DIR="./mintlify-demo-python"
TS_SDK_DIR="./mintlify-demo-typescript"

# ── Helpers ──────────────────────────────────────────────────────────────────
hr() { echo ""; echo "══════════════════════════════════════════════════════"; }
section() { hr; echo "  $1"; hr; }

check_python() {
  if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found on PATH" >&2
    exit 1
  fi
}

check_pyyaml() {
  if ! python3 -c "import yaml" &>/dev/null; then
    echo "  Installing PyYAML..."
    pip3 install pyyaml -q
  fi
}

# ── Pre-flight ────────────────────────────────────────────────────────────────
section "Pre-flight checks"

check_python
check_pyyaml

if [ ! -f "$OPENAPI_INPUT" ]; then
  echo "ERROR: OpenAPI spec not found at $OPENAPI_INPUT" >&2
  exit 1
fi
echo "  OpenAPI spec : $OPENAPI_INPUT"
echo "  Python       : $(python3 --version)"

# Count operations for summary
OP_COUNT=$(python3 - <<'EOF'
import yaml
with open("./openrouter-openapi.yaml") as f:
    spec = yaml.safe_load(f)
n = sum(
    1
    for methods in spec.get("paths", {}).values()
    for m, op in methods.items()
    if m in ("get","post","put","patch","delete","head","options") and isinstance(op, dict)
)
print(n)
EOF
)
echo "  Operations   : $OP_COUNT"

# =============================================================================
# STEP 1 — Use pre-built SDKs
# =============================================================================
section "Step 1 — Use pre-built SDK outputs"

echo "  Python    : $PY_SDK_DIR"
echo "  TypeScript: $TS_SDK_DIR"
EXTRACT_PY_DIR="$PY_SDK_DIR"
EXTRACT_TS_DIR="$TS_SDK_DIR"

# =============================================================================
# STEP 2 — Extract code snippets
# =============================================================================
section "Step 2 — Extract code snippets from SDK docs"

echo "  Python SDK   : $EXTRACT_PY_DIR"
echo "  TypeScript SDK: $EXTRACT_TS_DIR"

if [ ! -d "$EXTRACT_PY_DIR" ] && [ ! -d "$EXTRACT_TS_DIR" ]; then
  echo "  No SDK output dirs found — skipping snippet extraction."
  echo "  Pipeline will produce docs from raw spec (no code examples)."
  echo '{}' > "$SNIPPETS_JSON"
else
  python3 scripts/extract-snippets.py \
    --python-dir="$EXTRACT_PY_DIR" \
    --typescript-dir="$EXTRACT_TS_DIR" \
    --output="$SNIPPETS_JSON"
  echo "  Snippets written to $SNIPPETS_JSON"
fi

# Count how many operations got snippets
SNIPPET_COUNT=$(python3 -c "import json; d=json.load(open('$SNIPPETS_JSON')); print(len(d))")
echo "  Operations with snippets : $SNIPPET_COUNT"

# =============================================================================
# STEP 3 — Inject x-codeSamples into enriched spec
# =============================================================================
section "Step 3 — Inject x-codeSamples into OpenAPI spec"

python3 scripts/inject-code-samples.py \
  --input="$OPENAPI_INPUT" \
  --snippets="$SNIPPETS_JSON" \
  --output="$OPENAPI_ENRICHED"

echo "  Enriched spec written to $OPENAPI_ENRICHED"

# =============================================================================
# STEP 4 — Scaffold docs.json and introduction.mdx
# =============================================================================
section "Step 4 — Scaffold docs.json and introduction.mdx"

# Mintlify auto-generates all API pages from the OpenAPI spec — no MDX per
# endpoint needed. scaffold-mint.py writes docs.json (with "openapi" nav),
# introduction.mdx, and copies the enriched spec into docs-output/.
python3 scripts/scaffold-mint.py \
  --output-dir="$DOCS_OUTPUT" \
  --openapi="$OPENAPI_ENRICHED" \
  --fallback="$OPENAPI_INPUT"

echo "  docs.json written to $DOCS_OUTPUT/docs.json"
echo "  introduction.mdx written to $DOCS_OUTPUT/introduction.mdx"
echo "  spec copied to $DOCS_OUTPUT/$(basename "$OPENAPI_ENRICHED")"

# =============================================================================
# STEP 5 — Summary
# =============================================================================
section "Summary"

echo "  Operations processed     : $OP_COUNT"
echo "  Operations with snippets : $SNIPPET_COUNT"
echo "  Output directory         : $DOCS_OUTPUT"
echo ""
echo "  To preview with Mintlify:"
echo ""
echo "      cd $DOCS_OUTPUT"
echo "      npx mintlify dev"
echo ""
echo "  Done!"
hr
