/**
 * Project UI Tests
 * UI-003: Enter Plane QA Project Work Items page and verify existing items visible
 */
import { test, expect } from "@playwright/test";
import { ProjectPage } from "../../pages/project.page";

const WORKSPACE_SLUG = process.env.PLANE_WORKSPACE_SLUG || "qa-lab";
const PROJECT_ID = process.env.PLANE_PROJECT_ID || "0c1cf73f-2d88-430b-812b-2e1c7f010c3c";

test.describe("Project", () => {
  test.use({ storageState: ".playwright/auth-state.json" });

  test("UI-003: Enter Plane QA Project Work Items and verify existing items visible", async ({ page }) => {
    const projectPage = new ProjectPage(page, WORKSPACE_SLUG, PROJECT_ID);
    await projectPage.goto();

    // Verify we're on the issues page
    await expect(page).toHaveURL(/\/issues/);

    // Verify the existing "Verify Plane environment availability" is present
    // Use broader patterns since item IDs may vary in rendering
    const verifyLink = page.getByText(/Verify Plane environment availability/i);
    await expect(verifyLink.first()).toBeVisible({ timeout: 15000 });

    // Verify at least one work item link exists
    const anyItemLink = page.locator("a").filter({ hasText: /Verify|PLANE/i }).first();
    await expect(anyItemLink).toBeVisible({ timeout: 5000 });
  });
});
