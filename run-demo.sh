#!/usr/bin/env bash
# =============================================================================
#  run-demo.sh — OpenRouter docs pipeline
#  Stages: SDK generation → snippet extraction → spec enrichment → MDX → mint.json
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Flags ────────────────────────────────────────────────────────────────────
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done

# ── Paths ────────────────────────────────────────────────────────────────────
OPENAPI_INPUT="./openrouter-openapi.yaml"
OPENAPI_ENRICHED="./openrouter-openapi-enriched.yaml"
SNIPPETS_JSON="./snippets.json"
PY_SDK_DIR="./speakeasy-python"
TS_SDK_DIR="./speakeasy-typescript"
DOCS_OUTPUT="./docs-output"
API_REF_DIR="$DOCS_OUTPUT/api-reference"

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
echo "  Dry-run mode : $DRY_RUN"
echo "  Python       : $(python3 --version)"

# Count operations for summary
OP_COUNT=$(python3 - <<'EOF'
import yaml, sys
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
# STEP 1 — Generate SDKs
# =============================================================================
section "Step 1 — Generate SDKs with Speakeasy"

SDK_STEP_OK=true

if $DRY_RUN; then
  echo "  [DRY RUN] Skipping Speakeasy SDK generation."
  echo "  Using existing SDK dirs: $PY_SDK_DIR  $TS_SDK_DIR"
else
  if ! command -v speakeasy &>/dev/null; then
    echo "  WARNING: speakeasy CLI not found on PATH — skipping SDK generation."
    SDK_STEP_OK=false
  else
    echo "  Generating Python SDK → $PY_SDK_DIR ..."
    if speakeasy generate sdk \
        --schema="$OPENAPI_INPUT" \
        --lang=python \
        --out="$PY_SDK_DIR" \
        --non-interactive 2>&1; then
      echo "  Python SDK generated."
    else
      echo "  WARNING: Python SDK generation failed — continuing without it."
      SDK_STEP_OK=false
    fi

    echo ""
    echo "  Generating TypeScript SDK → $TS_SDK_DIR ..."
    if speakeasy generate sdk \
        --schema="$OPENAPI_INPUT" \
        --lang=typescript \
        --out="$TS_SDK_DIR" \
        --non-interactive 2>&1; then
      echo "  TypeScript SDK generated."
    else
      echo "  WARNING: TypeScript SDK generation failed — continuing without it."
      SDK_STEP_OK=false
    fi
  fi
fi

# =============================================================================
# STEP 2 — Extract code snippets
# =============================================================================
section "Step 2 — Extract code snippets from SDK output"

PY_EXISTS=false
TS_EXISTS=false
[ -d "$PY_SDK_DIR" ] && PY_EXISTS=true
[ -d "$TS_SDK_DIR" ] && TS_EXISTS=true

if ! $PY_EXISTS && ! $TS_EXISTS; then
  echo "  No SDK output dirs found — skipping snippet extraction."
  echo "  Pipeline will produce MDX from raw spec (no code examples)."
  # Write an empty snippets.json so downstream scripts don't fail
  echo '{}' > "$SNIPPETS_JSON"
else
  echo "  Python SDK dir exists : $PY_EXISTS"
  echo "  TypeScript SDK dir exists : $TS_EXISTS"
  python3 scripts/extract-snippets.py \
    --python-dir="$PY_SDK_DIR" \
    --typescript-dir="$TS_SDK_DIR" \
    --openapi="$OPENAPI_INPUT" \
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
# STEP 4 — Generate MDX files
# =============================================================================
section "Step 4 — Generate MDX files"

python3 scripts/generate-mdx.py \
  --input="$OPENAPI_ENRICHED" \
  --fallback="$OPENAPI_INPUT" \
  --output-dir="$API_REF_DIR"

MDX_COUNT=$(find "$API_REF_DIR" -name "*.mdx" | wc -l | tr -d ' ')
echo "  MDX files written to $API_REF_DIR ($MDX_COUNT files)"

# =============================================================================
# STEP 5 — Scaffold mint.json and introduction.mdx
# =============================================================================
section "Step 5 — Scaffold mint.json and introduction.mdx"

python3 scripts/scaffold-mint.py \
  --api-ref-dir="$API_REF_DIR" \
  --output-dir="$DOCS_OUTPUT" \
  --openapi="$OPENAPI_ENRICHED" \
  --fallback="$OPENAPI_INPUT"

echo "  mint.json written to $DOCS_OUTPUT/mint.json"
echo "  introduction.mdx written to $DOCS_OUTPUT/introduction.mdx"

# =============================================================================
# STEP 6 — Summary
# =============================================================================
section "Summary"

echo "  Operations processed     : $OP_COUNT"
echo "  Operations with snippets : $SNIPPET_COUNT"
echo "  MDX files generated      : $MDX_COUNT"
echo "  Output directory         : $DOCS_OUTPUT"
echo ""
echo "  To preview with Mintlify:"
echo ""
echo "      cd $DOCS_OUTPUT"
echo "      npx mintlify dev"
echo ""
echo "  Done!"
hr
