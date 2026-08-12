"use client";

import { useDocument } from "@/lib/api/knowledge";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowLeft, FileText, Globe, File, Calendar, Database, Activity } from "lucide-react";
import Link from "next/link";
import { ErrorBoundary } from "react-error-boundary";

export default function DocumentDetailsPage() {
  const params = useParams();
  const documentId = params.id as string;
  const { data: document, isLoading, isError } = useDocument(documentId);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <Skeleton className="h-[400px] md:col-span-2" />
          <Skeleton className="h-[400px]" />
        </div>
      </div>
    );
  }

  if (isError || !document) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border rounded-lg bg-destructive/5 text-destructive">
        <Activity className="h-12 w-12 mb-4" />
        <h3 className="text-lg font-semibold">Document Not Found</h3>
        <p className="text-muted-foreground mb-4">The document you're looking for doesn't exist or you don't have access.</p>
        <Button asChild variant="outline">
          <Link href="/dashboard/knowledge-base">Back to Knowledge Base</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 pb-10">
      <div className="flex items-center gap-4">
        <Button asChild variant="outline" size="icon" className="shrink-0">
          <Link href="/dashboard/knowledge-base">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{document.title}</h1>
            <Badge variant="outline" className="capitalize">{document.status.toLowerCase()}</Badge>
          </div>
          <p className="text-muted-foreground text-sm flex items-center gap-2 mt-1">
            <span className="capitalize">{document.file_type || (document.source_id ? "Website" : "FAQ")}</span>
            <span>•</span>
            <span>Version {document.version}</span>
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Document Preview</CardTitle>
              <CardDescription>Content extracted from the source</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted/30 border rounded-md p-6 h-[500px] overflow-auto text-sm leading-relaxed whitespace-pre-wrap font-mono">
                {/* Mocking actual document content extraction UI */}
                {document.file_type === "FAQ" ? (
                  "Question: " + document.title + "\n\nAnswer: (FAQ Answer loaded here)"
                ) : (
                  "Content preview is currently being generated. In a production environment, the extracted chunks or raw text is displayed here."
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><Calendar className="h-4 w-4" /> Date Added</span>
                <span className="text-sm">{new Date(document.created_at).toLocaleString()}</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><Database className="h-4 w-4" /> Vector Chunks</span>
                <span className="text-sm">Processed into 12 chunks</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><FileText className="h-4 w-4" /> Size</span>
                <span className="text-sm">{document.file_size ? `${(document.file_size / 1024).toFixed(2)} KB` : 'N/A'}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Processing History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative border-l border-muted ml-3 space-y-6">
                <div className="relative pl-6">
                  <span className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-background" />
                  <p className="text-sm font-medium text-emerald-600">Processing Completed</p>
                  <p className="text-xs text-muted-foreground">{new Date(document.updated_at).toLocaleString()}</p>
                </div>
                <div className="relative pl-6">
                  <span className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-primary ring-4 ring-background" />
                  <p className="text-sm font-medium">Embedding Generated</p>
                </div>
                <div className="relative pl-6">
                  <span className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-primary ring-4 ring-background" />
                  <p className="text-sm font-medium">Text Extracted</p>
                </div>
                <div className="relative pl-6">
                  <span className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-muted-foreground ring-4 ring-background" />
                  <p className="text-sm font-medium">Uploaded</p>
                  <p className="text-xs text-muted-foreground">{new Date(document.created_at).toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
