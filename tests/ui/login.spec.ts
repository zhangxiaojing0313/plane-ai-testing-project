/**
 * Login UI Tests (standalone — no storageState dependency)
 * UI-001: Login with valid credentials and enter QA Lab
 * UI-002: Verify Workspace home shows QA Lab and Plane QA Project
 */
import { test, expect } from "@playwright/test";
import { LoginPage } from "../../pages/login.page";
import { WorkspacePage } from "../../pages/workspace.page";

test.describe("Login Flow", () => {
  test("UI-001: Login with valid credentials and enter QA Lab", async ({ page }) => {
    const email = process.env.PLANE_UI_EMAIL;
    const password = process.env.PLANE_UI_PASSWORD;
    test.skip(!email || !password, "Credentials not configured");

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(email!, password!);

    const workspacePage = new WorkspacePage(page);
    await expect(workspacePage.workspaceHeading).toBeVisible({ timeout: 15000 });
  });

  test("UI-002: Verify Workspace home shows QA Lab and Plane QA Project", async ({ page }) => {
    const email = process.env.PLANE_UI_EMAIL;
    const password = process.env.PLANE_UI_PASSWORD;
    test.skip(!email || !password, "Credentials not configured");

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(email!, password!);

    const workspacePage = new WorkspacePage(page);
    await expect(workspacePage.workspaceHeading).toBeVisible();
    await expect(workspacePage.planeQaProjectLink.first()).toBeVisible();
  });
});
