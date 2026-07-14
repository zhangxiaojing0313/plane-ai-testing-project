/**
 * Workspace UI Tests (authenticated — uses storageState)
 * UI-002b: Verify workspace loads from stored auth state
 */
import { test, expect } from "@playwright/test";
import { WorkspacePage } from "../../pages/workspace.page";

const WORKSPACE_SLUG = process.env.PLANE_WORKSPACE_SLUG || "qa-lab";

test.describe("Workspace (authenticated)", () => {
  test("UI-002b: Workspace loads QA Lab heading and Plane QA Project from storage state", async ({ page }) => {
    const workspacePage = new WorkspacePage(page);
    await workspacePage.goto(WORKSPACE_SLUG);
    await expect(workspacePage.workspaceHeading).toBeVisible({ timeout: 10000 });
    await expect(workspacePage.planeQaProjectLink.first()).toBeVisible();
  });
});
