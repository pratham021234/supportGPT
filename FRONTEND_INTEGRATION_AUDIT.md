# Frontend Integration Audit

## Overview
The frontend is built with Next.js (App Router), Tailwind CSS, Shadcn UI, Zustand, and TanStack Query.
Currently, almost all components display hardcoded data arrays and dummy logic instead of communicating with the backend APIs.

## Areas to Integrate

### 1. Authentication
**Current State**: Uses a Zustand store (`src/store/authStore.ts`) with dummy `login` and `logout` actions.
**To Implement**: 
- `api-client.ts` with Axios/Fetch and interceptors.
- Replace Zustand dummy functions with `useMutation` (TanStack Query) calling `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/refresh`.
- Handle JWT tokens securely (localStorage/cookies for refresh, memory for access).
- Implement global error boundaries for unauthorized states.

### 2. Dashboard
**Current State**: `src/app/dashboard/page.tsx` and `src/components/dashboard/overview-charts.tsx` use hardcoded KPI values and static arrays for Recharts and "Recent Conversations".
**To Implement**:
- Build `analytics-client.ts`.
- Fetch `total conversations`, `AI resolution rate`, `knowledge sources`, and `active tickets` from backend.
- Replace Recharts data with live metric aggregations.

### 3. Knowledge Base, Agents, Conversations, Tickets
**Current State**: Likely similar to Dashboard—built with dummy data arrays.
**To Implement**:
- Build dedicated clients (`knowledge-client.ts`, `agent-client.ts`, `conversation-client.ts`, `ticket-client.ts`).
- Integrate React Query (`useQuery`, `useMutation`) for data fetching, caching, and optimistic updates.
- Create Skeleton loaders for all lists/tables.
- Provide proper Empty states (e.g. "No documents found").

### 4. Websockets / Real-time
**Current State**: Missing.
**To Implement**:
- Central `src/lib/websocket/` hook to handle live connections for notifications and agent typing indicators.

## Plan Summary
We will create a structured API layer, replace all `const data = [...]` with `const { data, isLoading } = useQuery(...)`, and ensure proper loading/empty/error states using Shadcn components.
