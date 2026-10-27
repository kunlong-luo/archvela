# Browser acceptance suite

Playwright Test pinned to **1.64.1**, running bundled Chromium against **locally built application servers** (not real deployments).

## Run from repo root

```bash
npm install --prefix tests/browser
npm exec --prefix tests/browser -- playwright install chromium

for app in cinematic-site saas-workspace home-digital-twin; do
  npm install --prefix "examples/$app"
  npm run build --prefix "examples/$app"
  ARCHVELA_EXAMPLE="$app" npm test --prefix tests/browser
done
```

Tests run for desktop Chromium and a Pixel 7 mobile emulation profile. They assert browser UI behavior, plus a controlled WebGL-unavailable fallback. Chromium's software GL is only a **smoke environment**, not a mobile GPU benchmark or evidence of correctly rendered architectural geometry.

**Do not overclaim:** Real devices, keyboard/screen reader UX, offline stress, performance budget, building geometry sign-off, agent-model inference and Safari/Firefox are NOT proven by these tests. Failure artifacts include trace/video/screenshots; E2E invokes only local servers with demo fixtures.
