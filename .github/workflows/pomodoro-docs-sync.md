---
description: Detect code changes under 1.pomodoro/ and update documentation to keep specs aligned with source code
on:
  push:
    branches: [main]
    paths:
      - "1.pomodoro/**"
      - "!1.pomodoro/docs/**"
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
safe-outputs:
  create-pull-request:
    title-prefix: "docs(pomodoro): "
    labels: [documentation]
    draft: true
---

# Pomodoro Documentation Sync

You are an AI agent responsible for keeping the documentation under `1.pomodoro/docs/` aligned with the source code under `1.pomodoro/`.

## Your Task

When code changes are pushed to `1.pomodoro/`, analyze the current source code and update the documentation to reflect the actual implementation.

## Steps

1. **Read the source code** under `1.pomodoro/`:
   - `app.py` — Flask application factory and configuration
   - `models/` — Data models and schemas
   - `repositories/` — Data access layer (repository pattern)
   - `services/` — Business logic layer
   - `routes/api.py` — REST API endpoints and their request/response formats
   - `static/js/` — Frontend JavaScript modules (timerCore.js, timerUI.js, progressRing.js)
   - `static/css/` — Stylesheets
   - `templates/` — HTML templates
   - `tests/` — Test files for understanding expected behavior

2. **Read the existing documentation** under `1.pomodoro/docs/` (if any exists).

3. **Read existing design documents** for reference:
   - `1.pomodoro/architecture.md` — Original architecture design
   - `1.pomodoro/features.md` — Feature specifications

4. **Compare and identify discrepancies** between the documentation and the actual source code:
   - New endpoints or changed API contracts
   - New or modified data models
   - Changed business logic or service behavior
   - New or updated frontend components
   - Configuration changes

5. **Update or create documentation files** under `1.pomodoro/docs/`:
   - `1.pomodoro/docs/api-reference.md` — REST API reference (endpoints, request/response formats, status codes)
   - `1.pomodoro/docs/architecture.md` — Current architecture overview (layers, dependencies, patterns)
   - `1.pomodoro/docs/data-models.md` — Data model specifications
   - `1.pomodoro/docs/frontend.md` — Frontend module documentation (JS modules, UI components)

6. **Create a pull request** with the documentation updates using `create-pull-request` safe output.
   - Title: `docs(pomodoro): sync documentation with latest code changes`
   - Body should summarize what documentation was updated and why.

## Guidelines

- Write documentation in Japanese (日本語) to match the existing project documentation style.
- Be precise and factual — only document what the code actually does, not what it should do.
- Include code examples where helpful (e.g., API request/response examples).
- If there are no discrepancies and documentation is up to date, use `noop` to signal no changes needed.
- Do NOT modify any source code — only update documentation files.
- Keep documentation concise and well-structured with clear headings.
