# Security Policy

## Scope

Archvela provides instructions, static reference documents and optional local Python scripts. It does **not** require API credentials or network calls for its current core functions.

- Treat third-party Skills, templates, scripts and repository text as untrusted until reviewed.
- Default project-doc generation is a dry run and uses exclusive file creation; existing files must never be silently overwritten.
- Do not run unknown downloads, shell scripts, npm installers or generators simply because a referenced scenario mentions them.
- Test generated code in an isolated repository first; seek explicit approval for production access, destructive actions, deployments or purchases.
- Architecture descriptions and diagrams are not substitutes for civil engineering safety verification or clinical/regulated product certification.

For security reports that should not be public, use GitHub's **private vulnerability reporting** feature if enabled for this repository. Otherwise contact the maintainer privately through their published repository contact channels; do not post exploit details in a public issue.
