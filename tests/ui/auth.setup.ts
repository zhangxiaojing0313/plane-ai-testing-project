/**
 * Authentication Setup
 * Logs in once and saves storage state to .playwright/auth-state.json
 * for reuse by all dependent tests.
 */
import { test as setup } from "@playwright/test";
import { LoginPage } from "../../pages/login.page";
import * as path from "path";
import * as fs from "fs";

const AUTH_STATE = path.resolve(__dirname, "..", "..", ".playwright", "auth-state.json");

setup.describe("Authentication Setup", () => {
  setup("authenticate and save storage state", async ({ page }) => {
    const email = process.env.PLANE_UI_EMAIL;
    const password = process.env.PLANE_UI_PASSWORD;

    if (!email || !password) {
      throw new Error("PLANE_UI_EMAIL and PLANE_UI_PASSWORD must be set in environment");
    }

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(email, password);

    // Verify we landed on a workspace page
    await page.waitForURL(/\/[a-zA-Z0-9-]+\//, { timeout: 15000 });

    // Ensure the storage directory exists
    const dir = path.dirname(AUTH_STATE);
    fs.mkdirSync(dir, { recursive: true });

    await page.context().storageState({ path: AUTH_STATE });
  });
});
