/**
 * Plane UI Locator Exploration Script
 * Discovers real page elements and their accessible locators.
 * Output: evidence/day3/ui/locator-exploration.txt
 */
import { chromium } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

// Read .env safely — never log values
function loadEnv(): Record<string, string> {
  const envPath = path.resolve(__dirname, "..", ".env");
  if (!fs.existsSync(envPath)) throw new Error(".env not found");
  const result: Record<string, string> = {};
  const lines = fs.readFileSync(envPath, "utf-8").split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) continue;
    result[trimmed.slice(0, eqIdx)] = trimmed.slice(eqIdx + 1);
  }
  return result;
}

async function logElement(page: any, label: string, locator: any) {
  const count = await locator.count();
  return `${label}: count=${count}`;
}

async function exploreLocators(page: any, section: string, selectors: Array<{ label: string; selector: any }>) {
  const lines: string[] = [];
  lines.push(`\n=== ${section} ===`);
  for (const { label, selector } of selectors) {
    try {
      const result = await logElement(page, label, selector);
      lines.push(`  ${result}`);
    } catch (e: any) {
      lines.push(`  ${label}: ERROR - ${e.message}`);
    }
  }
  return lines;
}

(async () => {
  const env = loadEnv();
  const BASE_URL = env.PLANE_BASE_URL || "http://192.168.146.132:8090";
  const EMAIL = env.PLANE_UI_EMAIL;
  const PASSWORD = env.PLANE_UI_PASSWORD;

  if (!EMAIL || !PASSWORD) {
    console.error("Missing PLANE_UI_EMAIL or PLANE_UI_PASSWORD in .env");
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const outDir = path.resolve(__dirname, "..", "evidence", "day3", "ui");
  fs.mkdirSync(outDir, { recursive: true });

  const outputFile = path.join(outDir, "locator-exploration.txt");
  const allLines: string[] = [];
  allLines.push("=== Plane UI Locator Exploration ===");
  allLines.push(`Base URL: ${BASE_URL}`);
  allLines.push(`Timestamp: ${new Date().toISOString()}`);

  try {
    // ======= 1. LOGIN PAGE - Email step =======
    allLines.push("\n\n## PHASE 1: Login Page — Email Step");
    await page.goto(BASE_URL, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000); // let JS hydrate

    allLines.push(`Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-01-login-email.png"), fullPage: true });

    const emailSelectors = [
      { label: "getByRole(textbox)", selector: page.getByRole("textbox") },
      { label: "getByPlaceholder('Enter your email')", selector: page.getByPlaceholder("Enter your email") },
      { label: "getByPlaceholder(/email/i)", selector: page.getByPlaceholder(/email/i) },
      { label: "getByLabel(/email/i)", selector: page.getByLabel(/email/i) },
      { label: "input[type=email]", selector: page.locator("input[type=email]") },
      { label: "input[name=email]", selector: page.locator("input[name=email]") },
      { label: "getByRole(button, 'Continue')", selector: page.getByRole("button", { name: /continue|sign in|next|log in/i }) },
      { label: "getByText('Continue')", selector: page.getByText("Continue", { exact: true }) },
    ];
    for (const { label, selector } of emailSelectors) {
      try {
        allLines.push(`  ${label}: count=${await selector.count()}`);
      } catch (e: any) { allLines.push(`  ${label}: ERROR - ${e.message}`); }
    }

    // Dump all visible buttons and inputs for reference
    const allButtons = await page.locator("button").all();
    allLines.push(`  Total <button> elements: ${allButtons.length}`);
    for (const btn of allButtons) {
      const text = await btn.textContent();
      const visible = await btn.isVisible();
      if (visible) allLines.push(`    button: "${text?.trim()}"`);
    }

    const allInputs = await page.locator("input").all();
    allLines.push(`  Total <input> elements: ${allInputs.length}`);
    for (const inp of allInputs) {
      const type = await inp.getAttribute("type");
      const placeholder = await inp.getAttribute("placeholder");
      const name = await inp.getAttribute("name");
      const visible = await inp.isVisible();
      if (visible) allLines.push(`    input: type="${type}" placeholder="${placeholder}" name="${name}"`);
    }

    // ======= 2. LOGIN PAGE - Password step =======
    allLines.push("\n\n## PHASE 2: Login Page — Password Step");
    // Enter email and click continue
    const emailInput = page.getByRole("textbox").first();
    if ((await emailInput.count()) > 0) {
      await emailInput.fill(EMAIL);
      allLines.push("  Filled email input (getByRole textbox)");
    }

    const continueBtn = page.getByRole("button", { name: /continue|sign in|next|log in/i });
    if ((await continueBtn.count()) > 0) {
      await continueBtn.first().click();
      allLines.push("  Clicked continue button");
      await page.waitForTimeout(2000);
    }

    allLines.push(`Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-02-login-password.png"), fullPage: true });

    const pwdSelectors = [
      { label: "getByPlaceholder(/password/i)", selector: page.getByPlaceholder(/password/i) },
      { label: "getByPlaceholder('Enter your password')", selector: page.getByPlaceholder("Enter your password") },
      { label: "getByLabel(/password/i)", selector: page.getByLabel(/password/i) },
      { label: "input[type=password]", selector: page.locator("input[type=password]") },
      { label: "getByRole(button, /sign in|log in|login/i)", selector: page.getByRole("button", { name: /sign in|log in|login|continue/i }) },
    ];
    for (const { label, selector } of pwdSelectors) {
      try {
        allLines.push(`  ${label}: count=${await selector.count()}`);
      } catch (e: any) { allLines.push(`  ${label}: ERROR - ${e.message}`); }
    }

    const pwdButtons = await page.locator("button").all();
    allLines.push(`  Total <button> elements: ${pwdButtons.length}`);
    for (const btn of pwdButtons) {
      const text = await btn.textContent();
      const visible = await btn.isVisible();
      if (visible) allLines.push(`    button: "${text?.trim()}"`);
    }

    // Fill password and login
    const pwdInput = page.getByPlaceholder(/password/i);
    if ((await pwdInput.count()) > 0) {
      await pwdInput.first().fill(PASSWORD);
      allLines.push("  Filled password input (getByPlaceholder /password/)");
    } else {
      const pwdAlt = page.locator("input[type=password]").first();
      if ((await pwdAlt.count()) > 0) {
        await pwdAlt.fill(PASSWORD);
        allLines.push("  Filled password input (input[type=password])");
      }
    }

    const loginBtn = page.getByRole("button", { name: /sign in|log in|login/i });
    if ((await loginBtn.count()) > 0) {
      await loginBtn.first().click();
      allLines.push("  Clicked login button");
      await page.waitForTimeout(3000);
    }

    allLines.push(`Current URL after login: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-03-after-login.png"), fullPage: true });

    // ======= 3. WORKSPACE PAGE =======
    allLines.push("\n\n## PHASE 3: Workspace Page");
    const wsSelectors = [
      { label: "getByText('QA Lab')", selector: page.getByText("QA Lab") },
      { label: "getByText('Plane QA')", selector: page.getByText("Plane QA") },
      { label: "getByRole(link, 'Plane QA')", selector: page.getByRole("link", { name: /Plane QA/i }) },
      { label: "getByRole(link, /workspace/i)", selector: page.getByRole("link", { name: /qa lab|workspace/i }) },
    ];
    for (const { label, selector } of wsSelectors) {
      try {
        allLines.push(`  ${label}: count=${await selector.count()}`);
      } catch (e: any) { allLines.push(`  ${label}: ERROR - ${e.message}`); }
    }

    // Dump page headings and links
    const headings = await page.locator("h1, h2, h3, h4, h5, h6").all();
    allLines.push(`  Total headings: ${headings.length}`);
    for (const h of headings) {
      const text = await h.textContent();
      const visible = await h.isVisible();
      if (visible) allLines.push(`    heading: "${text?.trim()}"`);
    }

    const links = await page.locator("a").all();
    allLines.push(`  Total <a> elements: ${links.length}`);
    for (const l of links) {
      const text = await l.textContent();
      const visible = await l.isVisible();
      if (visible && text?.trim()) allLines.push(`    link: "${text.trim()}"`);
    }

    // ======= 4. NAVIGATE TO PROJECT =======
    allLines.push("\n\n## PHASE 4: Project Page");
    // Try to find and click Plane QA Project
    const projectLink = page.getByRole("link", { name: /Plane QA/i }).or(page.getByText("Plane QA Project"));
    if ((await projectLink.count()) > 0) {
      await projectLink.first().click();
      await page.waitForTimeout(2000);
      allLines.push("  Clicked Plane QA Project link");
    }
    allLines.push(`Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-04-project.png"), fullPage: true });

    // ======= 5. WORK ITEMS PAGE =======
    allLines.push("\n\n## PHASE 5: Work Items Page");
    // Look for "Work Items" or "Issues" navigation
    const workItemsNav = page.getByRole("link", { name: /work items|issues/i })
      .or(page.getByText(/work items|issues/i));
    if ((await workItemsNav.count()) > 0) {
      await workItemsNav.first().click();
      await page.waitForTimeout(2000);
      allLines.push("  Clicked Work Items / Issues navigation");
    }
    allLines.push(`Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-05-work-items.png"), fullPage: true });

    // List existing work items
    const issueRows = page.locator("[class*=issue], [class*=row], tr, [role=row]");
    allLines.push(`  Potential issue rows: count=${await issueRows.count()}`);

    const issueLinks = page.locator("a").all();
    const issueTexts: string[] = [];
    for (const l of issueLinks) {
      const text = await l.textContent();
      const visible = await l.isVisible();
      if (visible && text?.trim()) issueTexts.push(text.trim());
    }
    allLines.push(`  Visible links (${issueTexts.length}): ${issueTexts.slice(0, 30).join(" | ")}`);

    // Look for New/Add button
    const addBtn = page.getByRole("button", { name: /new|add|create/i });
    allLines.push(`  getByRole(button, /new|add|create/i): count=${await addBtn.count()}`);
    for (const b of await addBtn.all()) {
      allLines.push(`    add/create button: "${await b.textContent()}"`);
    }

    // ======= 6. OPEN A WORK ITEM =======
    allLines.push("\n\n## PHASE 6: Work Item Detail");
    // Click the first work item we can find
    const firstIssueLink = page.locator("a").filter({ hasText: /Verify|AUTO|test|environment/i }).first();
    if ((await firstIssueLink.count()) > 0) {
      const title = await firstIssueLink.textContent();
      await firstIssueLink.click();
      await page.waitForTimeout(2000);
      allLines.push(`  Clicked work item: "${title?.trim()}"`);
    }
    allLines.push(`Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-06-work-item-detail.png"), fullPage: true });

    // Detail page elements
    const detailHeadings = await page.locator("h1, h2, h3").all();
    for (const h of detailHeadings) {
      const text = await h.textContent();
      const visible = await h.isVisible();
      if (visible) allLines.push(`  Detail heading: "${text?.trim()}"`);
    }

    // Look for description, priority, delete/archive
    const descArea = page.locator("[class*=description], textarea, [contenteditable=true], [role=textbox]");
    allLines.push(`  Potential description areas: count=${await descArea.count()}`);

    const deleteBtn = page.getByRole("button", { name: /delete|archive|remove/i });
    allLines.push(`  Delete/archive buttons: count=${await deleteBtn.count()}`);

    // ======= 7. NEW WORK ITEM FORM =======
    allLines.push("\n\n## PHASE 7: New Work Item Form");
    // Go back to list first
    await page.goBack();
    await page.waitForTimeout(1000);

    const newBtn = page.getByRole("button", { name: /new|add|create/i });
    if ((await newBtn.count()) > 0) {
      await newBtn.first().click();
      await page.waitForTimeout(2000);
      allLines.push("  Clicked New/Add button");
    }
    allLines.push(`Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(outDir, "explore-07-new-form.png"), fullPage: true });

    const formInputs = await page.locator("input, textarea, [contenteditable=true]").all();
    for (const inp of formInputs) {
      const placeholder = await inp.getAttribute("placeholder");
      const type = await inp.getAttribute("type");
      const name = await inp.getAttribute("name");
      const visible = await inp.isVisible();
      if (visible) allLines.push(`  form field: type="${type}" placeholder="${placeholder}" name="${name}"`);
    }

    const formBtns = await page.locator("button").all();
    for (const b of formBtns) {
      const text = await b.textContent();
      const visible = await b.isVisible();
      if (visible && text?.trim()) allLines.push(`  form button: "${text.trim()}"`);
    }

    allLines.push("\n\n=== EXPLORATION COMPLETE ===");

  } catch (e: any) {
    allLines.push(`\n\n=== ERROR: ${e.message} ===`);
    await page.screenshot({ path: path.join(outDir, "explore-error.png"), fullPage: true });
  } finally {
    fs.writeFileSync(outputFile, allLines.join("\n"), "utf-8");
    console.log(`Locator exploration written to: ${outputFile}`);
    await browser.close();
  }
})();
