# Jenkins Pipeline Design

**Date:** 2026-07-13  
**Version:** Day 4 Phase 2A  

---

## 1. Pipeline Stages

| Stage | Purpose | Parallel? |
|-------|---------|-----------|
| 1. Checkout / Sync Source | rsync from /opt/plane-source:ro to workspace | No |
| 2. Environment Preflight | Verify tools, network, DB access | No |
| 3. Python Environment | Create CI venv, install deps | No |
| 4. Node Dependencies | npm ci, playwright install chromium | No |
| 5. Create Temporary CI .env | Generate .env from Jenkins Credentials | No |
| 6. API Validation | 400 Bad Request tests (8 cases) | No |
| 7. API Regression | Full API suite (37 cases) | No |
| 8. Database Tests | DB assertions (19 cases) | No |
| 9. Playwright UI Tests | UI automation (10 collected) | No |
| 10. Cleanup Verification | API residue check + auto-clean | No |
| 11. Publish Test Results | JUnit report ingestion | No |
| 12. Archive Reports | HTML reports, evidence | No |

**No parallel execution** — avoids test data conflicts, port contention, and resource overloading on qa-linux.

## 2. Jenkins Credentials Design

| Credential ID | Type | Injected As | Used For |
|---------------|------|-------------|----------|
| `plane-api-key` | Secret text | `$PLANE_API_KEY` | API tests + DB cleanup |
| `plane-ui-email` | Secret text | `$PLANE_UI_EMAIL` | Playwright login |
| `plane-ui-password` | Secret text | `$PLANE_UI_PASSWORD` | Playwright login |

**All credentials:**
- Defined in Jenkins UI (Manage Jenkins → Credentials)
- Referenced by ID in Jenkinsfile
- Injected as environment variables at runtime
- NEVER hardcoded in Jenkinsfile, Dockerfile, or source code
- Temporary .env deleted in `post always`

## 3. Local Source Mode (Current — Day 4)

```
/opt/plane-source (host, read-only mount)
    │
    ▼ rsync (exclude .env, node_modules, .venv, etc.)
    │
${WORKSPACE} (Jenkins agent workspace)
    │
    ▼ tests execute here
```

### Excluded from sync:
- `.env`, `.venv`, `node_modules`, `.playwright`
- `reports`, `evidence` (runtime outputs)
- `test-results`, `playwright-report`
- `__pycache__`, `.pytest_cache`, `*.pyc`
- `.git`

## 4. Day 5 SCM Mode (Future)

Replace Stage 1 with:

```groovy
stage('1. Checkout') {
    steps {
        checkout scm
    }
}
```

After GitHub publishing, Jenkins will checkout directly from Git.

## 5. Test Statistics

| Suite | Unique Cases | Source |
|-------|-------------|--------|
| API Tests | 37 | `pytest tests/api --collect-only` |
| DB Tests | 19 | `pytest tests/db --collect-only` |
| Playwright | 10 | `npx playwright test tests/ui --list` |
| **Total collected** | **66** | |

**Note:** API Validation (8) is a subset of API Regression (37). Unique API = 37, not 37+8.

## 6. Cleanup Strategy

| Phase | Method |
|-------|--------|
| During tests | Each destructive test cleans its own data |
| Stage 10 | API list check → auto-delete leftover AUTO-D-* |
| Post always | rm .env, rm auth-state.json, rm .venv-ci |
| Archive | Reports + evidence only (no .env, no creds) |

## 7. Report Archiving

| Artifact | Path |
|----------|------|
| JUnit API Validation | `reports/junit-api-validation.xml` |
| JUnit API Regression | `reports/junit-api-regression.xml` |
| JUnit DB | `reports/junit-db.xml` |
| JUnit UI | `reports/junit-ui.xml` |
| HTML API Validation | `reports/api-validation.html` |
| HTML API Regression | `reports/api-regression.html` |
| HTML DB Full | `reports/db-full.html` |
| HTML Playwright | `reports/playwright-report/index.html` |
| Evidence | `archive/evidence/` |

## 8. Failure Handling

| Stage Failure | Action |
|---------------|--------|
| Any stage fails | `post always` executes cleanup |
| Cleanup fails | Logged, does not fail the build |
| API residue found | Auto-delete attempted; logs warning |
| .env not deleted | `rm -f` in post (best-effort) |

## 9. Rollback Steps

If pipeline misbehaves:
1. Stop agent: `docker stop plane-qa-runner-agent`
2. Fix Jenkinsfile in source
3. Restart agent
4. No controller restart needed
