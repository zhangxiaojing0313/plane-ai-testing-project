# QA Project Context

## Scope and verification state

- Product: Plane Community Edition.
- Project purpose: AI-assisted end-to-end testing practice for an enterprise project-management platform.
- Current phase: Day 1 project initialization only.
- Last verified date: 2026-07-12.
- Evidence: local static configuration checks only; no Linux host, Docker, Plane, API, database, or UI test execution has occurred.

## Target environment

- Target Linux host: qa-linux (user-provided target, not live-verified).
- Target Linux user: tester (user-provided target, not live-verified).
- Target project path: /home/tester/qa-workspace/plane-ai-testing-project (user-provided target, not live-verified).
- Planned Plane deployment path: /home/tester/qa-workspace/plane-selfhost (user-provided target, not live-verified).

## Test stack and assets

- API stack declared in requirements.txt: pytest, requests, pytest-html, python-dotenv, psycopg, jsonschema.
- UI stack declared in package.json and playwright.config.ts: Playwright, TypeScript, Chromium.
- Database target: PostgreSQL (user-provided project scope; connection details are unknown).
- Environment tooling target: Linux, Docker Compose, Jenkins.
- Existing tests and reports: none; placeholder directories only.

## Safety and collaboration constraints

- Secrets must remain in an untracked local .env file; no real values are recorded here.
- Plane deployment and test execution are outside the Day 1 initialization boundary until explicitly run.
- Codex and Claude Code must not edit the same file at the same time.
- Every future execution claim must point to a command, report, log, trace, screenshot, or other evidence.

## Known blockers and next action

- Blocker: target Linux environment has not been inspected or deployed.
- Next action: run scripts/collect-env.sh on qa-linux, then populate Day 1 baseline and deployment records from actual evidence.
