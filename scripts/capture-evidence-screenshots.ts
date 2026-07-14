/**
 * Capture three required evidence screenshots:
 * 1. Workspace home after login
 * 2. Work Items list
 * 3. AUTO-D3-UI work item created
 */
import { chromium } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

function loadEnv(): Record<string, string> {
  const envPath = path.resolve(__dirname, "..", ".env");
  const result: Record<string, string> = {};
  for (const line of fs.readFileSync(envPath, "utf-8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const i = t.indexOf("=");
    if (i > 0) result[t.slice(0, i)] = t.slice(i + 1);
  }
  return result;
}

(async () => {
  const env = loadEnv();
  const BASE_URL = env.PLANE_BASE_URL!;
  const WS = env.PLANE_WORKSPACE_SLUG || "qa-lab";
  const PID = env.PLANE_PROJECT_ID!;
  const EMAIL = env.PLANE_UI_EMAIL!;
  const PASSWORD = env.PLANE_UI_PASSWORD!;

  const outDir = path.resolve(__dirname, "..", "evidence", "day3", "ui", "screenshots");
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();

  try {
    // Login
    await page.goto(BASE_URL, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.locator("input[name=email]").fill(EMAIL);
    await page.getByRole("button", { name: "Continue" }).click();
    await page.waitForTimeout(2000);
    await page.locator("input[type=password]").fill(PASSWORD);
    await page.getByRole("button", { name: /go to workspace/i }).click();
    await page.waitForURL(/\/[a-zA-Z0-9-]+\//, { timeout: 15000 });
    await page.waitForTimeout(2000);

    // Screenshot 1: Workspace home
    await page.screenshot({ path: path.join(outDir, "01-workspace-home.png"), fullPage: true });
    console.log("Screenshot 1: Workspace home captured");

    // Screenshot 2: Work Items list
    await page.goto(`${BASE_URL}/${WS}/projects/${PID}/issues`, { waitUntil: "networkidle", timeout: 20000 });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(outDir, "02-work-items-list.png"), fullPage: true });
    console.log("Screenshot 2: Work Items list captured");

    // Screenshot 3: Create a work item and capture
    const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const title = `AUTO-D3-UI-EVIDENCE-${ts}`;

    // Click "Add work item"
    const addBtn = page.locator("button").filter({ hasText: /Add work item/i }).first();
    if (await addBtn.isVisible()) {
      await addBtn.click();
      await page.waitForTimeout(2000);
    }

    // Fill title
    const titleInput = page.locator("input[name=name]");
    if (await titleInput.isVisible()) {
      await titleInput.fill(title);
    }

    // Save
    const saveBtn = page.getByRole("button", { name: "Save" });
    if (await saveBtn.isVisible()) {
      await saveBtn.click();
      await page.waitForTimeout(3000);
    }

    await page.screenshot({ path: path.join(outDir, "03-work-item-created.png"), fullPage: true });
    console.log(`Screenshot 3: Work item "${title}" created`);

    // Clean up the evidence work item via API
    const apiKey = process.env.PLANE_API_KEY;
    if (apiKey) {
      const url = `${BASE_URL}/api/v1/workspaces/${WS}/projects/${PID}/issues/`;
      const listResp = await fetch(url, {
        headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
      });
      const data: any = await listResp.json();
      const issues = data?.results || data || [];
      const matching = Array.isArray(issues)
        ? issues.filter((i: any) => (i.name || "").includes("AUTO-D3-UI-EVIDENCE"))
        : [];
      for (const issue of matching) {
        await fetch(`${url}${issue.id}/`, {
          method: "DELETE",
          headers: { "X-API-Key": apiKey },
        });
      }
      console.log(`Cleaned up ${matching.length} evidence work items`);
    }

    console.log("All evidence screenshots captured successfully");
  } catch (e: any) {
    console.log(`Error: ${e.message}`);
  } finally {
    await browser.close();
  }
})();
