import { test, expect } from "@playwright/test";

test("sample incident workflow: filter, update, resolve and reset", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Good afternoon/i })).toBeVisible();
  await expect(page.getByText("DEMO DATA · NO BACKEND")).toBeVisible();
  const search = page.getByRole("searchbox", { name: "Search incident records" });
  await search.fill("Stream Hub");
  await expect(page.getByRole("row").filter({ hasText: "OPS-1042" })).toBeVisible();
  await expect(page.getByRole("row").filter({ hasText: "OPS-1038" })).toBeVisible();
  await expect(page.getByText("2 results")).toBeVisible();
  await page.getByRole("combobox", { name: /Status/i }).selectOption("new");
  await expect(page.getByText("1 result", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Start", exact: true }).click();
  await expect(page.getByText("No matching incidents")).toBeVisible();
  await page.getByRole("combobox", { name: /Status/i }).selectOption("investigating");
  await expect(page.getByRole("row").filter({ hasText: "OPS-1042" })).toBeVisible();
  await page.getByRole("button", { name: "Resolve", exact: true }).first().click();
  await expect(page.getByRole("row").filter({ hasText: "OPS-1042" })).toHaveCount(0);
  await page.getByRole("button", { name: /Reset sample/i }).click();
  await expect(page.getByText("6 results")).toBeVisible();
});

test("on-demand insights can be opened and hidden", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Service distribution" })).toHaveCount(0);
  await page.getByRole("button", { name: /Load breakdown/i }).click();
  await expect(page.getByRole("heading", { name: "Service distribution" })).toBeVisible();
  await page.getByRole("button", { name: /Hide breakdown/i }).click();
  await expect(page.getByRole("heading", { name: "Service distribution" })).toHaveCount(0);
});

test("empty results remain accessible", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("searchbox", { name: "Search incident records" }).fill("xyz--never--matches");
  await expect(page.getByRole("status").filter({ hasText: /No matching incidents/i })).toBeVisible();
});
