# SmartDesk — Governed Store Support Agent

SDAIA Academy Agentic AI Systems Engineering **capstone starter implementation**. A simple synthetic e-commerce support assistant with OpenRouter tool calling, three tools (including a real local MCP tool), a step-limited loop, context compaction, human-gated writes, traces, security tests, and A/B evaluation scaffolding.

> **Status:** Working source-code prototype. Offline mock smoke-tested; real OpenRouter and MCP integration must be tested in your environment. Not a production service or a claim of completed empirical evaluation.

## Use case
A shopper asks about order status, shipping, returns or refunds, and may request a support ticket. The assistant reads a synthetic order and store policy, drafts a ticket, and asks for approval. Ticket creation is performed separately only after an explicit user approval.

## Architecture
```
CLI / FastAPI -> SmartDesk Agent (OpenRouter LLM)
                  | get_order (read only)
                  | lookup_policy_mcp -> MCP stdio server -> local policy file
                  | draft_support_ticket (no write)
                  | steps <= 6, tools <= 8, compaction, trace
Human approval -> FastAPI /approve-ticket -> validation -> tickets.jsonl
```

## Setup
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.
2. `uv sync --extra dev`
3. `cp .env.example .env` and set `OPENROUTER_API_KEY` and a tool-capable `OPENROUTER_MODEL`. Do not commit `.env`.
4. `uv run python -m smartdesk.cli --question 'What is the status of ORD-1001?'`
5. Offline fallback: `uv run python -m smartdesk.cli --mock --question 'What is the status of ORD-1001?'`
6. API: `uv run uvicorn smartdesk.api:app --reload` then browse `http://127.0.0.1:8000/docs`.
7. Tests: `uv run pytest -q`.
8. Eval (real model): `uv run python evals/run_eval.py` (16 tasks x A/B = 32 calls, plus tool calls). Offline dry run: add `--mock`.

## Human approval
The model can only draft tickets. A real human must explicitly approve the exact order and issue:
```
curl -X POST http://127.0.0.1:8000/approve-ticket \
  -H 'Content-Type: application/json' \
  -d '{"order_id":"ORD-1001","issue":"Damaged item","approved":true}'
```
This local demo endpoint has no authentication and must not be publicly deployed.

## Eval and scoring
- 16 cases in `evals/cases.json`, automatic substring baseline grader; `evals/results.csv` is generated when run.
- A: minimal system prompt; B: hardened prompt and same hard code guards. This comparison tests prompt quality, **not** the hard guard effectiveness.
- Compute pass rate for A and B, review traces and count error categories (tool misuse, policy hallucination, wrong order, unsafe action, provider errors). For meaningful statistics repeat runs and inspect each result manually.
- Mock mode uses deterministic rules and **cannot** establish LLM quality or a real A/B improvement.
- For pass^k reliability, run each case k times and report fraction of tasks succeeding on every run.

## Capstone requirements mapping
| Requirement | Implementation | Evidence still needed |
|---|---|---|
| 3 tools, one MCP | `get_order`, `lookup_policy_mcp`, `draft_support_ticket` | Real API/MCP live trace |
| Context | policy file, bounded message context | Demonstrate actual compaction |
| Budgets | step/tool count, context length | Token/cost usage logging and dollar budget |
| Human approval | draft only; separate write endpoint | Live approval/rejection demo |
| 15+ evals, A/B | 16 cases, CSV runner | Real runs, error analysis and statistics |
| Security | allowlist, redaction, write guard, unit tests | Before/after attack traces |
| Reproducibility | uv, README, synthetic dataset | Clean-clone test, recorded demo |
| Production | FastAPI, health check | Auth, durable checkpoints, tracing backend, CI |

## Files
- `smartdesk/agent.py`: LLM loop, tool definitions, traces, compaction
- `smartdesk/mcp_server.py` / `mcp_client.py`: actual local MCP stdio transport
- `smartdesk/security.py`: deterministic guardrails and approved write
- `evals/`: A/B tasks and runner
- `docs/SECURITY.md`: threat model and attack validation plan

## Important limitations
No real user identities, no email sending, no payment or refund execution. The system does not implement a LangGraph workflow, which is optional if selecting the **Your Harness** track. Verify exact course grading with the instructor. Provider prices, model support, and SDK interfaces can change.

## References
- SDAIA Academy, course slides Day 4 p.31 (track 2 and minimum), Day 5 pp.5-8 (presentation and rubric), supplied by learner.
- [OpenRouter documentation](https://openrouter.ai/docs)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI](https://fastapi.tiangolo.com/)
