/**
 * Plane UI Locator Exploration v2 — fixed login flow
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
  const BASE_URL = env.PLANE_BASE_URL || "http://192.168.146.132:8090";
  const EMAIL = env.PLANE_UI_EMAIL!;
  const PASSWORD = env.PLANE_UI_PASSWORD!;

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();

  const outDir = path.resolve(__dirname, "..", "evidence", "day3", "ui");
  fs.mkdirSync(outDir, { recursive: true });
  const log: string[] = [];
  const L = (s: string) => { log.push(s); console.log(s); };

  try {
    // ===== LOGIN: Email step =====
    L("=== STEP 1: Login Email ===");
    await page.goto(BASE_URL, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000);
    L(`URL: ${page.url()}`);

    await page.getByRole("textbox").fill(EMAIL);
    L("Filled email via getByRole('textbox')");

    await page.getByRole("button", { name: "Continue" }).click();
    L("Clicked Continue");
    await page.waitForTimeout(2000);
    L(`URL after continue: ${page.url()}`);

    // Dump visible buttons
    for (const b of await page.locator("button").all()) {
      const txt = (await b.textContent())?.trim() || "";
      if (await b.isVisible()) L(`  BTN: "${txt}"`);
    }

    // ===== LOGIN: Password step =====
    L("=== STEP 2: Login Password ===");
    await page.getByPlaceholder(/password/i).fill(PASSWORD);
    L("Filled password via getByPlaceholder(/password/i)");

    await page.getByRole("button", { name: /go to workspace/i }).click();
    L("Clicked 'Go to workspace'");
    await page.waitForTimeout(3000);
    L(`URL after login: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-v2-01-post-login.png"), fullPage: true });

    // Dump all visible text on page
    const bodyText = await page.locator("body").innerText();
    L(`Page text preview: ${bodyText.slice(0, 500)}`);

    // ===== WORKSPACE =====
    L("=== STEP 3: Workspace ===");
    // Look for headings and key elements
    for (const role of ["heading", "link", "button"] as const) {
      const els = await page.getByRole(role).all();
      for (const el of els) {
        try {
          const txt = (await el.textContent())?.trim().slice(0, 80) || "";
          if (await el.isVisible() && txt) L(`  ${role}: "${txt}"`);
        } catch {}
      }
    }

    // ===== NAVIGATE TO WORK ITEMS =====
    L("=== STEP 4: Navigate to Work Items ===");
    // Try sidebar navigation links
    const sidebarLinks = await page.locator("nav a, [class*=sidebar] a, [class*=nav] a").all();
    L(`Sidebar/nav links: ${sidebarLinks.length}`);
    for (const el of sidebarLinks) {
      try {
        const txt = (await el.textContent())?.trim() || "";
        const href = await el.getAttribute("href") || "";
        if (await el.isVisible() && txt) L(`  nav-link: "${txt}" -> ${href}`);
      } catch {}
    }

    // Try clicking things that might lead to project/work items
    const planeQaLink = page.getByText(/Plane QA/i).first();
    L(`getByText(/Plane QA/i): count=${await planeQaLink.count()}`);

    const workItemsLink = page.getByText(/work items|issues/i).first();
    L(`getByText(/work items|issues/i): count=${await workItemsLink.count()}`);

    // Try clicking Plane QA if visible
    if (await planeQaLink.isVisible()) {
      await planeQaLink.click();
      await page.waitForTimeout(2000);
      L(`URL after clicking Plane QA: ${page.url()}`);
    }

    await page.screenshot({ path: path.join(outDir, "explore-v2-02-workspace.png"), fullPage: true });

    // ===== DUMP FULL PAGE STRUCTURE =====
    L("=== STEP 5: Full page dump ===");
    // Get all text content organized by section
    const sections = await page.locator("[class*=section], [class*=container], [class*=card], [class*=pane], main, aside, nav, header").all();
    L(`Sections/containers: ${sections.length}`);
    for (const s of sections) {
      try {
        const txt = (await s.innerText())?.trim().slice(0, 100);
        if (txt && await s.isVisible()) L(`  section: "${txt}"`);
      } catch {}
    }

    // ===== TRY DIRECT URL NAVIGATION =====
    L("=== STEP 6: Direct URL navigation ===");
    const WS_SLUG = env.PLANE_WORKSPACE_SLUG || "qa-lab";
    const PROJ_ID = env.PLANE_PROJECT_ID;

    // Try workspace URL
    await page.goto(`${BASE_URL}/${WS_SLUG}`, { waitUntil: "networkidle", timeout: 15000 });
    await page.waitForTimeout(2000);
    L(`Direct workspace URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-v2-03-workspace-url.png"), fullPage: true });

    // Try project issues URL
    await page.goto(`${BASE_URL}/${WS_SLUG}/projects/${PROJ_ID}/issues`, { waitUntil: "networkidle", timeout: 15000 });
    await page.waitForTimeout(2000);
    L(`Direct issues URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-v2-04-issues-url.png"), fullPage: true });

    // Dump buttons and links on issues page
    L("--- Issues page buttons ---");
    for (const b of await page.locator("button").all()) {
      const txt = (await b.textContent())?.trim()?.slice(0, 60) || "";
      if (await b.isVisible() && txt) L(`  BTN: "${txt}"`);
    }

    L("--- Issues page inputs ---");
    for (const inp of await page.locator("input, textarea, [contenteditable=true]").all()) {
      const ph = await inp.getAttribute("placeholder") || "";
      const tp = await inp.getAttribute("type") || "";
      if (await inp.isVisible()) L(`  INPUT: type="${tp}" placeholder="${ph}"`);
    }

    L("--- Issues page links/headings ---");
    for (const role of ["heading", "link"] as const) {
      for (const el of await page.getByRole(role).all()) {
        try {
          const txt = (await el.textContent())?.trim()?.slice(0, 80) || "";
          if (await el.isVisible() && txt) L(`  ${role}: "${txt}"`);
        } catch {}
      }
    }

    // ===== OPEN FIRST WORK ITEM =====
    L("=== STEP 7: Open work item ===");
    // Look for issue rows or links
    const issueEls = page.locator("[class*=issue], [class*=Issue], [class*=row], [class*=item], tr[class]");
    L(`Issue-like elements: count=${await issueEls.count()}`);

    // Try clicking any link that has known issue text
    const knownIssues = ["Verify Plane", "AUTO-D3", "environment"];
    for (const t of knownIssues) {
      const link = page.getByText(t, { exact: false }).first();
      if ((await link.count()) > 0 && await link.isVisible()) {
        L(`Found link matching "${t}": "${await link.textContent()}"`);
        await link.click();
        await page.waitForTimeout(2000);
        L(`URL after click: ${page.url()}`);
        break;
      }
    }

    await page.screenshot({ path: path.join(outDir, "explore-v2-05-detail.png"), fullPage: true });

    // Detail page elements
    L("--- Detail page ---");
    for (const b of await page.locator("button").all()) {
      const txt = (await b.textContent())?.trim()?.slice(0, 60) || "";
      if (await b.isVisible() && txt) L(`  BTN: "${txt}"`);
    }

    // ===== NEW WORK ITEM FORM =====
    L("=== STEP 8: New work item form ===");
    await page.goBack();
    await page.waitForTimeout(1000);

    // Look for Add/New button
    const addBtns = page.getByRole("button", { name: /new|add|create/i });
    L(`Add/New/Create buttons: count=${await addBtns.count()}`);
    for (const b of await addBtns.all()) {
      L(`  "${await b.textContent()}"`);
    }

    // Also look for icon-only buttons
    const allButtons = await page.locator("button").all();
    for (const b of allButtons) {
      const txt = await b.textContent();
      const aria = await b.getAttribute("aria-label");
      const title = await b.getAttribute("title");
      if (await b.isVisible()) {
        L(`  ALL-BTN: text="${txt?.trim()}" aria="${aria}" title="${title}"`);
      }
    }

    // Try clicking add
    if (await addBtns.count() > 0) {
      await addBtns.first().click();
      await page.waitForTimeout(2000);
      L(`URL after add click: ${page.url()}`);
      await page.screenshot({ path: path.join(outDir, "explore-v2-06-new-form.png"), fullPage: true });

      L("--- Form fields ---");
      for (const inp of await page.locator("input, textarea, [contenteditable=true]").all()) {
        const ph = await inp.getAttribute("placeholder") || "";
        const tp = await inp.getAttribute("type") || "";
        const nm = await inp.getAttribute("name") || "";
        if (await inp.isVisible()) L(`  FIELD: type="${tp}" placeholder="${ph}" name="${nm}"`);
      }

      L("--- Form buttons ---");
      for (const b of await page.locator("button").all()) {
        const txt = (await b.textContent())?.trim()?.slice(0, 60) || "";
        if (await b.isVisible() && txt) L(`  BTN: "${txt}"`);
      }
    }

    L("=== DONE ===");
  } catch (e: any) {
    L(`ERROR: ${e.message}`);
    await page.screenshot({ path: path.join(outDir, "explore-v2-error.png"), fullPage: true });
  } finally {
    fs.writeFileSync(path.join(outDir, "locator-exploration.txt"), log.join("\n"), "utf-8");
    await browser.close();
  }
})();
