"use client";

import { useDocuments } from "@/lib/api/knowledge";
import { DocumentTable } from "@/components/knowledge-base/document-table";
import { documentColumns } from "@/components/knowledge-base/document-columns";
import { UploadModal } from "@/components/knowledge-base/upload-modal";
import { KnowledgeHealthPanel } from "@/components/knowledge-base/knowledge-health";
import { KnowledgeSearch } from "@/components/knowledge-base/knowledge-search";
import { KnowledgeAnalytics } from "@/components/knowledge-base/knowledge-analytics";
import { SearchAnalyticsPanel } from "@/components/knowledge-base/search-analytics";
import { DocumentTableSkeleton } from "@/components/knowledge-base/skeletons";
import { ErrorState, EmptyState } from "@/components/ui/empty-state";
import { AlertCircle, FileX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ErrorBoundary } from "react-error-boundary";

import { RAGTester } from "@/components/knowledge-base/rag-tester";

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <ErrorState 
      title="Failed to load section" 
      message={error.message} 
      onRetry={resetErrorBoundary} 
    />
  );
}

export default function KnowledgeBasePage() {
  const { data: documents, isLoading, isError, refetch } = useDocuments();

  return (
    <div className="flex flex-col gap-8 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-muted-foreground">
            Manage the documents and URLs that your AI agents use to answer questions.
          </p>
        </div>
        <div className="flex items-center gap-4 flex-1 justify-end">
          <KnowledgeSearch />
          <UploadModal />
        </div>
      </div>

      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <KnowledgeHealthPanel />
      </ErrorBoundary>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <ErrorBoundary FallbackComponent={ErrorFallback}>
            <SearchAnalyticsPanel />
          </ErrorBoundary>

          <ErrorBoundary FallbackComponent={ErrorFallback}>
            <KnowledgeAnalytics />
          </ErrorBoundary>
        </div>

        <div className="lg:col-span-1">
          <ErrorBoundary FallbackComponent={ErrorFallback}>
            <RAGTester />
          </ErrorBoundary>
        </div>
      </div>

      <div className="flex flex-col gap-4 mt-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight">Document Library</h2>
        </div>
        
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          {isLoading ? (
            <DocumentTableSkeleton />
          ) : isError ? (
            <ErrorState 
              title="Failed to load documents" 
              message="Check your connection or try again." 
              onRetry={() => refetch()} 
            />
          ) : !documents || documents.length === 0 ? (
            <EmptyState 
              title="No documents found" 
              description="You haven't added any knowledge to this workspace yet."
            />
          ) : (
            <DocumentTable data={documents} columns={documentColumns} />
          )}
        </ErrorBoundary>
      </div>
    </div>
  );
}
