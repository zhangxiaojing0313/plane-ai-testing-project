/**
 * Plane Workspace Page Object
 * Dashboard/home page after login
 */
import { Page, Locator } from "@playwright/test";

export class WorkspacePage {
  readonly page: Page;
  readonly workspaceHeading: Locator;
  readonly planeQaProjectLink: Locator;
  readonly newWorkItemButton: Locator;
  readonly sidebarHomeLink: Locator;
  readonly sidebarProjectsLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.workspaceHeading = page.getByRole("heading", { name: "QA Lab" });
    this.planeQaProjectLink = page.getByRole("link", { name: /Plane QA Project/i });
    this.newWorkItemButton = page.getByRole("button", { name: "New work item" });
    this.sidebarHomeLink = page.getByRole("link", { name: "Home" });
    this.sidebarProjectsLink = page.getByRole("link", { name: "Projects" });
  }

  async goto(workspaceSlug: string): Promise<void> {
    const baseURL = process.env.PLANE_BASE_URL || "http://192.168.146.132:8090";
    await this.page.goto(`${baseURL}/${workspaceSlug}/`, {
      waitUntil: "networkidle",
      timeout: 15000,
    });
  }

  async isLoaded(): Promise<boolean> {
    return this.workspaceHeading.isVisible();
  }

  async navigateToProject(): Promise<void> {
    await this.planeQaProjectLink.first().click();
    await this.page.waitForURL(/\/issues/, { timeout: 10000 });
  }
}
