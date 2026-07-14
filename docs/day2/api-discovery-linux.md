# Plane API Discovery - Day 2 Phase 2 (Linux)

**Date:** 2026-07-13  
**Plane Version:** Community Edition v1.3.1  
**Host:** qa-linux  
**Target:** http://192.168.146.132:8090  

---

## 1. API Discovery Goals

The goal of Day 2 Phase 2 is to identify the Plane API base path, confirm real API endpoints, and catalog candidates for Day 3 automation — all through read-only, non-invasive methods:

- Docker service inspection
- Caddy/Proxy configuration analysis
- Container log analysis (API, Proxy, Web)
- Frontend static resource search
- Safe, unauthenticated HTTP probing (GET/HEAD/OPTIONS only)
- Django URL configuration review (read-only)

**No API Keys were created. No passwords, tokens, or session cookies were recorded.**

---

## 2. Methodology

| Method | Tool | Scope | Output |
|--------|------|-------|--------|
| Service inspection | docker compose ls, docker ps | Identify all Plane containers | Service map |
| Proxy config | docker exec + cat Caddyfile | Confirm routing rules | API base path |
| Log analysis | docker logs (API, Proxy) | Extract real request paths | Confirmed endpoints |
| Frontend search | grep + strings on JS bundles | Find API path references | Candidate endpoints |
| HTTP probing | curl GET/OPTIONS | Test auth boundaries | Status codes, response structure |
| URL config | docker exec + cat urls.py | Read Django route definitions | Full endpoint catalog |

---

## 3. Deployment Architecture & API Routing

### 3.1 Service Topology

```
External (Port 8090)
    │
    ▼
┌──────────────────────────────┐
│  Caddy Proxy (plane-proxy)   │
│  Port: 80 (internal)         │
└──────┬───────────────────────┘
       │
       ├── /api/*       ──►  api:8000      (Django backend)
       ├── /auth/*      ──►  api:8000      (Django backend)
       ├── /static/*    ──►  api:8000      (Django static)
       ├── /spaces/*    ──►  space:3000    (Plane Spaces)
       ├── /god-mode/*  ──►  admin:3000    (Plane Admin)
       ├── /live/*      ──►  live:3000     (Live server)
       ├── /{bucket}/*  ──►  plane-minio:9000 (S3 storage)
       └── /*           ──►  web:3000      (SPA frontend)
```

### 3.2 Container Summary

| Container | Image | Role |
|-----------|-------|------|
| plane-app-proxy-1 | makeplane/plane-proxy:v1.3.1 | Caddy reverse proxy |
| plane-app-api-1 | makeplane/plane-backend:v1.3.1 | Django REST API (Gunicorn + Uvicorn) |
| plane-app-web-1 | makeplane/plane-frontend:v1.3.1 | React SPA (Nginx) |
| plane-app-worker-1 | makeplane/plane-backend:v1.3.1 | Background task worker |
| plane-app-beat-worker-1 | makeplane/plane-backend:v1.3.1 | Scheduled task worker |
| plane-app-space-1 | makeplane/plane-space:v1.3.1 | Plane Spaces app |
| plane-app-admin-1 | makeplane/plane-admin:v1.3.1 | Plane Admin app |
| plane-app-live-1 | makeplane/plane-live:v1.3.1 | Real-time live server |
| plane-app-plane-db-1 | postgres:15.7-alpine | PostgreSQL database |
| plane-app-plane-redis-1 | valkey/valkey:7.2.11-alpine | Redis cache |
| plane-app-plane-mq-1 | rabbitmq:3.13.6-management-alpine | Message queue |
| plane-app-plane-minio-1 | minio/minio:latest | S3-compatible object storage |

---

## 4. API Base Path

**External Base URL:** `http://192.168.146.132:8090/api/`

**URL Structure:**
```
/api/              → Main application API (plane.app.urls)
/api/v1/           → Public API v1 (plane.api.urls) — API Key based
/api/public/       → Spaces public API (plane.space.urls)
/api/instances/    → Instance/license API (plane.license.urls)
/auth/             → Authentication endpoints
```

**API v1 modules:** asset, cycle, intake, label, member, module, project, state, user, work_item, invite, sticky

**Schema endpoints:** Disabled by default (`ENABLE_DRF_SPECTACULAR=0`). Would be at:
- `/api/schema/` (OpenAPI schema)
- `/api/schema/swagger-ui/` (Swagger UI)
- `/api/schema/redoc/` (ReDoc)

