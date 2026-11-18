# restructure-readme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the repo into one `financial_agent/` package with no behaviour change, redesign the README, and redraw the diagrams as generated SVGs.

**Architecture:** `git mv` every module to its new place, rewrite imports mechanically using the spec's mapping table, verify by importing and booting the app with dummy env vars, then add the diagram script and the README.

**Tech stack:** Python, FastAPI, LangGraph, Streamlit, hand-drawn SVG via `sketch.py` (stdlib only).

**Spec:** [spec.md](spec.md) (decisions in [grill.md](grill.md))

## Global constraints

- Branch `refactor/restructure-readme` cut from `main`; PR targets `main`; no `dev` branch.
- Commit messages and PR text in English, short, with no mention of Claude, Anthropic or AI and no trailers. This overrides the harness attribution reminder per the user's global instructions.
- Runtime strings (`"file_controler"`, node ids, agent names, prompts) are not edited; only the folder is renamed to `file_controller`.
- No fixes for the non-goal findings (duplicate `upload_dir`, unused `update_memory` import, unused helpers); list them in the PR description.
- No `pyproject.toml`, no new license badge, no Python-version badge; `requirements.txt` and `.gitignore` untouched.
- README in English, sentence-case headers, no em dashes (use ` - `), every claim checked in the repo.
- Run everything from the repo root (relative `.env`, `temp/...` paths).

## Review focus

- Leftover old import path (`from config`, `from graph`, ...) in a file nobody imports at boot (for example `demo/streamlit_demo.py`): grep, not just import.
- Circular import between `agents/__init__.py` and `agents/graph.py` breaking after the rename: the boot check in Task 1 imports it.
- Old `.pyc` or empty old directories hiding a missed move: `git status` shows no old top-level `graph/`, `routers/`, `model/`, `dependencies/`.
- A README command that no longer works (`python app.py`): Task 4 runs each command or greps the path.
- An SVG label cut off at the edge or overlapping: Task 3 renders and reads the PNG.

---

### Task 1: Move into `financial_agent/` and fix imports

**Files:**
- Move (`git mv`): per the spec's target layout, `app.py` → `financial_agent/app.py`; `routers/{chat,health}.py` → `financial_agent/api/`; `dependencies/auth.py` → `financial_agent/api/auth.py`; `graph/` → `financial_agent/agents/` (with `file_controler` → `file_controller`); `memory/local.py` → `financial_agent/memory/local.py`; `config.py`, `logger.py`, `utils.py` → `financial_agent/core/`; `model/{chat_request,message}.py` → `financial_agent/core/models/`.
- Create: empty `__init__.py` in `financial_agent/`, `api/`, `core/`, `core/models/` (others are moved with their `__init__.py`).
- Modify: every moved file's imports; `financial_agent/app.py` `uvicorn.run("app:app", ...)` → `uvicorn.run("financial_agent.app:app", ...)`.

**Interfaces:**
- Produces: importable `financial_agent.app:app` (FastAPI instance) and `financial_agent.agents.app` (compiled graph), used by Tasks 2 and 4.

- [ ] **Step 1: Cut the branch.** `git switch -c refactor/restructure-readme` from `main`. Check: `git branch --show-current` prints it.
- [ ] **Step 2: Move the files** with `git mv` into the layout above. Check: `git status` shows only renames; no old top-level `graph/`, `routers/`, `model/`, `dependencies/` left.
- [ ] **Step 3: Rewrite imports** with the spec's import-mapping table (absolute paths such as `graph.file_controler.x` → `financial_agent.agents.file_controller.x`). In `agents/__init__.py` keep the relative imports, changing only `.file_controler` → `.file_controller`; in `agents/graph.py`, `from graph import (...)` → `from financial_agent.agents import (...)`.
- [ ] **Step 4: Grep for leftovers.**
  Run: `grep -rnE "^(from|import) (config|logger|utils|model|memory|graph|routers|dependencies|app)\b" -- $(git ls-files 'financial_agent/*.py')`
  Expected: no output.
- [ ] **Step 5: Boot check with dummy env vars.**
  Run: `OPENAI_API_KEY=x FASTAPI_KEYS='["k"]' AUTH_ENCRYPTION_KEY=x python -c "from fastapi.testclient import TestClient; from financial_agent.app import app; r = TestClient(app).get('/api/v1/health'); print(r.status_code)"`
  Expected: `200`. If `AUTH_ENCRYPTION_KEY` needs a real Fernet key to import, generate one with `cryptography.fernet.Fernet.generate_key()`.
- [ ] **Step 6: Commit.** `git add -A && git commit -m "Move code into financial_agent package"`

### Task 2: Move the demo

**Files:**
- Move: `streamlit_demo.py` → `demo/streamlit_demo.py`; `examples/` → `demo/examples/`.
- Modify: `demo/streamlit_demo.py` imports `logger`, `config` → `financial_agent.core.logger`, `financial_agent.core.config`. The earlier grep found no reference to `examples/` or PDF paths in the demo, so no path edits there.

**Interfaces:**
- Consumes: `financial_agent.core.config.configs`, `financial_agent.core.logger.logger` from Task 1.

