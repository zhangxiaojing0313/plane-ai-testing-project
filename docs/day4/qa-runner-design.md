# QA Runner Agent — Design Document

**Date:** 2026-07-13  
**Version:** Day 4 Phase 2A  

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│ qa-linux Host                                            │
│                                                          │
│  ┌──────────────┐    ┌──────────────────────────────┐   │
│  │ qa-jenkins    │    │ plane-qa-runner-agent         │   │
│  │ (Controller)  │    │ (Inbound Agent via WebSocket)  │   │
│  │ :8081         │◄──►│                               │   │
│  └──────────────┘    │  ┌──────────┐ ┌───────────┐   │   │
│                      │  │ Python   │ │ Node.js   │   │   │
│                      │  │ pytest   │ │ Playwright │   │   │
│                      │  │ requests │ │ Chromium   │   │   │
│                      │  └──────────┘ └───────────┘   │   │
│                      │  docker exec ──► plane-db      │   │
│                      │  docker.sock (mounted)          │   │
│                      └──────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Plane Services                                    │   │
│  │ plane-app-plane-db-1  plane-app-api-1  ...       │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## 2. Runner Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Java | OpenJDK 17.0.18 Temurin | Jenkins agent runtime |
| Git | 2.x+ | Source checkout |
| Python 3 | 3.x (venv) | API + DB tests |
| pytest | 9.1.1 | Test runner |
| requests | 2.34.2 | HTTP client |
| Node.js | 22.x | Playwright runtime |
| @playwright/test | 1.55.0 | UI tests |
| Chromium | headless-shell 149.x | Browser |
| Docker CLI | 27.3.1 | `docker exec` to Plane DB |
| curl, rsync, bash | Latest | Utilities |

## 3. WebSocket Connection

- Jenkins inbound agent connects via WebSocket to `$JENKINS_URL`
- `JENKINS_WEB_SOCKET=true` enables WebSocket mode
- No SSH or JNLP port required
- Agent Secret passed via `$JENKINS_AGENT_SECRET` at runtime (never in image)

## 4. Docker Socket Usage

**Why:** The QA Runner needs to execute `docker exec plane-app-plane-db-1 psql ...` for database assertion tests.

**How:** `/var/run/docker.sock` mounted read-write into the container.

**Security assessment:**

| Risk | Severity | Mitigation |
|------|----------|------------|
| Agent can start/stop containers | Medium | Only trusted local agent; no internet exposure |
| Agent accesses all host containers | Medium | Non-root user inside agent; docker group |
| Socket escape to host | Low | No `privileged:true`; no `--pid=host` |

**Constraints:**
- Agent runs as `jenkins` user (non-root)
- Docker socket access via `group_add: ${DOCKER_GID}`
- Only for local trusted pipeline execution
- No internet-facing Jenkins

## 5. Resources

| Resource | Limit | Rationale |
|----------|-------|-----------|
| CPU | 1.5 cores | Avoid starving Plane services |
| Memory | 2.5 GB | Enough for Chromium + Python |
| Playwright workers | 1 | Single-worker serial execution |

## 6. Security Design

1. **No credentials in image:** .env never copied; API keys passed via Jenkins credentials
2. **Non-root user:** Container runs as `jenkins` (uid 1000)
3. **No privileged mode:** Dropped explicitly
4. **Read-only source:** Project mounted `:ro` at `/opt/plane-source`
5. **Temporary .env:** Created at build start, deleted in post always
6. **Docker socket:** The primary risk — mitigated by local-only, trusted execution

## 7. Rollback

If the QA Runner causes issues:
1. Stop container: `docker stop plane-qa-runner-agent`
2. Rebuild from Dockerfile (immutable source)
3. Previous runner image tagged as `plane-qa-runner:day4` preserved
4. No Jenkins controller modifications needed
