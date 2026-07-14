# Plane PostgreSQL Database Schema — Day 4 Discovery

**Date:** 2026-07-13
**Host:** qa-linux
**Discovered from:** Real container inspection (read-only)

---

## 1. Database Version

| Item | Value |
|------|-------|
| Container | `plane-app-plane-db-1` |
| Image | `postgres:15.7-alpine` |
| Version | PostgreSQL 15.7 on x86_64-pc-linux-musl |
| Database | `plane` |
| User | `plane` |
| Auth | Via container-internal `$POSTGRES_PASSWORD` (never printed) |

---

## 2. Core Tables

### 2.1 issues (Work Items)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | Primary Key |
| `name` | varchar | NO | Work item title |
| `description_json` | jsonb | NO | Rich description (ProseMirror JSON) |
| `description_html` | text | NO | Rendered HTML |
| `description_stripped` | text | YES | Plain text extract |
| `priority` | varchar | NO | `urgent`, `high`, `medium`, `low`, `none` |
| `sequence_id` | integer | NO | Display number (e.g., PLANEQAPRO-1) |
| `sort_order` | float | NO | List ordering |
| `state_id` | uuid | YES | FK → states.id |
| `project_id` | uuid | NO | FK → projects.id |
| `workspace_id` | uuid | NO | FK → workspaces.id |
| `parent_id` | uuid | YES | FK → issues.id (sub-issue) |
| `created_by_id` | uuid | YES | FK → users.id |
| `updated_by_id` | uuid | YES | FK → users.id |
| `estimate_point_id` | uuid | YES | FK → estimate_points.id |
| `type_id` | uuid | YES | FK → issue_types.id |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |
| `completed_at` | timestamptz | YES | |
| `archived_at` | date | YES | |
| `deleted_at` | timestamptz | YES | **Soft delete** |
| `is_draft` | boolean | NO | |
| `start_date` | date | YES | |
| `target_date` | date | YES | |
| `point` | integer | YES | Story points |
| `external_id` | varchar | YES | Import source ID |
| `external_source` | varchar | YES | Import source |

### 2.2 projects

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | Primary Key |
| `name` | varchar | NO | |
| `identifier` | varchar | NO | Unique per workspace+deleted_at |
| `description` | text | NO | |
| `workspace_id` | uuid | NO | FK → workspaces.id |
| `default_state_id` | uuid | YES | FK → states.id |
| `created_by_id` | uuid | YES | FK → users.id |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |
| `archived_at` | timestamptz | YES | |
| `deleted_at` | timestamptz | YES | **Soft delete** |

### 2.3 workspaces

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | Primary Key |
| `name` | varchar | NO | |
| `slug` | varchar | NO | UNIQUE |
| `owner_id` | uuid | NO | FK → users.id |
| `created_at` | timestamptz | NO | |
| `updated_at` | timestamptz | NO | |
| `deleted_at` | timestamptz | YES | **Soft delete** |

### 2.4 states

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | uuid | NO | Primary Key |
| `name` | varchar | NO | |
| `color` | varchar | NO | |
| `slug` | varchar | NO | |
| `group` | varchar | NO | `backlog`, `unstarted`, `started`, `completed`, `cancelled` |
| `sequence` | float | NO | |
| `default` | boolean | NO | |
| `is_triage` | boolean | NO | |
| `project_id` | uuid | NO | FK → projects.id |
| `workspace_id` | uuid | NO | FK → workspaces.id |
| `deleted_at` | timestamptz | YES | **Soft delete** |

### 2.5 workspace_members

| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid PK | |
| `member_id` | uuid FK→users | |
| `workspace_id` | uuid FK→workspaces | |
| `role` | smallint | |
| `is_active` | boolean | |
| `deleted_at` | timestamptz | Soft delete |

### 2.6 project_members

| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid PK | |
| `member_id` | uuid FK→users | |
| `project_id` | uuid FK→projects | |
| `workspace_id` | uuid FK→workspaces | |
| `role` | smallint | |
| `is_active` | boolean | |
| `deleted_at` | timestamptz | Soft delete |

---

## 3. Key Relationships

```
workspaces 1──N projects
workspaces 1──N issues
workspaces 1──N states
workspaces 1──N workspace_members

projects 1──N issues
projects 1──N states
projects 1──N project_members

states 1──N issues (via issues.state_id)

users 1──N workspace_members (via member_id)
users 1──N project_members (via member_id)
```

---

## 4. Delete Mechanism

**All core tables use soft delete** via `deleted_at timestamp with time zone`.

- `issues.deleted_at` — soft delete
- `projects.deleted_at` — soft delete
- `workspaces.deleted_at` — soft delete
- `states.deleted_at` — soft delete
- `workspace_members.deleted_at` — soft delete
- `project_members.deleted_at` — soft delete

When an issue is "deleted" via API (DELETE method, status 204), the record is NOT physically removed. Instead `deleted_at` is set to the deletion timestamp. The API filters out rows where `deleted_at IS NOT NULL`.

In addition, `issues.archived_at` provides a separate archival mechanism.

---

## 5. Work Item Key Fields (for DB Assertions)

| Assertion | Field(s) |
|-----------|----------|
| Title match | `issues.name` |
| Project FK | `issues.project_id` |
| Workspace FK | `issues.workspace_id` |
| State FK | `issues.state_id` |
| Priority | `issues.priority` |
| Exists (not deleted) | `issues.deleted_at IS NULL` |
| Created timestamp | `issues.created_at` |
| Updated timestamp | `issues.updated_at` |
| Sequence number | `issues.sequence_id` |

---

## 6. Executable Database Assertions

1. Table existence: `SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'issues')`
2. Column existence: `SELECT column_name FROM information_schema.columns WHERE table_name = 'issues'`
3. Work item by API ID: `SELECT name, project_id, workspace_id FROM issues WHERE id = $1 AND deleted_at IS NULL`
4. Created record exists: `SELECT COUNT(*) FROM issues WHERE id = $1`
5. Updated timestamp: `SELECT updated_at FROM issues WHERE id = $1`
6. Soft delete check: `SELECT deleted_at FROM issues WHERE id = $1`
7. Cleanup verification: `SELECT COUNT(*) FROM issues WHERE name LIKE 'AUTO-D4-DB-%' AND deleted_at IS NULL`

---

## 7. Sensitive Information Handling

- Database password is NEVER printed, logged, or stored in code
- All psql commands use container-internal `$POSTGRES_PASSWORD` via `PGPASSWORD`
- No connection strings in reports or logs
- UUID validation before any query to prevent injection
- Fixed query templates only — no user-supplied SQL
- No DROP, TRUNCATE, ALTER, CREATE DATABASE statements permitted