- [ ] **Step 1: `git mv` the files, then fix the two imports.**
- [ ] **Step 2: Check the demo imports.** Run `grep -nE "^(from|import) (config|logger)\b" demo/streamlit_demo.py` → no output. Streamlit puts the script folder on `sys.path`, not the repo root, so the README must run it as `PYTHONPATH=. streamlit run demo/streamlit_demo.py`; confirm that `PYTHONPATH=. python -c "import ast; ast.parse(open('demo/streamlit_demo.py').read())"` parses and that no `ModuleNotFoundError` for `financial_agent` appears when the demo is started.
- [ ] **Step 3: Commit.** `git commit -am "Move demo and examples to demo/"`

### Task 3: Diagram script and SVGs

**Files:**
- Create: `docs/diagrams/make_diagrams.py` (copy of `~/.claude/skills/writing-readme/diagrams/sketch.py`), `docs/diagrams/PatrickHand-Latin.ttf`, `docs/diagrams/OFL.txt`, generated `docs/diagrams/pipeline.svg` and `docs/diagrams/layout.svg`.

**Interfaces:**
- Produces: the two SVGs embedded by Task 4. `make_diagrams.py` writes both when run as `python docs/diagrams/make_diagrams.py`; `example()` is replaced by `pipeline()` and `layout()` returning `Sketch` objects (width 2000, fixed seed per figure), using `Sketch.box`, `cylinder`, `frame`, `arrow`, `person`, `heading`.

- [ ] **Step 1: Verify the flow before drawing.** Read `agents/graph.py`, `agents/supervisor/graph.py`, `agents/analyzer/graph.py`, `agents/file_controller/graph.py`, `api/chat.py`; list the real edges. Draw only edges that exist: START → memory → planning → supervisor; supervisor ↔ analyzer / file_controller and their tools; supervisor → responser → END; memory ↔ local store (`memory/local.py`); SSE stream from `api/chat.py`. Check the PNG's "Tools description" / "Workers description" arrows against `planning/prompt.py` importing `members, tools_description` from `supervisor/prompt.py` before drawing them.
- [ ] **Step 2: Write `pipeline()` and `layout()`**, fills per the spec (lilac inputs, yellow LLM calls, green plain code, blue stores) with a short colour legend via `s.text`.
- [ ] **Step 3: Generate and render.**
  Run: `python docs/diagrams/make_diagrams.py`, then headless Chrome per the writing-readme skill (`--window-size=2000,1200 --screenshot=<scratchpad>/x.png file://$PWD/docs/diagrams/pipeline.svg`), then Read each PNG. Expected: no overlapping text, no label cut at an edge, no box too small for its bullets; fix and re-render until clean.
- [ ] **Step 4: Idempotence.** Run the script twice; the second run leaves the SVGs byte-identical (`git diff --stat docs/diagrams` after `git add` shows no change).
- [ ] **Step 5: Commit.** `git add docs/diagrams && git commit -m "Add generated architecture diagrams"`

### Task 4: README

**Files:**
- Modify: `README.md` (full rewrite).

**Interfaces:**
- Consumes: `docs/diagrams/pipeline.svg`, `docs/diagrams/layout.svg`, `docs/architecture.png`, `docs/SystemDesign.pdf`, `docs/diagrams/OFL.txt`.

- [ ] **Step 1: Write the README** in the spec's section order: header (title "Financial agent", tagline from the old README's purpose, shields for FastAPI / LangGraph / OpenAI only if each is in `requirements.txt` or `config.py`, anchor links), intro and at-a-glance table, architecture (both SVGs embedded as `<p align="center"><img src="docs/diagrams/x.svg" alt="<full sentence>" width="100%"></p>`, links to the old PNG and PDF, stack table in `<details>`), agent catalogue table in pipeline order, quickstart (3 numbered commands: `pip install -r requirements.txt`, create `.env` with `OPENAI_API_KEY`, `FASTAPI_KEYS`, `AUTH_ENCRYPTION_KEY`, then `python -m financial_agent.app`), `<details>` for the demo UI (`PYTHONPATH=. streamlit run demo/streamlit_demo.py`) and calling `POST /api/v1/chat/ainvoke`, project layout, tests ("none yet"), licenses (no license file stated; Patrick Hand SIL OFL 1.1 credit linking `docs/diagrams/OFL.txt`; how to regenerate the diagrams).
- [ ] **Step 2: Check every claim.** Counts of agents/tools/endpoints taken from the code with grep; each path in the README exists (`ls`); each command works or is grep-confirmed (module name, endpoint path, the API-key header name in `api/auth.py`); no em dashes (`grep -n "—" README.md` → no output).
- [ ] **Step 3: Commit.** `git commit -am "Redesign README"`

### Task 5: Pull request

- [ ] **Step 1: Final checks.** Re-run Task 1 Steps 4 and 5; `git status` clean.
- [ ] **Step 2: Push and open the PR** into `main` (ask the user before pushing, since it is outward-facing). Title in English, short; description in English listing: what moved, the `python app.py` → `python -m financial_agent.app` and `streamlit run` command changes, and the unchanged findings (duplicate `upload_dir`, unused `update_memory` import, possibly unused `convert_to_message` / `get_session_id`, no tests, no LICENSE). No attribution lines.

## Self-review

- Spec coverage: layout, import mapping, demo, diagrams, README, verification and PR notes each map to Tasks 1-5. The spec's open check about `examples/` references is resolved (no reference found).
- Type consistency: names used across tasks (`financial_agent.app:app`, `financial_agent.agents.app`, `make_diagrams.py`, `pipeline.svg`, `layout.svg`) match the spec.
- Proportion: the plan only writes out commands and checks, not the code bodies.
