import { test, expect } from "@playwright/test";

test("2D proportional plan and truthful precision disclosures are visible", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /住宅空间概览/i })).toBeVisible();
  await expect(page.getByRole("img", { name: "宅基地与主屋平面比例示意" })).toBeVisible();
  await expect(page.getByText("11.20 × 8.40 m", { exact: true }).first()).toBeVisible();
  await expect(page.getByText(/非施工图、非实测 BIM 模型/)).toBeVisible();
  await expect(page.getByRole("button", { name: "平面", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("canvas")).toHaveCount(0);
});

test("WebGL disabled: 3D cannot replace the scaled accessible plan", async ({ page }) => {
  await page.addInitScript(() => {
    const getContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (...args) {
      if (args[0] === "webgl" || args[0] === "webgl2" ||
          args[0] === "experimental-webgl") return null;
      return getContext.apply(this, args);
    } as typeof getContext;
  });
  await page.goto("/");
  await page.getByRole("button", { name: "三维", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: /未提供 WebGL/i })).toBeVisible();
  await expect(page.getByRole("img", { name: "宅基地与主屋平面比例示意" })).toBeVisible();
  await expect(page.locator("canvas")).toHaveCount(0);
});

test("plan/3D controls function where software WebGL is available", async ({ page }) => {
  await page.goto("/");
  const supported = await page.evaluate(() => {
    try {
      const c = document.createElement("canvas");
      return Boolean(c.getContext("webgl2") || c.getContext("webgl"));
    } catch { return false; }
  });
  test.skip(!supported, "No WebGL context in this CI/browser (explicit unsupported environment)");
  await page.getByRole("button", { name: "三维", exact: true }).click();
  await expect(page.getByRole("button", { name: "二层" })).toBeVisible();
  await page.getByRole("button", { name: "二层" }).click();
  await expect(page.getByRole("button", { name: "二层" })).toHaveClass(/on/);
  const slider = page.getByRole("slider", { name: /视角旋转角度/i });
  await slider.fill("45");
  await expect(slider).toHaveValue("45");
  await page.getByRole("button", { name: "平面", exact: true }).click();
  await expect(page.getByRole("img", { name: "宅基地与主屋平面比例示意" })).toBeVisible();
});
