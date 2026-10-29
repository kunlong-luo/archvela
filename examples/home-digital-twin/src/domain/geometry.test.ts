import assert from "node:assert/strict";
import test from "node:test";
import { areaM2, dimensions, fitsWithinRect, houseAreaM2, plotAreaM2 } from "./geometry.ts";

test("house footprint follows 11.20 by 8.40 input", () => {
  assert.equal(houseAreaM2, 94.08);
  assert.equal(areaM2(11.2, 8.4), 94.08);
});
test("site area and footprint consistency", () => {
  assert.equal(plotAreaM2, 210);
  assert.ok(fitsWithinRect(dimensions.plotWidthM, dimensions.plotDepthM, dimensions.houseWidthM, dimensions.houseDepthM));
  assert.equal(fitsWithinRect(15, 14, 16.3, 8.4), false);
});
test("invalid dimensions do not silently pass", () => {
  assert.throws(() => areaM2(0, 3));
  assert.throws(() => areaM2(-1, 4));
});
