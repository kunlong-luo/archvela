# Alpha — upstream license-source triage for six installed-package exceptions

> **Evidence classification: upstream sources identified; actual npm tarballs and distributable output NOT cleared.**
> Checked 2026-11-01 against `main` at `0934a18e7266914224c5bcd3faed2727b729f240`. This document adds a second, **source-level** review to the ten observed package-root gaps in [LICENSE-EVIDENCE-EXCEPTIONS.md](./LICENSE-EVIDENCE-EXCEPTIONS.md). It is **not a legal opinion, a six-package sign-off or permission to tag/release**.

## Scope and separation of evidence

The archived [CI evidence register](./INSTALLED-LICENSE-EXCEPTIONS.json) lists **10 missing package-root LICENSE/NOTICE observations, representing six distinct exact package versions** in two Next.js and one Vite starter. The original reports used Linux x64, Node 24, and `npm ci --ignore-scripts`; browser-tests had zero such exceptions. Those observations describe **absence of scanner-recognized filenames at an installed package root**, not a finding that the package has no license, that the original package archive lacks all notices, or that a shipped product is noncompliant.

The primary sources below were read **at version-tagged upstream paths**, where available, and the npm package pages were checked for the published license declaration. No original npm `.tgz` bytes, `npm pack` manifest, server deployment image or Vite `dist/` has been independently downloaded/inspected during this source-triage step. No package copyright attribution should be guessed from an adjacent repository.

## Verified upstream evidence and remaining questions

