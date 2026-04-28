# Copilot Instructions for bottle-buddy-bot

## Project Overview
- **Type:** Vite + React + TypeScript SPA
- **UI:** shadcn-ui, Tailwind CSS
- **State/Async:** React Query (`@tanstack/react-query`)
- **Routing:** React Router DOM
- **Purpose:** Interactive bottle recycling dashboard with real-time stats, controls, and settings.

## Key Architecture & Patterns
- **Entry Point:** `src/main.tsx` mounts `App.tsx`.
- **App Structure:**
  - `App.tsx` sets up providers (React Query, Tooltip, Toasters) and routes.
  - Pages in `src/pages/` (e.g., `Index.tsx`, `Settings.tsx`, `NotFound.tsx`).
  - UI split into feature folders: `components/recycling/` (domain-specific), `components/ui/` (reusable UI primitives).
  - State and logic hooks in `src/hooks/` (e.g., `useRecyclingMachine.ts`).
- **Type Definitions:** Centralized in `src/types/` (e.g., `recycling.ts`).
- **Utilities:** Shared helpers in `src/lib/utils.ts`.
- **Styling:** Tailwind config in `tailwind.config.ts`, global styles in `src/index.css` and `src/App.css`.
- **Component Imports:** Use `@` alias for `src/` (see `vite.config.ts`).

## Developer Workflow
- **Install:** `npm install`
- **Dev Server:** `npm run dev` (default: http://localhost:8080)
- **Build:** `npm run build`
- **Lint:** ESLint config in `eslint.config.js` (uses TypeScript, React Hooks, and React Refresh plugins)
- **UI Components:** Prefer shadcn-ui patterns for new UI; see `components/ui/` for examples.
- **Routing:** Add new routes in `App.tsx` above the catch-all `*` route.
- **State Management:** Use React Query for async data; use hooks for local state.
- **Testing:** No explicit test setup found—add tests in `src/` if needed.

## Conventions & Integration
- **Component Structure:**
  - Domain components: `components/recycling/`
  - UI primitives: `components/ui/` (Radix UI + shadcn-ui conventions)
  - Use `className` and `cn()` utility for styling overrides.
- **Icons:** Use `lucide-react` for icons.
- **External Integrations:**
  - `lovable-tagger` plugin in Vite for component tagging (dev mode only).
  - Project is designed for [Lovable](https://lovable.dev/) platform but works locally.
- **Aliases:** Use `@` for imports from `src/` (e.g., `import { cn } from '@/lib/utils'`).

## Examples
- **Adding a Page:** Create a file in `src/pages/`, add a `<Route />` in `App.tsx`.
- **Creating a UI Component:** Follow patterns in `components/ui/`, export with `displayName`.
- **Domain Logic:** Place hooks in `src/hooks/`, types in `src/types/`.

## References
- [vite.config.ts](../vite.config.ts): Vite, alias, plugin setup
- [App.tsx](../src/App.tsx): Providers, routing
- [tailwind.config.ts](../tailwind.config.ts): Theme, colors, fonts
- [README.md](../README.md): Setup, deployment, tech stack

---
For more details, see the referenced files and follow the established folder structure and patterns. If unsure, mimic the style of existing components and hooks.