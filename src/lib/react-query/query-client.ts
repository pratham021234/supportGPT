import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // Data is fresh for 5 minutes
      gcTime: 1000 * 60 * 30, // Data remains in cache for 30 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 401, 403, 404
        if (error?.response?.status === 401 || error?.response?.status === 403 || error?.response?.status === 404) {
          return false;
        }
        return failureCount < 3; // Otherwise retry up to 3 times
      },
      refetchOnWindowFocus: true, // Enterprise SaaS standard: refetch when user comes back
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1, // Only retry mutations once to avoid side-effects
    },
  },
});
