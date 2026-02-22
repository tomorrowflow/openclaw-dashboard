# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenClaw Dashboard is a zero-dependency, local browser-based monitoring dashboard for OpenClaw AI agents. It aggregates gateway health, cost tracking, cron jobs, active sessions, sub-agent activity, and token usage into 10 dashboard panels.

**Hard constraint: zero external dependencies.** No npm, no pip, no CDN, no external fonts, no build tools. Frontend is vanilla HTML/CSS/JS in a single `index.html`. Backend is Python stdlib only. Bash uses POSIX-compatible commands.

## Architecture

```
Browser (index.html)  →  GET /api/refresh  →  server.py  →  refresh.sh (bash + inline Python)
                                                                    ↓
Browser  ←  render dashboard  ←  data.json (atomic write, gitignored)
```

- **`index.html`** (~1,160 lines) — Single-file frontend: embedded CSS (~250 lines) + JS (~750 lines). Glass morphism UI with 6 built-in themes via 19 CSS custom properties.
- **`server.py`** (~195 lines) — Python `http.server` subclass. Serves static files + `/api/refresh` endpoint with 30s debounce and thread lock.
- **`refresh.sh`** (~774 lines) — Bash wrapper with inline Python (heredoc). Reads `~/.openclaw/` data, generates atomic `data.json` with 35+ keys.
- **`config.json`** — Runtime configuration (bot name, theme, panels, alerts, server settings). Priority: CLI flags > env vars > config.json > defaults.
- **`themes.json`** — 6 built-in theme definitions (3 dark + 3 light).

### Frontend Patterns

- Global state: `D` (current data), `prevD` (previous snapshot), tab vars (`uTab`, `srTab`, `stTab`), `chartDays`
- Dirty checking via `sectionChanged()` — compares JSON-stringified data to skip unchanged DOM updates
- All renders wrapped in `requestAnimationFrame` for batching
- Scroll position preservation on re-render
- XSS safety: always use `esc()` for user-facing text, `safeColor()` for hex color validation
- DOM access helper: `$()` wraps `document.getElementById`

### Backend Patterns

- Inline Python in bash via heredoc (`<< 'PYEOF'...PYEOF`)
- Subprocess timeout: 15s limit on refresh.sh execution
- No `shell=True` in subprocess calls
- Atomic file writes (write to `.tmp`, then move)
- GMT+8 timezone hardcoded for "today" calculations
- Model name normalization: `anthropic/claude-opus-4-6` → `Claude Opus 4.6`

## Commands

```bash
# Run the server (default: localhost:8080)
python3 server.py
python3 server.py --bind 0.0.0.0 --port 9090   # LAN access

# Run all tests
python3 -m pytest tests/ -v

# Run static tests only (no server needed)
python3 -m pytest tests/test_frontend.py tests/test_data_schema.py -v

# Run a single test file
python3 -m pytest tests/test_critical.py -v

# Run a single test by name
python3 -m pytest tests/test_critical.py -k "test_name" -v

# Run test suite via script
bash tests/run_tests.sh
```

There is no build step, no linter, and no formatter configured.

## Testing Conventions

Tests use pytest + unittest across 4 files in `tests/`:
- `test_server.py` — Integration tests (starts its own server instance)
- `test_data_schema.py` — Static schema validation of data.json structure
- `test_frontend.py` — Static analysis/pattern matching on source files (XSS safety, CORS, etc.)
- `test_critical.py` — Critical area tests (TC1-TC32)

When changing CSS: test with all 6 built-in themes (switch via the palette button).
When changing charts: test both 7d and 30d views across all 3 chart types.

## Security Notes

- Localhost-only by default; LAN mode (`--bind 0.0.0.0`) has no authentication
- CORS restricted to localhost (never use wildcard `*`)
- `data.json` contains sensitive data (session keys, costs, PIDs) — it's gitignored
- Bash scripts use `set -euo pipefail`
