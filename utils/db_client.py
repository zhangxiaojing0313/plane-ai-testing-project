"""
Safe PostgreSQL client for Plane database assertions.

Connects via docker exec to the Plane PostgreSQL container.
Uses container-internal env vars — never stores or prints passwords.
Only allows predefined query templates. No user-supplied SQL.
"""

import subprocess
import re
import uuid
from typing import Optional, List, Dict, Any

# Fixed-safe query templates
_SAFE_QUERIES = {
    "table_exists": (
        "SELECT EXISTS ("
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:table"
        ")",
        ["table"],
    ),
    "column_exists": (
        "SELECT EXISTS ("
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=:table AND column_name=:column"
        ")",
        ["table", "column"],
    ),
    "get_columns": (
        "SELECT column_name, data_type, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=:table "
        "ORDER BY ordinal_position",
        ["table"],
    ),
    "issue_by_id": (
        "SELECT id, name, description_stripped, priority, state_id, "
        "project_id, workspace_id, sequence_id, sort_order, "
        "created_at, updated_at, completed_at, archived_at, deleted_at, is_draft "
        "FROM issues WHERE id=:issue_id",
        ["issue_id"],
    ),
    "issue_by_name_pattern": (
        "SELECT id, name, project_id, workspace_id, deleted_at "
        "FROM issues WHERE name LIKE :pattern",
        ["pattern"],
    ),
    "issue_count_by_name_pattern": (
        "SELECT COUNT(*) FROM issues "
        "WHERE name LIKE :pattern AND deleted_at IS NULL",
        ["pattern"],
    ),
    "issue_updated_at": (
        "SELECT updated_at FROM issues WHERE id=:issue_id",
        ["issue_id"],
    ),
    "issue_deleted_at": (
        "SELECT deleted_at FROM issues WHERE id=:issue_id",
        ["issue_id"],
    ),
    "project_by_id": (
        "SELECT id, name, identifier, workspace_id "
        "FROM projects WHERE id=:project_id AND deleted_at IS NULL",
        ["project_id"],
    ),
    "workspace_by_slug": (
        "SELECT id, name, slug FROM workspaces WHERE slug=:slug AND deleted_at IS NULL",
        ["slug"],
    ),
    "state_by_id": (
        "SELECT id, name, group_name, color FROM states WHERE id=:state_id AND deleted_at IS NULL",
        ["state_id"],
    ),
    "cleanup_auto_items": (
        "SELECT id, name FROM issues "
        "WHERE name LIKE :pattern AND deleted_at IS NULL",
        ["pattern"],
    ),
}

# Container identification
_CONTAINER = "plane-app-plane-db-1"

# UUID regex for validation
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _validate_uuid(value: str) -> str:
    """Raise ValueError if value is not a valid UUID."""
    if not _UUID_RE.match(value):
        raise ValueError(f"Invalid UUID: {value}")
    return value


def _validate_safe_string(value: str, max_length: int = 255) -> str:
    """Reject strings containing dangerous characters."""
    if not value:
        raise ValueError("Empty string not allowed")
    if len(value) > max_length:
        raise ValueError(f"String too long: {len(value)} > {max_length}")
    # Reject SQL metacharacters
    dangerous = [";", "'", '"', "\\", "--", "/*", "*/"]
    for d in dangerous:
        if d in value:
            raise ValueError(f"Dangerous character '{d}' in parameter")
    return value


def _validate_pattern(value: str) -> str:
    """Validate a LIKE pattern — allow only alphanumeric, underscore, dash, %, and AUTO-D4-DB- prefix."""
    # Allow only safe patterns
    if not value.startswith(("AUTO-D4-DB-", "Verify Plane", "%AUTO-D4-DB-%")):
        if "%" not in value:
            _validate_safe_string(value, 500)
    if len(value) > 500:
        raise ValueError(f"Pattern too long: {len(value)}")
    if any(c in value for c in [";", "'", '"', "\\", "--", "/*", "*/"]):
        raise ValueError("Dangerous characters in pattern")
    return value


def _container_exec(sql: str) -> str:
    """Execute SQL via docker exec psql. Returns stdout. Raises on error."""
    cmd = [
        "docker", "exec", _CONTAINER,
        "sh", "-c",
        f'PGPASSWORD="${{POSTGRES_PASSWORD}}" psql -U "${{POSTGRES_USER}}" -d "${{POSTGRES_DB}}" -At -F "|" -c "{sql}"'
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Strip any potential password leakage from error messages
        if "password" in stderr.lower():
            stderr = "Authentication error (details suppressed)"
        raise RuntimeError(f"psql error (suppressed): {stderr[:200]}")
    return result.stdout.strip()


def run_query(query_name: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Execute a predefined safe query.

    Args:
        query_name: Key in _SAFE_QUERIES
        params: Dict of parameter name → value

    Returns:
        Raw psql output (pipe-delimited rows)
    """
    if query_name not in _SAFE_QUERIES:
        raise ValueError(f"Unknown query: {query_name}")

    template, param_names = _SAFE_QUERIES[query_name]
    resolved_params = params or {}

    # Validate all required params present
    for pname in param_names:
        if pname not in resolved_params:
            raise ValueError(f"Missing required parameter: {pname}")

    # Build SQL with validated params
    sql = template
    for pname in resolved_params:
        value = resolved_params[pname]
        placeholder = f":{pname}"

        if pname.endswith("_id"):
            _validate_uuid(value)
            sql = sql.replace(placeholder, f"'{value}'")
        elif pname == "pattern":
            _validate_pattern(value)
            sql = sql.replace(placeholder, f"'{value}'")
        elif pname in ("table", "column", "slug"):
            _validate_safe_string(value, 100)
            sql = sql.replace(placeholder, f"'{value}'")
        else:
            _validate_safe_string(value)
            sql = sql.replace(placeholder, f"'{value}'")

    # Final safety check — reject dangerous statements
    _validate_final_sql(sql)

    return _container_exec(sql)


def _validate_final_sql(sql: str) -> None:
    """Reject any SQL containing dangerous standalone statements (not column names)."""
    dangerous = [
        "DROP ", "DROP\n", "TRUNCATE ", "TRUNCATE\n",
        "ALTER ", "ALTER\n", "CREATE DATABASE",
        "INSERT ", "INSERT\n", "UPDATE ", "UPDATE\n",
        "DELETE ", "DELETE\n", "GRANT ", "REVOKE ",
    ]
    sql_upper = sql.upper()
    for d in dangerous:
        if d in sql_upper:
            raise RuntimeError(f"Dangerous SQL detected: {d.strip()}")


def query_one_row(query_name: str, params: Optional[Dict[str, str]] = None) -> Optional[List[str]]:
    """Execute query and return first row as list of column values."""
    output = run_query(query_name, params)
    if not output:
        return None
    return output.split("|")


def query_all_rows(query_name: str, params: Optional[Dict[str, str]] = None) -> List[List[str]]:
    """Execute query and return all rows as list of column value lists."""
    output = run_query(query_name, params)
    if not output:
        return []
    rows = []
    for line in output.split("\n"):
        line = line.strip()
        if line:
            rows.append(line.split("|"))
    return rows


def query_count(query_name: str, params: Optional[Dict[str, str]] = None) -> int:
    """Execute a count query and return integer result."""
    output = run_query(query_name, params)
    try:
        return int(output.strip())
    except (ValueError, TypeError):
        return 0
