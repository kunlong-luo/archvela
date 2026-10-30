# Asset provenance and redistribution review

> **Status: PARTIAL INVENTORY; THIRD-PARTY RIGHTS REVIEW REMAINS OPEN.**
> Audited 2026-10-30 against the repository's tracked-file tree at
> `6b253839758f3ab881731be961e7a929b04545ec`.

## Current observed media inventory

The GitHub source tree had **0 separately committed raster images, SVG files,
font files, videos, audio files, GLB/GLTF models or PDF documents**. Current
front-end examples use source-authored markup, CSS, inline SVG and procedural
Three.js/React Three Fiber geometry; example content is fictional. This
inventory says **nothing** about ownership of source text, embedded code,
inline vector designs, product/trademark names, quoted or adapted reference
guides, screenshots, remote assets, and npm dependencies.

The machine-checkable [asset manifest](./ASSET-PROVENANCE.json) is empty
because no standalone media files were observed. It is not a statement that
the entire project has completed copyright clearance.

## Media asset gate

Run:

```bash
python3 scripts/check_asset_provenance.py
```

This inventories standalone PNG/JPEG/WebP/AVIF/GIF/SVG, 3D files, fonts,
audio, video and PDF assets. New or removed files fail validation unless
`docs/ASSET-PROVENANCE.json` is updated and reviewed. The checker requires
a per-file record:

```json
{
  "path": "examples/example/public/media/illustration.svg",
  "origin": "original",
  "rights_holder": "The person or organization granting rights",
  "license": "MIT or exact third-party license identifier",
  "source": "Local design source or authoritative asset URL",
  "attribution": "Text required for redistribution, or explicit 'none'",
  "reviewed_on": "2026-10-30",
  "redistribution_approved": true
}
```

**Do not add this sample record unless a corresponding actual file exists.**
Do not set `redistribution_approved` to true until a human has verified
authorship, license terms, attribution obligations and redistribution scope.

Automated file matching cannot certify license authenticity. The tool skips
third-party installed npm packages and transient build output; dependencies
have their own package licenses and npm audits do **not** constitute copyright
clearance.

## Manual review required before a Release

- [ ] Inspect the full six-domain V3 reference collection for copied/adapted
  third-party text, tables, screenshots, diagrams, official specifications,
  translated material, and compatibility claims.
- [ ] Review source-authored SVG/JSX/CSS, procedural 3D examples and copied
  snippets for ownership and derivative-work concerns, not only media files.
- [ ] Verify npm dependency license obligations and bundling restrictions for
  every generated starter; record an SBOM or license report.
- [ ] Review trademarks and branding: do not imply endorsement by AI coding
  client or framework vendors.
- [ ] Verify date/version claims against official documentation and track
  last-checked dates for technology choices.
- [ ] Have the repository copyright owner review the full audit and sign off
  prior to any tag/Release.

Track incomplete work in [Issue #5](https://github.com/kunlong-luo/archvela/issues/5)
and [Release Readiness](./RELEASE-READINESS.md). MIT only licenses content
the contributor actually has rights to license.
