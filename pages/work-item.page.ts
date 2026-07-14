/**
 * Work Item Page Object
 * Covers: create form, detail drawer, edit, delete/archive
 */
import { Page, Locator } from "@playwright/test";

export class WorkItemPage {
  readonly page: Page;

  // Create form
  readonly titleInput: Locator;
  readonly saveButton: Locator;
  readonly discardButton: Locator;
  readonly createMoreButton: Locator;

  // Detail drawer
  readonly drawerHeading: Locator;
  readonly editButton: Locator;
  readonly deleteButton: Locator;
  readonly archiveButton: Locator;
  readonly descriptionButton: Locator;

  constructor(page: Page) {
    this.page = page;

    // Create form elements
    this.titleInput = page.locator("input[name=name]").or(page.getByPlaceholder("Title"));
    this.saveButton = page.getByRole("button", { name: "Save" });
    this.discardButton = page.getByRole("button", { name: "Discard" });
    this.createMoreButton = page.getByRole("button", { name: "Create more" });

    // Detail drawer elements
    this.drawerHeading = page.locator("h1, h2, h3").first();
    this.editButton = page.getByRole("button", { name: "Edit" });
    this.deleteButton = page.getByRole("button", { name: "Delete" });
    this.archiveButton = page.getByRole("button", { name: /Archive/i });
    this.descriptionButton = page.locator("button").filter({ hasText: /description/i });
  }

  async fillTitle(title: string): Promise<void> {
    await this.titleInput.fill(title);
  }

  async save(): Promise<void> {
    await this.saveButton.click();
    // Wait for success indicator or form to close
    await this.page.waitForTimeout(2000);
  }

  async discard(): Promise<void> {
    // Discard button may be disabled when title is empty
    const btn = this.discardButton;
    if (await btn.isEnabled().catch(() => false)) {
      await btn.click();
    } else {
      await this.page.keyboard.press("Escape");
    }
    await this.page.waitForTimeout(1000);
  }

  async isSaveDisabled(): Promise<boolean> {
    return this.saveButton.isDisabled();
  }

  // --- Detail drawer actions ---

  async getDrawerTitle(): Promise<string> {
    const text = await this.drawerHeading.textContent();
    return text?.trim() || "";
  }

  async clickDelete(): Promise<void> {
    await this.deleteButton.first().click();
    // A confirmation may appear
    await this.page.waitForTimeout(1000);
  }

  async clickArchive(): Promise<void> {
    await this.archiveButton.first().click();
    await this.page.waitForTimeout(1000);
  }

  async isIssueVisibleInList(titlePattern: string | RegExp): Promise<boolean> {
    const link = this.page.locator("a").filter({ hasText: titlePattern }).first();
    return link.isVisible().catch(() => false);
  }

  async closeDrawer(): Promise<void> {
    await this.page.keyboard.press("Escape");
    await this.page.waitForTimeout(1000);
  }
}
