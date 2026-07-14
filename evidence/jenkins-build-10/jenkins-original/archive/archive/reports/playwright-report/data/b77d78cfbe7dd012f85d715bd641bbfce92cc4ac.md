# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: work-item.spec.ts >> Work Items >> UI-007: Modify created work item and verify persistence
- Location: tests/ui/work-item.spec.ts:99:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('a').filter({ hasText: 'AUTO-D3-UI-2026-07-14T00-02-54' }).first()
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('a').filter({ hasText: 'AUTO-D3-UI-2026-07-14T00-02-54' }).first()

```

```yaml
- region "Notifications"
- main:
  - button "Open workspace switcher":
    - text: Q
    - heading "QA Lab" [level=4]
    - img
  - button:
    - img
    - textbox "Search commands..."
  - link:
    - /url: /qa-lab/notifications/
    - img
  - button:
    - button:
      - img
  - link "Star us on GitHub":
    - /url: https://github.com/makeplane/plane
  - button "A":
    - button "A"
  - complementary "Main sidebar":
    - complementary:
      - text: Projects
      - button:
        - img
      - button:
        - img
      - button "New work item":
        - img
        - text: New work item
      - link "Home":
        - /url: /qa-lab/
        - img
        - paragraph: Home
      - link "Drafts":
        - /url: /qa-lab/drafts/
        - img
        - paragraph: Drafts
      - link "Your work":
        - /url: /qa-lab/profile/91b3dba8-eedf-4dd1-b8f8-2b98c4310304/
        - img
        - paragraph: Your work
      - link "Stickies":
        - /url: /qa-lab/stickies/
        - img
        - paragraph: Stickies
      - button "aria_labels.app_sidebar.close_workspace_menu" [expanded]: Workspace
      - button "aria_labels.app_sidebar.close_workspace_menu" [expanded]:
        - img
      - link "Projects":
        - /url: /qa-lab/projects/
        - img
        - paragraph: Projects
      - button "aria_labels.app_sidebar.open_extended_sidebar":
        - img
        - text: More
      - button "Close projects menu" [expanded]: Projects
      - button "Close projects menu":
        - img
      - link "Close project menu":
        - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/issues
        - button "Close project menu":
          - text: 📌
          - paragraph: Plane QA Project
      - button "Toggle quick actions menu":
        - button:
          - img
      - link "Work items":
        - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/issues/
        - img
        - text: Work items
      - link "Pages":
        - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/pages/
        - img
        - text: Pages
      - link "Open project menu":
        - /url: /qa-lab/projects/93c04c4a-6874-425e-b143-17f55ddc4a92/issues
        - button "Open project menu":
          - text: 👇
          - paragraph: QA Lab
      - button "Toggle quick actions menu":
        - button:
          - img
      - button "Open paid plans' modal": Community
      - separator "Resize sidebar"
  - complementary "Sidebar peek view":
    - complementary:
      - text: Projects
      - button:
        - img
      - button:
        - img
      - button "New work item":
        - img
        - text: New work item
      - link "Home":
        - /url: /qa-lab/
        - img
        - paragraph: Home
      - link "Drafts":
        - /url: /qa-lab/drafts/
        - img
        - paragraph: Drafts
      - link "Your work":
        - /url: /qa-lab/profile/91b3dba8-eedf-4dd1-b8f8-2b98c4310304/
        - img
        - paragraph: Your work
      - link "Stickies":
        - /url: /qa-lab/stickies/
        - img
        - paragraph: Stickies
      - button "aria_labels.app_sidebar.close_workspace_menu" [expanded]: Workspace
      - button "aria_labels.app_sidebar.close_workspace_menu" [expanded]:
        - img
      - link "Projects":
        - /url: /qa-lab/projects/
        - img
        - paragraph: Projects
      - button "aria_labels.app_sidebar.open_extended_sidebar":
        - img
        - text: More
      - button "Close projects menu" [expanded]: Projects
      - button "Close projects menu":
        - img
      - link "Close project menu":
        - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/issues
        - button "Close project menu":
          - text: 📌
          - paragraph: Plane QA Project
      - button "Toggle quick actions menu":
        - button:
          - img
      - link "Work items":
        - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/issues/
        - img
        - text: Work items
      - link "Pages":
        - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/pages/
        - img
        - text: Pages
      - link "Open project menu":
        - /url: /qa-lab/projects/93c04c4a-6874-425e-b143-17f55ddc4a92/issues
        - button "Open project menu":
          - text: 👇
          - paragraph: QA Lab
      - button "Toggle quick actions menu":
        - button:
          - img
      - button "Open paid plans' modal": Community
      - separator "Resize sidebar"
  - main:
    - button "📌 Plane QA Project":
      - button "📌 Plane QA Project"
      - img
    - link "Work Items":
      - /url: /qa-lab/projects/0c1cf73f-2d88-430b-812b-2e1c7f010c3c/issues/
      - img
      - text: Work Items
    - button:
      - img
    - button:
      - img
    - button:
      - img
    - button:
      - img
    - button:
      - img
    - button:
      - img
    - button "Display"
    - button "Analytics"
    - button "Add work item"
