# Security policy

## Supported versions

This repository is an **application monorepo** under active development. Security fixes land on the default branch (`main`) as regular commits; there is no separate LTS line yet.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for undisclosed security problems.

Instead, email the repository maintainers with:

- A short description of the impact
- Steps to reproduce (or a proof-of-concept) if safe to share
- Affected components (`apps/api`, `apps/web`, worker, infra, etc.)

We aim to acknowledge reports within a few business days.

## Out of scope (typical)

- Social engineering against maintainers or users
- Denial-of-service that requires overwhelming shared infrastructure without a clear software defect
- Issues in third-party dependencies without a practical upgrade path in this repo

## Secure development notes

- Treat **`JWT_SECRET`**, **`INTERNAL_API_KEY`**, and database credentials as production secrets.
- Never commit `.env` files or real tokens.
- Browser demos store JWTs in **`sessionStorage`**; they are suitable for local demos, not for high-assurance production UX without additional hardening.
