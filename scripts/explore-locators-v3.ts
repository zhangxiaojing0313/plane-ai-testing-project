/**
 * Targeted exploration: drawer, new work item form, save button
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
  const EMAIL = env.PLANE_UI_EMAIL!;
  const PASSWORD = env.PLANE_UI_PASSWORD!;
  const WS = env.PLANE_WORKSPACE_SLUG || "qa-lab";
  const PID = env.PLANE_PROJECT_ID!;

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const log: string[] = [];
  const L = (s: string) => { log.push(s); console.log(s); };

  try {
    // Login
    L("=== LOGIN ===");
    await page.goto(BASE_URL, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.getByRole("textbox").fill(EMAIL);
    await page.getByRole("button", { name: "Continue" }).click();
    await page.waitForTimeout(2000);
    await page.getByPlaceholder(/password/i).fill(PASSWORD);
    await page.getByRole("button", { name: /go to workspace/i }).click();
    await page.waitForTimeout(3000);
    L(`Logged in: ${page.url()}`);

    // Go directly to issues page
    L("\n=== ISSUES PAGE ===");
    await page.goto(`${BASE_URL}/${WS}/projects/${PID}/issues`, { waitUntil: "networkidle", timeout: 15000 });
    await page.waitForTimeout(3000);
    L(`URL: ${page.url()}`);

    // Find the "Add work item" button
    L("\n--- Looking for Add Work Item button ---");
    for (const b of await page.locator("button").all()) {
      const txt = (await b.textContent())?.trim() || "";
      if (txt.toLowerCase().includes("add") || txt.toLowerCase().includes("new")) {
        L(`  BTN: "${txt}" visible=${await b.isVisible()}`);
      }
    }

    // Click "Add work item" button
    const addWorkItemBtn = page.locator("button").filter({ hasText: /Add work item/i }).first();
    L(`\nAdd work item button count: ${await addWorkItemBtn.count()}`);
    if (await addWorkItemBtn.isVisible()) {
      await addWorkItemBtn.click();
      await page.waitForTimeout(3000);
      L(`After clicking Add work item: ${page.url()}`);
    }

    // Look for the modal/dialog/form
    L("\n--- Looking for form/modal ---");
    const dialog = page.locator("[role=dialog], [class*=modal], [class*=drawer], [class*=form], [class*=sheet]");
    L(`Dialog/modal/drawer count: ${await dialog.count()}`);

    // All inputs in the form
    L("\n--- All input fields ---");
    for (const inp of await page.locator("input, textarea, [contenteditable=true]").all()) {
      const ph = await inp.getAttribute("placeholder") || "";
      const tp = await inp.getAttribute("type") || "";
      const nm = await inp.getAttribute("name") || "";
      const role = await inp.getAttribute("role") || "";
      const vis = await inp.isVisible();
      L(`  FIELD: type="${tp}" placeholder="${ph}" name="${nm}" role="${role}" visible=${vis}`);
    }

    // All buttons including in modal
    L("\n--- All buttons ---");
    for (const b of await page.locator("button").all()) {
      const txt = (await b.textContent())?.trim()?.slice(0, 80) || "";
      const aria = await b.getAttribute("aria-label") || "";
      const vis = await b.isVisible();
      if (vis && (txt || aria)) L(`  BTN: text="${txt}" aria="${aria}"`);
    }

    await page.screenshot({ path: path.join(__dirname, "..", "evidence/day3/ui/explore-v3-01-add-form.png"), fullPage: true });

    // Try filling title and saving
    L("\n=== TRY CREATING WORK ITEM ===");
    // Find title input
    const titleInput = page.getByPlaceholder(/title|name|issue/i).or(page.locator("[contenteditable=true]").first());
    L(`Title input count: ${await titleInput.count()}`);

    // Check if Save button is disabled when empty
    const saveBtn = page.getByRole("button", { name: /save|create|submit|add/i });
    L(`Save/Create button count: ${await saveBtn.count()}`);
    for (const b of await saveBtn.all()) {
      const disabled = await b.isDisabled();
      const txt = await b.textContent();
      L(`  Save btn: "${txt}" disabled=${disabled}`);
    }

    // Close the form (try Escape or Cancel)
    const cancelBtn = page.getByRole("button", { name: /cancel|close|discard/i });
    L(`Cancel/Close button count: ${await cancelBtn.count()}`);
    if (await cancelBtn.count() > 0) {
      await cancelBtn.first().click();
      await page.waitForTimeout(1000);
      L("Closed form");
    } else {
      await page.keyboard.press("Escape");
      await page.waitForTimeout(1000);
      L("Pressed Escape");
    }

    // ===== TEST: Click existing work item to open drawer =====
    L("\n=== OPEN WORK ITEM DRAWER ===");
    // Look for issue link
    const issueLink = page.locator("a").filter({ hasText: /Verify Plane/i }).first();
    L(`Issue link count: ${await issueLink.count()}`);
    if (await issueLink.isVisible()) {
      await issueLink.click();
      await page.waitForTimeout(3000);
      L(`After clicking issue: ${page.url()}`);
    }

    await page.screenshot({ path: path.join(__dirname, "..", "evidence/day3/ui/explore-v3-02-drawer.png"), fullPage: true });

    // Dump drawer content
    L("\n--- Drawer headings ---");
    for (const el of await page.getByRole("heading").all()) {
      const txt = (await el.textContent())?.trim() || "";
      if (await el.isVisible()) L(`  H: "${txt}"`);
    }

    L("\n--- Drawer buttons ---");
    for (const b of await page.locator("button").all()) {
      const txt = (await b.textContent())?.trim()?.slice(0, 60) || "";
      if (await b.isVisible() && txt) L(`  BTN: "${txt}"`);
    }

    // Look for description/priority fields
    L("\n--- Drawer inputs ---");
    for (const inp of await page.locator("input, textarea, [contenteditable=true]").all()) {
      const ph = await inp.getAttribute("placeholder") || "";
      const tp = await inp.getAttribute("type") || "";
      if (await inp.isVisible()) L(`  FIELD: type="${tp}" placeholder="${ph}"`);
    }

    // Try editing description
    L("\n=== TRY EDIT DESCRIPTION ===");
    // Look for description area
    const descBtn = page.locator("button").filter({ hasText: /description|add description/i }).first();
    L(`Description button count: ${await descBtn.count()}`);

    // Close drawer
    await page.keyboard.press("Escape");
    await page.waitForTimeout(1000);

    L("\n=== DONE ===");
  } catch (e: any) {
    L(`ERROR: ${e.message}\n${e.stack}`);
    await page.screenshot({ path: path.join(__dirname, "..", "evidence/day3/ui/explore-v3-error.png"), fullPage: true });
  } finally {
    fs.writeFileSync(path.join(__dirname, "..", "evidence/day3/ui/locator-exploration-v3.txt"), log.join("\n"), "utf-8");
    await browser.close();
  }
})();
