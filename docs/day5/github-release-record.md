# GitHub Public Release Record

## Release Information

| Attribute | Value |
|---|---|
| Repository | zhangxiaojing0313/plane-ai-testing-project |
| Visibility | **PUBLIC** |
| Default Branch | main |
| First Public Commit | `7b2d40ef691358ae86a5a17545f14f6cbdd03686` |
| Commit Message | feat: complete Plane QA five-day testing project |
| Release Date | 2026-07-14 |
| Committed Files | 221 |
| Local git identity | zhangxiaojing0313 / 2055005751@qq.com |
| Push Method | `gh repo create` with `--push` flag |
| Remote URL | https://github.com/zhangxiaojing0313/plane-ai-testing-project |

## Release Content

The repository contains the complete five-day AI-assisted full-stack QA project for Plane Community Edition v1.3.1.

### Final Test Statistics

| Layer | Unique Tests | Pass | Fail | Pass Rate |
|---|---|---|---|---|
| API Validation | 8 | 8 | 0 | 100% |
| API Regression | 29 | 29 | 0 | 100% |
| **API Unique Total** | **37** | **37** | **0** | **100%** |
| **Database** | **19** | **19** | **0** | **100%** |
| **Playwright UI** | **10** | **10** | **0** | **100%** |
| **Unique Business Tests** | **66** | **66** | **0** | **100%** |

> UI Credential Smoke (1 test) is a CI pre-check and is not counted in the 66 unique business tests.

### Jenkins CI

| Attribute | Value |
|---|---|
| Job | plane-qa-pipeline |
| Final Build | #10 |
| Result | **SUCCESS** |
| Agent | plane-qa-runner-v2 |
| Stages | 12 |
| Output | Pipeline PASSED - all tests green, zero residue. |

### Known Items

| Item | Status |
|---|---|
| UI-007 | Flaky observation — first run timeout, retry #1 passed. Classified as automation stability item, NOT a Plane product defect. |
| junit-ui.xml | Missing from Jenkins Build #10 original archive — likely `cp` path issue in Jenkinsfile post step. Does not affect build conclusion. |

## Security

- ✅ Sensitive information scan passed before commit
- ✅ No `.env`, `auth-state.json`, `node_modules`, or `.venv` committed
- ✅ No real API keys, passwords, tokens, or private keys in repository
- ✅ Jenkins credentials managed exclusively via Jenkins `withCredentials`
- ✅ Console log contains Jenkins masking (`ha://`) for all credential values
- ✅ `.gitignore` correctly excludes sensitive files and build artifacts
- ✅ Evidence directories protected from aggressive gitignore patterns

## Evidence

- Jenkins Build #10 original console log: `evidence/jenkins-build-10/jenkins-original/console.log`
- Jenkins Build #10 original archive: `evidence/jenkins-build-10/jenkins-original/archive/`
- SHA-256 checksums: `evidence/jenkins-build-10/jenkins-original/SHA256SUMS.txt`
- Local equivalent reports (reference only): `evidence/local-equivalent-reports/`
- Evidence index: `.qa/evidence/INDEX.md`
