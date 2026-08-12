# Frontend API Audit

## Audit Findings

This audit identifies where the frontend is relying on mock data architectures or sub-optimal fetch wrappers that need to be migrated to the new enterprise-grade Axios + TanStack Query layer.

### 1. `src/app/dashboard/page.tsx` (Dashboard Overview)
- **Mock Data Found**: Calls to `analyticsClient.getStats()`, `getRecentConversations()`, `getSystemStatus()`.
- **Current State**: Currently utilizing a primitive `api-client.ts` fetch wrapper that lacks robust error handling and token refresh logic.
- **Replacement API**: Replace with `useDashboard()` hook powered by Axios interceptors.
- **Priority**: High

### 2. `src/app/dashboard/conversations/page.tsx`
- **Mock Data Found**: Calls to `conversationClient.getConversations()`.
- **Current State**: Primitive client with hardcoded fallback types.
- **Replacement API**: `useConversations()` hook.
- **Priority**: High

### 3. `src/app/dashboard/agents/page.tsx`
- **Mock Data Found**: Calls to `agentClient.getAgents()`.
- **Current State**: Basic fetch wrapper handling list responses, lacks mutation support for "Create Agent".
- **Replacement API**: `useAgents()` hook (queries and mutations).
- **Priority**: High

### 4. `src/lib/api/api-client.ts`
- **Current State**: Naive `fetch` implementation manually pulling tokens from `localStorage` (`auth-storage`). Does not handle token refresh gracefully on 401s.
- **Replacement**: Deprecate this file in favor of a new Axios Singleton (`src/lib/api/client.ts`) with request/response interceptors to securely handle token refresh cycles via the Zustand store.
- **Priority**: Critical

## Conclusion
The frontend currently has the UI and pages built out using `@tanstack/react-query`, but the underlying API clients are primitive stubs. We must replace the foundation with a structured Axios architecture before we update the components to use it.
