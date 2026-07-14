/**
 * UI Test Data Factory
 * Generates unique, traceable test data for UI automation
 * Pattern: AUTO-D3-UI-{utc-timestamp}
 */
export function generateWorkItemTitle(): string {
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  return `AUTO-D3-UI-${ts}`;
}

export function generateDescription(): string {
  return `UI automation test description — created at ${new Date().toISOString()}`;
}

export function isAutoTestData(title: string): boolean {
  return /^AUTO-D3[-_]/.test(title);
}
