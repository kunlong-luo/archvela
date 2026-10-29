import test from "node:test";
import assert from "node:assert/strict";
import { filterIncidents, seedIncidents, summarizeIncidents } from "../src/domain/operations.ts";

test("sample incident totals are consistent", () => {
  const total = summarizeIncidents(seedIncidents);
  assert.equal(total.total, 6);
  assert.equal(total.open + total.resolved, total.total);
  assert.equal(total.critical, 2);
});
test("query, status and no-result filters are deterministic", () => {
  assert.deepEqual(filterIncidents(seedIncidents, "stream hub", "all").map(x => x.id), ["OPS-1042", "OPS-1038"]);
  assert.deepEqual(filterIncidents(seedIncidents, "ops-1040", "resolved").map(x => x.id), ["OPS-1040"]);
  assert.equal(filterIncidents(seedIncidents, "nonexistent", "all").length, 0);
});
