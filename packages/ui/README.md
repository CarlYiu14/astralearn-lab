# Shared UI (`packages/ui`)

## Why it looks “empty”

This monorepo **front-loads** `apps/web` (Next.js App Router demos). A separate `packages/ui` folder is reserved for **later extraction** when you have **two or more** frontends (e.g. `apps/web` + `apps/instructor-portal`) or you want to publish a private component library.

Typical contents (future):

- Design tokens (CSS variables or JSON → Style Dictionary)
- Headless primitives (Radix/shadcn wrappers) shared across apps
- Storybook or Ladle for visual regression

Until then, keeping only this README avoids pretending there is a second app to maintain.

## When to populate

Add real files when either:

1. You split a second Next.js app under `apps/`, or  
2. You promote 3+ duplicated components from `apps/web` into shared building blocks.