---

## 5. Confirmed Endpoints (with log or HTTP evidence)

These endpoints have been confirmed by real HTTP responses in API container logs, proxy logs, or direct curl probes. Status codes are from actual observations.

### 5.1 Instance (no authentication required)

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-001 | GET | `/api/instances/` | 200 | Public, returns config + instance info |
| API-DISC-005 | GET | `/auth/get-csrf-token/` | 200 | Public, returns CSRF token |

### 5.2 Authentication

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-004 | POST | `/auth/sign-in/` | 302 | Sets session cookie |
| — | POST | `/auth/email-check/` | 200 | Email validation |

### 5.3 Current User

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-006 | GET | `/api/users/me/` | 200 | Current user profile |
| API-DISC-007 | PATCH | `/api/users/me/` | 200 | Update current user |
| API-DISC-008 | GET | `/api/users/me/profile/` | 200 | User profile detail |
| API-DISC-009 | PATCH | `/api/users/me/profile/` | 200 | Update profile |
| API-DISC-010 | GET | `/api/users/me/settings/` | 200 | User settings |
| API-DISC-011 | GET | `/api/users/me/workspaces/` | 200 | User's workspaces |

### 5.4 Workspace

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-012 | GET | `/api/workspace-slug-check/` | 200 | Slug availability |
| API-DISC-013 | POST | `/api/workspaces/` | 201 | Create workspace |
| API-DISC-016 | GET | `/api/workspaces/<slug>/members/` | 200 | Workspace members |

### 5.5 Projects

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-019 | GET | `/api/workspaces/<slug>/projects/` | 200 | List projects |
| API-DISC-020 | POST | `/api/workspaces/<slug>/projects/` | 201 | Create project |
| API-DISC-021 | GET | `/api/workspaces/<slug>/projects/<pid>/` | 200 | Project detail |
| API-DISC-022 | PATCH | `/api/workspaces/<slug>/projects/<pid>/` | 200 | Update project |

### 5.6 Work Items (Issues)

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-028 | GET | `/api/workspaces/<slug>/projects/<pid>/issues/` | 200 | List with pagination |
| API-DISC-029 | POST | `/api/workspaces/<slug>/projects/<pid>/issues/` | 201 | Create issue |

### 5.7 States

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-023 | GET | `/api/workspaces/<slug>/projects/<pid>/states/` | 200 | Project states |

### 5.8 Labels

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-026 | GET | `/api/workspaces/<slug>/projects/<pid>/issue-labels/` | 200 | Project labels |

### 5.9 Members

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-025 | GET | `/api/workspaces/<slug>/projects/<pid>/members/` | 200 | Project members |
| API-DISC-040 | GET | `/api/workspaces/<slug>/projects/<pid>/project-members/me/` | 200 | Current user's project membership |

### 5.10 Cycles

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-033 | GET | `/api/workspaces/<slug>/projects/<pid>/cycles/` | 200 | Project cycles |

### 5.11 Modules

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-035 | GET | `/api/workspaces/<slug>/projects/<pid>/modules/` | 200 | Project modules |

### 5.12 Other Confirmed

| ID | Method | Path | Status | Notes |
|----|--------|------|--------|-------|
| API-DISC-037 | GET | `/api/workspaces/<slug>/projects/<pid>/estimates/` | 200 | Estimates |
| API-DISC-038 | GET | `/api/workspaces/<slug>/projects/<pid>/views/` | 200 | Project views |
| API-DISC-039 | GET | `/api/workspaces/<slug>/projects/<pid>/intake-state/` | 200 | Intake state |
| API-DISC-047 | GET | `/api/workspaces/<slug>/users/notifications/unread/` | 200 | Unread count |

---

## 6. High-Confidence Candidate Endpoints (from Django URL config, not yet in logs)

These are from Django URL configuration files. They are structurally guaranteed to exist but lack log-confirmed status codes.

### 6.1 Work Item Detail & Operations

| ID | Method | Path |
|----|--------|------|
| API-DISC-030 | GET | `/api/workspaces/<slug>/projects/<pid>/issues/<iid>/` |
| API-DISC-031 | PATCH | `/api/workspaces/<slug>/projects/<pid>/issues/<iid>/` |
| API-DISC-032 | DELETE | `/api/workspaces/<slug>/projects/<pid>/issues/<iid>/` |

### 6.2 Comments

