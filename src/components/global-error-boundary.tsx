"use client";

import { ErrorBoundary } from "react-error-boundary";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

function Fallback({ error, resetErrorBoundary }: { error: any; resetErrorBoundary: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950 p-4">
      <div className="max-w-md w-full bg-white dark:bg-zinc-900 rounded-xl shadow-xl border border-zinc-200 dark:border-zinc-800 p-8 text-center">
        <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
        <p className="text-zinc-500 dark:text-zinc-400 mb-6">
          An unexpected error occurred. Our team has been notified.
        </p>
        <div className="bg-zinc-100 dark:bg-zinc-950 rounded-md p-4 mb-6 text-left overflow-auto text-sm font-mono text-zinc-700 dark:text-zinc-300">
          {error.message}
        </div>
        <Button onClick={() => window.location.reload()} className="w-full" size="lg">
          <RefreshCcw className="w-4 h-4 mr-2" />
          Reload Application
        </Button>
      </div>
    </div>
  );
}

export function GlobalErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary FallbackComponent={Fallback}>
      {children}
    </ErrorBoundary>
  );
}
