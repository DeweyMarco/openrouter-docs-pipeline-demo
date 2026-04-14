# OpenRouter Docs Pipeline Demo

Takes an OpenAPI spec, injects code snippets from pre-built SDK docs, and outputs a Mintlify-ready site scaffold.

```
OpenAPI spec + pre-built SDK docs → snippets.json → enriched spec → docs.json + introduction.mdx + copied spec
```

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.9+ | `brew install python` |
| PyYAML | installed automatically by `run-demo.sh` |
| Mintlify (preview only) | `npm i -g mintlify` or use `npx` |

## Quickstart

```bash
cd demo1
./run-demo.sh
```

That's it. Output lands in `./docs-output/`. To preview:

```bash
cd docs-output
npx mintlify dev
```

`run-demo.sh` currently takes no arguments.

## Can it be run multiple times?

Yes. Every run overwrites its outputs cleanly:

| Output | Overwritten each run |
|--------|----------------------|
| `./snippets.json` | yes |
| `./openrouter-openapi-enriched.yaml` | yes |
| `./docs-output/` | yes (`docs.json`, `introduction.mdx`, and copied enriched spec) |

The input spec (`./openrouter-openapi.yaml`) is never modified.

## Pipeline stages

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1 | Use existing SDK doc dirs | `mintlify-demo-python/`, `mintlify-demo-typescript/` | source markdown for snippet extraction |
| 2 | `scripts/extract-snippets.py` | SDK dirs | `snippets.json` |
| 3 | `scripts/inject-code-samples.py` | spec + snippets | `openrouter-openapi-enriched.yaml` |
| 4 | `scripts/scaffold-mint.py` | enriched spec (+ fallback) | `docs-output/docs.json`, `docs-output/introduction.mdx`, copied spec |

Each script is independently runnable. Pass `--help` for options:

```bash
python3 scripts/extract-snippets.py --help
python3 scripts/inject-code-samples.py --help
python3 scripts/scaffold-mint.py --help
```

## Graceful degradation

If SDK doc dirs are missing, the pipeline continues without code snippets by writing
an empty `snippets.json`. The generated site scaffold still works; endpoint pages are
rendered by Mintlify from the OpenAPI spec.

## File structure

```
demo1/
├── run-demo.sh                         # main entrypoint
├── requirements.txt                    # PyYAML
├── openrouter-openapi.yaml             # input spec (untouched)
├── openrouter-openapi-enriched.yaml    # generated — spec + x-codeSamples
├── snippets.json                       # generated — operationId → {python, typescript}
├── scripts/
│   ├── extract-snippets.py
│   ├── inject-code-samples.py
│   └── scaffold-mint.py
├── mintlify-demo-python/               # pre-built Python SDK docs
├── mintlify-demo-typescript/           # pre-built TypeScript SDK docs
└── docs-output/
    ├── docs.json
    ├── introduction.mdx
    └── openrouter-openapi-enriched.yaml
```