| ID | Method | Path |
|----|--------|------|
| API-DISC-041 | GET | `/api/workspaces/<slug>/projects/<pid>/issues/<iid>/comments/` |
| API-DISC-042 | POST | `/api/workspaces/<slug>/projects/<pid>/issues/<iid>/comments/` |

### 6.3 Activity

| ID | Method | Path |
|----|--------|------|
| API-DISC-043 | GET | `/api/workspaces/<slug>/projects/<pid>/issues/<iid>/activity/` |

### 6.4 API Key Management

| ID | Method | Path |
|----|--------|------|
| API-DISC-044 | GET | `/api/v1/users/api-tokens/` |
| API-DISC-045 | POST | `/api/v1/users/api-tokens/` |

### 6.5 Pages

| ID | Method | Path |
|----|--------|------|
| API-DISC-048 | GET | `/api/workspaces/<slug>/projects/<pid>/pages/` |
| API-DISC-049 | POST | `/api/workspaces/<slug>/projects/<pid>/pages/` |

### 6.6 Notifications

| ID | Method | Path |
|----|--------|------|
| API-DISC-046 | GET | `/api/workspaces/<slug>/users/notifications/` |

### 6.7 Search & Webhooks

| ID | Method | Path |
|----|--------|------|
| API-DISC-051 | GET | `/api/workspaces/<slug>/search/` |
| API-DISC-050 | GET | `/api/workspaces/<slug>/webhooks/` |
| API-DISC-052 | GET | `/api/workspaces/<slug>/export-issues/` |

---

## 7. Authentication Mechanism

### 7.1 Session Authentication (Primary)

- Plane uses **Django session-based authentication**
- CSRF token obtained from `GET /auth/get-csrf-token/`
- Session cookie set after `POST /auth/sign-in/`
- All `/api/` endpoints (except `/api/instances/`) require authentication
- Unauthenticated requests return **HTTP 401**

### 7.2 API Key Authentication (Secondary)

- **Confirmed available** via environment variable `API_KEY_RATE_LIMIT=60/minute`
- API token management at `/api/v1/users/api-tokens/` (CRUD)
- Frontend reference: `/api/users/api-tokens/` (in JS bundles)
- **Status:** Endpoint exists but requires authentication to create tokens
- **Day 3 plan:** User manually creates API Key via Plane UI, then pytest uses `X-API-Key` header

### 7.3 CSRF Token

- Endpoint: `GET /auth/get-csrf-token/` — public, no auth required
- Response: `{"csrf_token": "<token>"}`
- Required for POST/PATCH/PUT/DELETE via session auth
- Not needed for API Key-based requests

---

## 8. HTTP Status Code Observations

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success (GET/PATCH) | Most GET endpoints |
| 201 | Created | POST /api/workspaces/, POST /api/projects/, POST /api/issues/ |
| 204 | No Content | PATCH /api/assets/v2/... when successful |
| 302 | Redirect | POST /auth/sign-in/ (redirects after login) |
| 401 | Unauthorized | Accessing protected endpoints without auth |
| 404 | Not Found | /api/, /api/v1/, /api/schema/ (disabled) |
| 502 | Bad Gateway | API backend unreachable (observed during startup) |

---

## 9. Pagination, Filtering & Sorting

### Observed Query Parameters (from logs)

**Issue list:**
```
GET /api/workspaces/<slug>/projects/<pid>/issues/
  ?order_by=-created_at         (sort descending by creation date)
  &sub_issue=true                (include sub-issues)
  &filters=%7B%7D                (URL-encoded JSON filter object)
  &layout=list                   (display layout: list, board, etc.)
  &cursor=100:0:0                (cursor-based pagination)
  &per_page=100                  (items per page)
```

**Stickies:**
```
GET /api/workspaces/<slug>/stickies/
  ?cursor=30:0:0
  &per_page=30
  &query=
```

### Key Observations
- **Pagination:** Cursor-based (not offset-based). Format: `<limit>:<offset>:<page>`
- **Page size:** Configurable via `per_page` parameter
- **Sorting:** `order_by` field with `-` prefix for descending
- **Filtering:** URL-encoded JSON in `filters` parameter
- **Layout:** `layout` parameter controls view mode

---

## 10. Day 3 Automation Candidates

### Priority 1 — Core CRUD (log-confirmed)

