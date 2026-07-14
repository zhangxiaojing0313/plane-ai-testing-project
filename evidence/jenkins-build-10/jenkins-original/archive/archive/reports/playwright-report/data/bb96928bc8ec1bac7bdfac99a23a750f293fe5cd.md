# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: login.spec.ts >> Login Flow >> UI-001: Login with valid credentials and enter QA Lab
- Location: tests/ui/login.spec.ts:11:7

# Error details

```
TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
=========================== logs ===========================
waiting for navigation until "load"
  navigated to "http://192.168.146.132:8090/"
============================================================
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic:
    - region "Notifications"
  - main [ref=e3]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - link [ref=e7] [cursor=pointer]:
          - /url: /
          - img [ref=e8]
        - generic [ref=e16]:
          - generic [ref=e17]: New to Plane?
          - link "Sign up" [ref=e18] [cursor=pointer]:
            - /url: /sign-up/
      - generic [ref=e20]:
        - generic [ref=e21]:
          - generic [ref=e22]: Work in all dimensions.
          - generic [ref=e23]: Welcome back to Plane.
        - generic [ref=e24]:
          - generic [ref=e25]:
            - text: Email
            - textbox "Email" [active] [ref=e27]:
              - /placeholder: name@company.com
          - button "Continue" [disabled]
        - paragraph [ref=e29]:
          - text: By signing in, you understand and agree to our
          - link "Terms of Service" [ref=e30] [cursor=pointer]:
            - /url: https://plane.so/legals/terms-and-conditions/
          - text: and
          - link "Privacy Policy" [ref=e31] [cursor=pointer]:
            - /url: https://plane.so/legals/privacy-policy/
          - text: .
      - generic [ref=e32]:
        - generic [ref=e33]: Join 10,000+ teams building with Plane
        - generic [ref=e34]:
          - img [ref=e36]
          - img [ref=e40]
          - img [ref=e43]
          - img [ref=e52]
```

# Test source

```ts
  1  | /**
  2  |  * Plane Login Page Object
  3  |  * Handles two-step login: email → Continue → password → Go to workspace
  4  |  */
  5  | import { Page, Locator } from "@playwright/test";
  6  | 
  7  | export class LoginPage {
  8  |   readonly page: Page;
  9  |   readonly emailInput: Locator;
  10 |   readonly continueButton: Locator;
  11 |   readonly passwordInput: Locator;
  12 |   readonly loginButton: Locator;
  13 | 
  14 |   constructor(page: Page) {
  15 |     this.page = page;
  16 |     // Step 1: Email — use precise attribute selectors unique to login form
  17 |     this.emailInput = page.locator("input[name=email]");
  18 |     this.continueButton = page.getByRole("button", { name: "Continue" });
  19 |     // Step 2: Password (appears after Continue)
  20 |     this.passwordInput = page.locator("input[type=password]");
  21 |     this.loginButton = page.getByRole("button", { name: /go to workspace/i });
  22 |   }
  23 | 
  24 |   async goto(): Promise<void> {
  25 |     const baseURL = process.env.PLANE_BASE_URL || "http://192.168.146.132:8090";
  26 |     await this.page.goto(baseURL, { waitUntil: "networkidle", timeout: 30000 });
  27 |     // Wait for the login form: email input should be visible
  28 |     await this.emailInput.waitFor({ state: "visible", timeout: 10000 });
  29 |   }
  30 | 
  31 |   async login(email: string, password: string): Promise<void> {
  32 |     await this.emailInput.fill(email);
  33 |     await this.continueButton.click();
  34 |     // Wait for password step to render
  35 |     await this.passwordInput.waitFor({ state: "visible", timeout: 10000 });
  36 |     await this.passwordInput.fill(password);
  37 |     await this.loginButton.click();
  38 |     // Wait for redirect to workspace
> 39 |     await this.page.waitForURL(/\/[a-zA-Z0-9-]+\//, { timeout: 15000 });
     |                     ^ TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
  40 |   }
  41 | }
  42 | 
```