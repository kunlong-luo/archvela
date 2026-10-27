import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

const choices = ["cinematic-site", "saas-workspace", "home-digital-twin"] as const;
const example = process.env.ARCHVELA_EXAMPLE;
if (!example || !choices.some(choice => choice === example)) {
  throw new Error("Set ARCHVELA_EXAMPLE to " + choices.join(", "));
}
const root = path.resolve(__dirname, "../../examples", example);
const port = 4180;
const origin = "http://127.0.0.1:" + port;

export default defineConfig({
  testDir: "./specs",
  testMatch: "**/" + example + ".spec.ts",
  timeout: 40_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: process.env.CI ? 1 : undefined,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "./playwright-report" }]
  ],
  outputDir: "./test-results",
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } },
    { name: "mobile-chromium", use: { ...devices["Pixel 7"], browserName: "chromium" } }
  ],
  use: {
    baseURL: origin,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    launchOptions: {
      args: ["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"]
    }
  },
  webServer: {
    command: example === "home-digital-twin"
      ? "npm run preview -- --host 127.0.0.1 --port 4180"
      : "npm run start -- -p 4180",
    cwd: root,
    url: origin,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: "ignore",
    stderr: "pipe"
  }
});
