# Evidence Index

## Day 1 — Project Synchronization

- Timestamp: 2026-07-12T19:41:37+08:00
- Scope: Day 1 project synchronization from Windows to qa-linux.
- Source: C:\Users\zhangxiaojing\Documents\plane-ai-testing-project
- Target: /home/tester/qa-workspace/plane-ai-testing-project
- Project commit: not recorded; no Git commit was created for this operation.
- Environment: qa-linux as user tester, verified by SSH before transfer.

### Commands and results

| Operation | Result | Evidence |
| --- | --- | --- |
| Source-directory and key-file preflight | PASS | README.md, CLAUDE.md, pytest.ini, playwright.config.ts, and both scripts were present |
| Remote identity | PASS | hostname returned qa-linux; whoami returned tester |
| Transfer method | PASS | SCP explicit safe manifest; no duplicate project root |
| Exclusions | PASS | .git, caches, virtual environments, reports, .env, plane.env, and credential files were not in the transfer manifest |
| dos2unix | BLOCKED | Command was not installed on qa-linux; original error was preserved |
| Line-ending fallback | PASS | sed normalized only the two shell scripts |
| Script permissions and syntax | PASS | both scripts are executable and pass bash -n |
| Key-file and layout check | PASS | required files exist at target root; nested project root is absent |
| Directory tree | PASS | tree -a -L 3 completed on the target |

### Artifacts and limitations

- Artifact paths: target project files and this index.
- Test cases, Plane deployment, Docker checks, API calls, UI tests, database assertions, and test reports were not executed during synchronization.
- No passwords, cookies, API keys, tokens, or real environment-variable values were recorded.

---

## Day 2 — Requirements Analysis & API Exploration

- Timestamp: 2026-07-12 (evening) – 2026-07-13 (early)
- Scope: Test requirements analysis, API endpoint exploration, test case design.
- Evidence: evidence/day2/ (environment snapshots, API response samples).

---

## Day 3 — API Automation & Playwright Core Flows

- Timestamp: 2026-07-13
- Scope: API automated tests, Playwright UI core flows, permission testing.
- Evidence: evidence/day3/ (API test reports, UI HTML reports, screenshots).
- Reports: reports/day3-api-*.html, reports/day3-ui-html/, reports/day3-summary.md.

---

## Day 4 — Database Assertions & Jenkins Pipeline

- Timestamp: 2026-07-13
- Scope: Database schema validation, API-DB cross-assertions, Jenkins Pipeline setup.
- Evidence: evidence/day4/ (DB test reports, Jenkins build artifacts).
- Reports: reports/day4-api-*.html, reports/day4-db-*.html, reports/day4-phase1-summary.md.

---

## Day 5 — Final Report & Evidence Archive

- Timestamp: 2026-07-14
- Scope: Jenkinsfile credential consolidation, Build #10 final run, report generation, evidence archival.

### Jenkins Build #10 — Final SUCCESS

| Attribute | Value |
|---|---|
| Job | plane-qa-pipeline |
| Build | #10 |
| Agent | plane-qa-runner-v2 |
| Result | SUCCESS |
| Stages | 12/12 passed |
| API Validation | 8/8 PASS |
| API Regression | 29/29 PASS |
| Database Tests | 19/19 PASS |
| Playwright UI | 10/10 PASS |
| Cleanup | AUTO-D residue: 0 |

### Final Reports

| Document | Path |
|---|---|
| Final Test Report | docs/day5/final-test-report.md |
| Build #10 Summary | docs/day5/jenkins-build-10-summary.md |
| Project Retrospective | docs/day5/project-retrospective.md |
| Interview Summary | docs/day5/interview-project-summary.md |

### Build Evidence — Original (from Jenkins Build #10)

| Artifact | Path | Source |
|---|---|---|
| Console Log | evidence/jenkins-build-10/jenkins-original/console.log | qa-jenkins container, Build #10 log |
| API Validation HTML | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/api-validation.html | Jenkins archiveArtifacts |
| API Regression HTML | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/api-regression.html | Jenkins archiveArtifacts |
| DB Full HTML | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/db-full.html | Jenkins archiveArtifacts |
| JUnit API Validation | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/junit-api-validation.xml | Jenkins archiveArtifacts |
| JUnit API Regression | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/junit-api-regression.xml | Jenkins archiveArtifacts |
| JUnit DB | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/junit-db.xml | Jenkins archiveArtifacts |
| Playwright HTML | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/playwright-report/index.html | Jenkins archiveArtifacts |
| SHA-256 Checksums | evidence/jenkins-build-10/jenkins-original/SHA256SUMS.txt | Generated post-copy |

### Build Evidence — Local Equivalent (reference only)

| Artifact | Path | Note |
|---|---|---|
| Local Reports | evidence/local-equivalent-reports/ | Same test suites, local run; NOT Build #10 original |

### Missing from Jenkins Original Archive

| Artifact | Status |
|---|---|
| junit-ui.xml (Playwright UI JUnit) | Not found in archive — likely cp path issue in Jenkinsfile post step |

### Security

- No .env files in evidence
- No auth-state.json in evidence
- No API keys, passwords, or tokens in any committed or archived file
- All credential values managed exclusively in Jenkins

---

## Overall Summary

| Phase | Status | Key Deliverables |
|---|---|---|
| Day 1 | ✅ | Project init, Plane deployment, environment baseline |
| Day 2 | ✅ | Requirements analysis, API exploration, test case design |
| Day 3 | ✅ | API automation, Playwright core flows |
| Day 4 | ✅ | DB assertions, Jenkins Pipeline |
| Day 5 | ✅ | Credential consolidation, Build #10 SUCCESS, final reports |

**Final Result: 66 unique business tests, 100% pass rate, zero residue, recommended for delivery.**
