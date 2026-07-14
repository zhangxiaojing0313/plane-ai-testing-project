/**
 * Plane Login Page Object
 * Handles two-step login: email → Continue → password → Go to workspace
 */
import { Page, Locator } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly continueButton: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;

  constructor(page: Page) {
    this.page = page;
    // Step 1: Email — use precise attribute selectors unique to login form
    this.emailInput = page.locator("input[name=email]");
    this.continueButton = page.getByRole("button", { name: "Continue" });
    // Step 2: Password (appears after Continue)
    this.passwordInput = page.locator("input[type=password]");
    this.loginButton = page.getByRole("button", { name: /go to workspace/i });
  }

  async goto(): Promise<void> {
    const baseURL = process.env.PLANE_BASE_URL || "http://192.168.146.132:8090";
    await this.page.goto(baseURL, { waitUntil: "networkidle", timeout: 30000 });
    // Wait for the login form: email input should be visible
    await this.emailInput.waitFor({ state: "visible", timeout: 10000 });
  }

  async login(email: string, password: string): Promise<void> {
    // Step 1: enter email and continue
    await this.emailInput.fill(email);
    await this.continueButton.click();

    // Wait for password step to render
    await this.passwordInput.waitFor({ state: "visible", timeout: 10000 });

    // Step 2: enter password and submit
    await this.passwordInput.fill(password);
    await this.loginButton.click();

    // Determine outcome: success (entered /qa-lab/) vs failure (returned to email step)
    // Each branch catches its own timeout so the losing promise never rejects unhandled.
    const result = await Promise.race([
      this.page
        .waitForURL(/\/qa-lab(?:\/|$)/, { timeout: 20000 })
        .then(() => "success" as const)
        .catch(() => "timeout" as const),

      this.emailInput
        .waitFor({ state: "visible", timeout: 20000 })
        .then(() => "returned-to-email" as const)
        .catch(() => "timeout" as const),
    ]);

    if (result === "returned-to-email") {
      throw new Error(
        `Plane login rejected: returned to email step. Current URL: ${this.page.url()}`
      );
    }

    if (result === "timeout") {
      throw new Error(
        `Plane login timed out: neither workspace URL nor email step detected. Current URL: ${this.page.url()}`
      );
    }

    // Check for explicit error_code in URL
    if (this.page.url().includes("error_code")) {
      throw new Error(
        `Plane login rejected: error_code detected. Current URL: ${this.page.url()}`
      );
    }
  }
}