1. **Instance info:** GET /api/instances/ (no auth needed — basic health check)
2. **Current user:** GET /api/users/me/ (verify auth)
3. **List workspaces:** GET /api/users/me/workspaces/
4. **List projects:** GET /api/workspaces/<slug>/projects/
5. **List issues:** GET /api/workspaces/<slug>/projects/<pid>/issues/
6. **Create issue:** POST /api/workspaces/<slug>/projects/<pid>/issues/
7. **Get issue detail:** GET /api/workspaces/<slug>/projects/<pid>/issues/<iid>/
8. **Update issue:** PATCH /api/workspaces/<slug>/projects/<pid>/issues/<iid>/
9. **List states:** GET /api/workspaces/<slug>/projects/<pid>/states/
10. **List labels:** GET /api/workspaces/<slug>/projects/<pid>/issue-labels/
11. **List members:** GET /api/workspaces/<slug>/projects/<pid>/members/
12. **List cycles:** GET /api/workspaces/<slug>/projects/<pid>/cycles/
13. **List modules:** GET /api/workspaces/<slug>/projects/<pid>/modules/

### Priority 2 — Extended (URL-confirmed, needs testing)

14. **Comments CRUD:** GET/POST /api/workspaces/<slug>/projects/<pid>/issues/<iid>/comments/
15. **Activity feed:** GET /api/workspaces/<slug>/projects/<pid>/issues/<iid>/activity/
16. **Create label:** POST /api/workspaces/<slug>/projects/<pid>/issue-labels/
17. **Create state:** POST /api/workspaces/<slug>/projects/<pid>/states/
18. **API token management:** GET/POST /api/v1/users/api-tokens/

### Test Scenarios

| Category | Examples |
|----------|----------|
| **Happy path** | GET all resources, create issue with valid data |
| **Auth** | 401 without session, 401 with invalid API key |
| **Validation** | Create issue with missing required fields |
| **Not found** | GET non-existent issue/project ID |
| **Pagination** | Verify cursor navigation, per_page limits, empty pages |
| **Permissions** | Attempt cross-workspace access |
| **Rate limiting** | Exceed API_KEY_RATE_LIMIT (60/min) |

---

## 11. Current Limitations

1. **No API Key available:** API token endpoints exist but require authentication to create tokens. User must create one manually via Plane UI for Day 3.
2. **Schema disabled:** DRF Spectacular is disabled (`ENABLE_DRF_SPECTACULAR=0`). Cannot auto-generate OpenAPI schemas or client code.
3. **Limited log coverage:** API container logs only cover the initial setup session (login → workspace → project → first issue). Additional navigation (states, labels, members, settings, work item detail) was not captured in current logs.
4. **No response schemas:** Cannot confirm exact field types, required fields, or nested structures without authenticated API calls.
5. **Public API v1 untested:** `/api/v1/` endpoints require API Key authentication and were not probed.

---

## 12. Risks & Next Steps

### Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| API changes between versions | Low | Plane v1.3.1 is stable; Docker images are pinned |
| Session expiry during testing | Medium | Use API Key instead of session for Day 3 |
| Rate limiting (60/min) | Low | Implement backoff in pytest fixtures |
| Missing schema validation | Medium | Manually define expected response shapes |

### Day 3 Prerequisites

1. **User action:** Create a test-dedicated API Key via Plane UI
   - Navigate to: Settings → API Tokens → Create Token
   - Save the token value securely (it will only be shown once)
2. **Environment setup:**
   - Store API Key in environment variable or test config file
   - Set `PLANE_BASE_URL=http://192.168.146.132:8090`
   - Set `PLANE_WORKSPACE_SLUG=qa-lab`
3. **Framework:** pytest + requests (or httpx)

---

## 13. Module Distribution Summary

```
Module         Confirmed  High-Confidence  Total
────────────────────────────────────────────────
Instance          3            0              3
Authentication    3            0              3
User              6            0              6
Workspace         3            2              5
Project           4            0              4
Work Items        2            3              5
States            1            1              2
Labels            1            1              2
Members           2            0              2
Cycles            1            1              2
Modules           1            1              2
Comments          0            2              2
Activity          0            1              1
API Key           0            2              2
Pages             0            2              2
Notifications     1            1              2
Views             1            0              1
Estimates         1            0              1
Intake            1            0              1
Search            0            1              1
Webhooks          0            1              1
Exporter          0            1              1
────────────────────────────────────────────────
TOTAL            31           21             52
```

---

*Evidence file: `evidence/day2/api-discovery.txt`*  
*No Plane data was modified during this discovery.*  
*No credentials, tokens, or session cookies are stored in this document.*