| Exact npm package | Current source-level result | Exact source checked | What remains unresolved |
| --- | --- | --- | --- |
| `@img/sharp-libvips-linux-x64@1.3.4` | npm declares **LGPL-3.0-or-later** for the Linux binary package. Its upstream `v1.3.4` README says the packaging **scripts** use Apache-2.0 while shipped shared libraries have their **own multiple licenses**; the release-tagged third-party notice table includes LGPL, MPL, BSD, MIT and other entries. This is **not** a simple Apache-only package. | [npm package](https://www.npmjs.com/package/%40img/sharp-libvips-linux-x64) · [v1.3.4 README](https://github.com/lovell/sharp-libvips/blob/v1.3.4/README.md) · [v1.3.4 third-party notices](https://github.com/lovell/sharp-libvips/blob/v1.3.4/THIRD-PARTY-NOTICES.md) · [packaging-scripts LICENSE](https://github.com/lovell/sharp-libvips/blob/v1.3.4/LICENSE) | **HIGH:** identify exact bundled shared libraries/versions and applicable source, modification, replacement/relinking and notice obligations for any redistribution of the Linux binary. Inspect `1.3.4` tarball and actual server/image payload; upstream table alone is insufficient. |
| `@next/env@16.4.3` | npm and release-tagged `packages/next-env/package.json` declare **MIT**. The `v16.4.3` upstream Next.js `license.md` contains the MIT license and Vercel copyright. This establishes an upstream license source, **not** license-file inclusion in the independently published npm archive. | [npm package](https://www.npmjs.com/package/%40next/env) · [v16.4.3 package manifest](https://github.com/vercel/next.js/blob/v16.4.3/packages/next-env/package.json) · [v16.4.3 license](https://github.com/vercel/next.js/blob/v16.4.3/license.md) | Check exact npm archive files and attribution in any distributed Next server/app package. |
| `@next/swc-linux-x64-gnu@16.4.3` | npm declares **MIT** and describes this as the Linux GNU native SWC binary for Next.js. The `v16.4.3` Next.js MIT license is available upstream; `packages/next-swc/package.json` documents native Rust/N-API builds. That does **not** inventory separately licensed native components. | [npm package](https://www.npmjs.com/package/%40next/swc-linux-x64-gnu) · [v16.4.3 license](https://github.com/vercel/next.js/blob/v16.4.3/license.md) · [v16.4.3 native build manifest](https://github.com/vercel/next.js/blob/v16.4.3/packages/next-swc/package.json) | Verify exact `.node` binary, embedded third-party notices and whether the compiler is shipped or only used at build time. |
| `client-only@0.0.1` | npm declares **MIT**. The archived Linux install found no recognized package-root notice. **No authoritative package-specific copyright line has been established in this review**. In particular, do not fabricate a Vercel/Meta copyright notice from publisher associations. | [npm package](https://www.npmjs.com/package/client-only) · [public provenance discussion, secondary/unverified](https://github.com/vercel/next.js/discussions/99484) | Inspect the `0.0.1` tarball and npm metadata for actual copyright/license text; request confirmation from the original publisher where required. Keep copyright-holder field **unknown/unverified**, not inferred. |
| `@react-three/fiber@9.8.2` | npm declares **MIT**. The repository `v9.8.2` tag contains the Poimandres MIT LICENSE. **Version-mapping caveat:** `packages/fiber/package.json` at this same tag still says **9.8.1**, not 9.8.2; a tag by itself cannot establish byte-level or exact-manifest equivalence to the published `9.8.2` npm archive. | [npm package](https://www.npmjs.com/package/%40react-three/fiber) · [v9.8.2 LICENSE](https://github.com/pmndrs/react-three-fiber/blob/v9.8.2/LICENSE) · [v9.8.2 package manifest](https://github.com/pmndrs/react-three-fiber/blob/v9.8.2/packages/fiber/package.json) | Compare exact npm `9.8.2` tarball to the release source/build and verify license text accompanies the relevant bundled client code/attribution. |
| `@rolldown/binding-linux-x64-gnu@1.2.15` | npm declares **MIT**; the exact upstream `v1.2.15` LICENSE attributes VoidZero & contributors. The same release tag contains a separate `THIRD-PARTY-LICENSE` with Rollup/esbuild notices. This is a native binding present as **development + optional** in the archived Linux lockfile; those flags are not a waiver for binaries redistributed later. | [npm package](https://www.npmjs.com/package/%40rolldown/binding-linux-x64-gnu) · [v1.2.15 LICENSE](https://github.com/rolldown/rolldown/blob/v1.2.15/LICENSE) · [v1.2.15 THIRD-PARTY-LICENSE](https://github.com/rolldown/rolldown/blob/v1.2.15/THIRD-PARTY-LICENSE) | Compare npm archive and any native binding in shipped deliverables; determine whether build tool is omitted from the static Vite artifact and carry applicable notices for any distributed copy. |

**Status for all six:** `upstream_license_source_located_or_declaration_recorded`; `npm_tarball_verified=false`; `delivered_payload_verified=false`; `rights_cleared=false`. Upstream source identification does not supersede the separate [42-entry unusual SPDX review](./DEPENDENCY-LICENSE-AUDIT.md).

## Actual Archvela delivery scenarios to verify

At this source SHA, `examples/cinematic-site` and `examples/saas-workspace` are **Next.js 16.4.3 server-based examples** (`next build`, `next start`). `examples/home-digital-twin` is a **Vite 8.3.5** example (`vite build`) whose `@react-three/fiber@9.8.2` dependency is listed under runtime `dependencies`, while Rolldown is observed as a transitive development/optional native binding. All example packages are marked `private: true`. These facts describe source manifests, **not** a verified production deliverable or automatic notice exemption.

1. **Source-only GitHub / generated starter:** decide whether the recipient receives only source + lockfile or also downloaded dependencies, vendored/bundled code, scripts or binary files. Preserve a dependency attribution record for recipients building the code.
2. **Next.js server/container deployment:** build from the exact release SHA, enumerate the actual `.next/`, `node_modules/` and container/image layers (if any), and check whether `@img/sharp-libvips-linux-x64`, `@next/env`, `@next/swc-linux-x64-gnu`, and `client-only` are present in the redistributable payload. A package being installed in CI **does not show** it is shipped.
3. **Vite web `dist/`:** inspect emitted JS chunks, source maps and any files shipped with the client build; determine inclusion of the R3F implementation. Inspect a deployed image/archive separately if it also contains `node_modules`/native build tooling.
4. **Other OS/CPU targets:** the original Linux x64 run does not inspect optional macOS, Windows, ARM or musl archives. Re-run for each actual target or explicitly document the distribution scope.

## Reproducible manual tarball / notice checklist

Use a **disposable, empty** workspace with Node 24, and one of the exact package specifiers listed above (not `latest`). Example:

```bash
set -euo pipefail
work="$(mktemp -d)"
npm pack --ignore-scripts --json --pack-destination "$work" '@react-three/fiber@9.8.2' > "$work/pack.json"
python3 - "$work/pack.json" <<'PY'
import json, sys
for entry in json.load(open(sys.argv[1], encoding="utf-8")):
    print("name:", entry["name"], "version:", entry["version"])
    print("integrity:", entry.get("integrity"), "filename:", entry["filename"])
    for f in entry["files"]:
        print(f["path"])
PY
sha256sum "$work"/*.tgz
tar -tzf "$work"/*.tgz
```

Retain the tarball SHA-256, registry integrity, actual filename list, precise `LICENSE`/`NOTICE`/nested paths, package-specific copyright evidence, relevant native binary inventory and the output artifact manifest. Compare the npm integrity with the **committed lockfile** rather than substituting upstream HEAD. For `client-only`, record missing or uncertain copyright attribution as such; do **not** create an unverified copyright line. Never copy a different package's license text into a binary archive as an assumed cure.

## Explicit approval barrier

- [x] Exact six unique exceptions grouped from ten historical Linux installation observations.
- [x] Release-tagged **upstream** license sources examined for Next.js, Poimandres, Rolldown, and sharp-libvips (with the package/source distinction documented).
- [ ] Download and hash all **six exact npm archives** and inspect nested files and binary notices; reconcile the Poimandres tag/manifest version discrepancy.
- [ ] Build and independently inventory actual **intended shipping artifacts** on each applicable target, then determine notices/obligations for those exact outputs.
- [ ] Complete the wider 42 flagged SPDX review plus original V3 source rights checks.
- [ ] Obtain a documented **authorized human rights/redistribution decision** tied to the final release SHA.

**Release decision: HOLD.** See [Rights Review Register](./RIGHTS-REVIEW-REGISTER.md), [Issue #5](https://github.com/kunlong-luo/archvela/issues/5) and [Alpha checklist](./ALPHA-RELEASE-CHECKLIST.md). A source-level triage commit or green CI must never change `rights_cleared` to `true`.
