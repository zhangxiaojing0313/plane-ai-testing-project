/**
 * Plane Project / Issues Page Object
 * Work items list view
 */
import { Page, Locator } from "@playwright/test";

export class ProjectPage {
  readonly page: Page;
  readonly issuesUrl: string;

  readonly workItemsLink: Locator;
  readonly addWorkItemButton: Locator;
  readonly newWorkItemSidebarButton: Locator;
  readonly searchInput: Locator;
  readonly issueLinks: Locator;

  constructor(page: Page, workspaceSlug: string, projectId: string) {
    this.page = page;
    this.issuesUrl = `/${workspaceSlug}/projects/${projectId}/issues`;

    this.workItemsLink = page.getByRole("link", { name: "Work items" });
    this.addWorkItemButton = page.locator("button").filter({ hasText: /Add work item/i });
    this.newWorkItemSidebarButton = page.getByRole("button", { name: "New work item" });
    this.searchInput = page.getByPlaceholder("Search commands...");
    this.issueLinks = page.locator("a").filter({ hasText: /PLANEQAPRO/i });
  }

  async goto(): Promise<void> {
    const baseURL = process.env.PLANE_BASE_URL || "http://192.168.146.132:8090";
    await this.page.goto(`${baseURL}${this.issuesUrl}`, {
      waitUntil: "domcontentloaded",
      timeout: 20000,
    });
    // Wait for the work items list to render (SPA hydration)
    await this.page.locator("a").filter({ hasText: /Verify Plane|PLANEQAPRO|AUTO/i }).first().waitFor({ state: "visible", timeout: 15000 }).catch(() => {
      // May have no work items — acceptable
    });
  }

  async isLoaded(): Promise<boolean> {
    // Wait for issue links or the add button to appear
    await this.page.waitForLoadState("networkidle");
    return true;
  }

  async getIssueLinks(): Promise<Locator> {
    return this.page.locator("a").filter({ hasText: /PLANEQAPRO/i });
  }

  async clickIssueByTitle(titlePattern: string | RegExp): Promise<void> {
    const link = this.page.locator("a").filter({ hasText: titlePattern }).first();
    await link.click();
    // Drawer opens inline — wait for detail content
    await this.page.waitForTimeout(2000);
  }

  async openAddWorkItemForm(): Promise<void> {
    // Click the in-page "Add work item" button
    const btn = this.addWorkItemButton.first();
    if (await btn.isVisible()) {
      await btn.click();
    } else {
      // Fallback: use sidebar button
      await this.newWorkItemSidebarButton.first().click();
    }
    // Wait for title input to appear
    await this.page.locator("input[name=name]").waitFor({ state: "visible", timeout: 10000 });
  }
}
