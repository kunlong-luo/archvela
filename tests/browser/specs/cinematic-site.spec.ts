import { test, expect } from "@playwright/test";

test("story and poster are available before requesting 3D", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Design that.*purpose/i })).toBeVisible();
  await expect(page.getByText("WEBGL LOADED ON REQUEST")).toBeVisible();
  await expect(page.locator("canvas.stage-canvas")).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Explore in 3D/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /See the study/i })).toBeVisible();
});

test("GPU unavailable: 3D is optional and static page remains functional", async ({ page }) => {
  await page.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (...args) {
      if (args[0] === "webgl" || args[0] === "webgl2" ||
          args[0] === "experimental-webgl") return null;
      return original.apply(this, args);
    } as typeof original;
  });
  await page.goto("/");
  await page.getByRole("button", { name: /Explore in 3D/i }).click();
  await expect(page.getByRole("status").filter({ hasText: /3D is unavailable/i })).toBeVisible();
  await page.getByRole("button", { name: "Close preview" }).click();
  await expect(page.getByRole("button", { name: /Explore in 3D/i })).toBeVisible();
  await expect(page.locator("canvas.stage-canvas")).toHaveCount(0);
});

test("mobile layout does not introduce horizontal page scrolling", async ({ page }, testInfo) => {
  test.skip(!testInfo.project.name.startsWith("mobile"), "Mobile-only check");
  await page.goto("/");
  await expect(page.locator("header .wordmark")).toBeVisible();
  const overflow = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth
  }));
  expect(overflow.content).toBeLessThanOrEqual(overflow.viewport + 3);
});
