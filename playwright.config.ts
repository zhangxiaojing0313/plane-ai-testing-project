import { defineConfig, devices } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

// Manual .env loader — avoids adding dotenv dependency
function loadEnvFile(): void {
  const envPath = path.resolve(__dirname, ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf-8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const idx = t.indexOf("=");
    if (idx === -1) continue;
    const key = t.slice(0, idx);
    if (!process.env[key]) {
      process.env[key] = t.slice(idx + 1);
    }
  }
}
loadEnvFile();

export default defineConfig({
  testDir: "./tests/ui",
  outputDir: "reports/test-results",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ["list"],
    ["html", { outputFolder: "reports/playwright-report", open: "never" }],
  ],
  use: {
    baseURL: process.env.PLANE_BASE_URL || undefined,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    // Auth setup — runs first, saves storage state, covers UI-001
    {
      name: "setup",
      testMatch: /auth\.setup\.ts/,
    },
    // Standalone login tests — NO dependency, NO storageState
    {
      name: "chromium-login",
      testMatch: /login\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
      },
    },
    // Authenticated tests — depend on auth setup
    {
      name: "chromium",
      testIgnore: /login\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: ".playwright/auth-state.json",
      },
      dependencies: ["setup"],
    },
  ],
});