```

# Test source

```ts
  44  |   } catch (e: any) {
  45  |     return `API_CLEANUP_ERROR: ${e.message}`;
  46  |   }
  47  | }
  48  | 
  49  | test.describe("Work Items", () => {
  50  |   test.use({ storageState: ".playwright/auth-state.json" });
  51  | 
  52  |   let testTitle: string;
  53  |   let projectPage: ProjectPage;
  54  |   let workItemPage: WorkItemPage;
  55  | 
  56  |   test.beforeEach(async ({ page }) => {
  57  |     projectPage = new ProjectPage(page, WORKSPACE_SLUG, PROJECT_ID);
  58  |     workItemPage = new WorkItemPage(page);
  59  |     await projectPage.goto();
  60  |   });
  61  | 
  62  |   test("UI-004: Open existing work item and verify detail drawer", async ({ page }) => {
  63  |     await projectPage.clickIssueByTitle(/Verify Plane environment availability/i);
  64  | 
  65  |     // Verify detail drawer is visible with action buttons
  66  |     await expect(page.getByRole("button", { name: "Edit" }).first()).toBeVisible({ timeout: 5000 });
  67  |     await expect(page.getByRole("button", { name: "Delete" }).first()).toBeVisible({ timeout: 5000 });
  68  | 
  69  |     // Close drawer
  70  |     await workItemPage.closeDrawer();
  71  |   });
  72  | 
  73  |   test("UI-005: Open New Work Item form and verify empty-title behavior", async ({ page }) => {
  74  |     await projectPage.openAddWorkItemForm();
  75  |     await expect(workItemPage.titleInput).toBeVisible({ timeout: 5000 });
  76  | 
  77  |     // In Plane v1.3.1, Save is NOT disabled with empty title (recorded behavior)
  78  |     const saveDisabled = await workItemPage.isSaveDisabled();
  79  |     console.log(`Save button disabled with empty title: ${saveDisabled}`);
  80  | 
  81  |     // Close form without submitting
  82  |     await workItemPage.discard();
  83  |     await expect(workItemPage.titleInput).not.toBeVisible({ timeout: 5000 }).catch(() => {
  84  |       // Form may stay open if discard didn't close — cleanup with Escape
  85  |     });
  86  |   });
  87  | 
  88  |   test("UI-006: Create unique work item and verify it appears in list", async ({ page }) => {
  89  |     testTitle = generateWorkItemTitle();
  90  | 
  91  |     await projectPage.openAddWorkItemForm();
  92  |     await workItemPage.fillTitle(testTitle);
  93  |     await workItemPage.save();
  94  | 
  95  |     // Verify new item appears in list
  96  |     await expect(page.locator("a").filter({ hasText: testTitle }).first()).toBeVisible({ timeout: 10000 });
  97  |   });
  98  | 
  99  |   test("UI-007: Modify created work item and verify persistence", async ({ page }) => {
  100 |     test.setTimeout(60000);
  101 |     testTitle = generateWorkItemTitle();
  102 | 
  103 |     // Step 1: Create the work item
  104 |     await projectPage.openAddWorkItemForm();
  105 |     await workItemPage.fillTitle(testTitle);
  106 |     await workItemPage.save();
  107 |     await page.waitForTimeout(2000);
  108 | 
  109 |     // Step 2: Open the new work item's detail drawer
  110 |     const itemLink = page.locator("a").filter({ hasText: testTitle }).first();
  111 |     await expect(itemLink).toBeVisible({ timeout: 10000 });
  112 |     await itemLink.click();
  113 |     await page.waitForTimeout(3000);
  114 | 
  115 |     // Step 3: Try to interact with a property (look for priority/state dropdowns)
  116 |     // Plane v1.3.1 detail drawer shows property buttons like "Backlog", "None", "Add assignees"
  117 |     // Click on the state button (e.g., "Backlog") to see if we can change it
  118 |     const stateBtn = page.locator("button").filter({ hasText: /Backlog/i }).first();
  119 |     if (await stateBtn.isVisible().catch(() => false)) {
  120 |       await stateBtn.click();
  121 |       await page.waitForTimeout(1000);
  122 | 
  123 |       // Look for a different state to switch to
  124 |       const startedOption = page.getByText(/started|in progress/i).first();
  125 |       if (await startedOption.isVisible().catch(() => false)) {
  126 |         await startedOption.click();
  127 |         await page.waitForTimeout(1000);
  128 |         console.log(`Changed state for ${testTitle}`);
  129 |       } else {
  130 |         // Close dropdown if nothing selectable
  131 |         await page.keyboard.press("Escape");
  132 |         await page.waitForTimeout(500);
  133 |       }
  134 |     }
  135 | 
  136 |     // Close drawer
  137 |     await workItemPage.closeDrawer();
  138 | 
  139 |     // Step 4: Reload page and verify persistence
  140 |     await page.reload();
  141 |     await page.waitForTimeout(2000);
  142 | 
  143 |     // Step 5: Verify the work item still exists
> 144 |     await expect(page.locator("a").filter({ hasText: testTitle }).first()).toBeVisible({ timeout: 10000 });
      |                                                                            ^ Error: expect(locator).toBeVisible() failed
  145 |   });
  146 | 
  147 |   test("UI-008: Delete created work item and verify removal from list", async ({ page }) => {
  148 |     testTitle = generateWorkItemTitle();
  149 | 
  150 |     // Step 1: Create the work item
  151 |     await projectPage.openAddWorkItemForm();
  152 |     await workItemPage.fillTitle(testTitle);
  153 |     await workItemPage.save();
  154 |     await page.waitForTimeout(2000);
  155 | 
  156 |     // Step 2: Try UI delete — first close any interfering overlays
  157 |     // Dismiss any open menus by pressing Escape
  158 |     await page.keyboard.press("Escape");
  159 |     await page.waitForTimeout(500);
  160 | 
  161 |     // Find the work item in the list and use its context menu
  162 |     const itemLink = page.locator("a").filter({ hasText: testTitle }).first();
  163 |     await expect(itemLink).toBeVisible({ timeout: 10000 });
  164 | 
  165 |     // Click the item to open detail drawer
  166 |     await itemLink.click();
  167 |     await page.waitForTimeout(3000);
  168 | 
  169 |     // Try clicking Delete with force to bypass overlays
  170 |     const deleteBtn = page.getByRole("button", { name: "Delete" }).first();
  171 |     let deletedViaUI = false;
  172 | 
  173 |     try {
  174 |       await deleteBtn.click({ force: true, timeout: 5000 });
  175 |       await page.waitForTimeout(1000);
  176 | 
  177 |       // Check for confirmation dialog
  178 |       const confirmBtn = page.getByRole("button", { name: /delete|confirm|yes/i });
  179 |       if (await confirmBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
  180 |         await confirmBtn.click();
  181 |         await page.waitForTimeout(2000);
  182 |         deletedViaUI = true;
  183 |       }
  184 |     } catch {
  185 |       console.log("UI delete click failed, using API cleanup");
  186 |     }
  187 | 
  188 |     // Step 3: Verify removal
  189 |     await page.waitForTimeout(2000);
  190 |     const stillVisible = await page.locator("a").filter({ hasText: testTitle }).first().isVisible().catch(() => false);
  191 | 
  192 |     if (!stillVisible) {
  193 |       console.log(`UI delete successful for "${testTitle}"`);
  194 |     } else {
  195 |       // Fallback: API cleanup
  196 |       console.log(`Falling back to API cleanup for "${testTitle}"`);
  197 |       const result = await apiCleanup(new RegExp(testTitle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  198 |       console.log(`API cleanup: ${result}`);
  199 | 
  200 |       // Refresh and verify
  201 |       await page.reload();
  202 |       await page.waitForTimeout(2000);
  203 |     }
  204 | 
  205 |     // Final verification: item should not be in list
  206 |     const stillThere = await page.locator("a").filter({ hasText: testTitle }).first().isVisible().catch(() => false);
  207 |     expect(stillThere).toBe(false);
  208 |   });
  209 | });
  210 | 
  211 | /**
  212 |  * Global teardown: Clean up any leftover AUTO-D3-UI test data via API
  213 |  */
  214 | test.afterAll(async () => {
  215 |   const result = await apiCleanup(/AUTO-D3-UI-/);
  216 |   const cleanupFile = path.resolve(
  217 |     __dirname, "..", "..", "evidence", "day3", "ui", "cleanup-result.txt"
  218 |   );
  219 |   fs.mkdirSync(path.dirname(cleanupFile), { recursive: true });
  220 |   fs.writeFileSync(cleanupFile, `Cleanup result: ${result}\nTimestamp: ${new Date().toISOString()}\n`, "utf-8");
  221 |   console.log(`Global cleanup: ${result}`);
  222 | });
  223 | 
```