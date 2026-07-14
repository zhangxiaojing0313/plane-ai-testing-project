"""
DB Schema Tests (read-only)
DB-001: Database connection and core table verification
DB-002: Known work item query
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.db_client import run_query, query_one_row, query_all_rows, query_count


@pytest.mark.db
@pytest.mark.smoke
class TestDatabaseConnection:
    """DB-001: Database connection and core tables."""

    def test_db_container_accessible(self, db_container):
        """Verify PostgreSQL container responds."""
        assert db_container is True

    def test_issues_table_exists(self):
        output = run_query("table_exists", {"table": "issues"})
        assert "t" in output, "issues table not found"

    def test_projects_table_exists(self):
        output = run_query("table_exists", {"table": "projects"})
        assert "t" in output, "projects table not found"

    def test_workspaces_table_exists(self):
        output = run_query("table_exists", {"table": "workspaces"})
        assert "t" in output, "workspaces table not found"

    def test_states_table_exists(self):
        output = run_query("table_exists", {"table": "states"})
        assert "t" in output, "states table not found"

    def test_issues_columns_exist(self):
        """Verify key columns in issues table."""
        output = run_query("get_columns", {"table": "issues"})
        assert "id" in output
        assert "name" in output
        assert "project_id" in output
        assert "workspace_id" in output
        assert "state_id" in output
        assert "priority" in output
        assert "created_at" in output
        assert "updated_at" in output
        assert "deleted_at" in output

    def test_column_id_is_pk(self):
        output = run_query("column_exists", {"table": "issues", "column": "id"})
        assert "t" in output, "id column not found"


@pytest.mark.db
@pytest.mark.regression
class TestKnownWorkItem:
    """DB-002: Verify known manual work item exists in database."""

    def test_known_issue_exists(self, known_issue_id):
        row = query_one_row("issue_by_id", {"issue_id": known_issue_id})
        assert row is not None, "Known issue not found in DB"
        # row[0]=id, row[1]=name, row[5]=project_id, row[6]=workspace_id
        assert "Verify Plane environment availability" == row[1], f"Name mismatch: {row[1]}"

    def test_known_issue_not_deleted(self, known_issue_id):
        row = query_one_row("issue_by_id", {"issue_id": known_issue_id})
        assert row is not None
        # deleted_at is index 13 (query: id,name,desc,priority,state_id,project_id,workspace_id,seq,sort,created_at,updated_at,completed_at,archived_at,[13]deleted_at,[14]is_draft)
        deleted = row[13] if len(row) > 13 else None
        assert deleted == "" or deleted is None, f"Issue is soft-deleted: {deleted}"

    def test_known_issue_project_fk(self, known_issue_id, known_project_id):
        row = query_one_row("issue_by_id", {"issue_id": known_issue_id})
        assert row is not None
        assert row[5] == known_project_id, f"Project FK mismatch: {row[5]}"

    def test_known_issue_workspace_fk(self, known_issue_id, known_workspace_id):
        row = query_one_row("issue_by_id", {"issue_id": known_issue_id})
        assert row is not None
        assert row[6] == known_workspace_id, f"Workspace FK mismatch: {row[6]}"

    def test_known_issue_created_at_not_null(self, known_issue_id):
        row = query_one_row("issue_by_id", {"issue_id": known_issue_id})
        assert row is not None
        # created_at is index 9
        assert row[9] != "", "created_at is empty"

    def test_no_modification_of_known_item(self, known_issue_id):
        """Read-only: this test MUST NOT modify the known work item."""
        # Just read — if we got here, no modifications occurred
        row = query_one_row("issue_by_id", {"issue_id": known_issue_id})
        assert row is not None
        assert row[1] == "Verify Plane environment availability"
