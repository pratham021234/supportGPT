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
import { useDocumentChunks, useReembedDocument } from "@/lib/api/knowledge";

function ChunkPreview({ documentId }: { documentId: string }) {
  const { data, isLoading } = useDocumentChunks(documentId);

  if (isLoading) return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading chunks...</div>;
  if (!data || data.chunks.length === 0) return <div className="p-8 text-center text-muted-foreground">No chunks found or document still processing.</div>;

  return (
    <>
      <div className="flex justify-between items-center text-xs text-muted-foreground px-1">
        <span>{data.total} Chunks Generated</span>
      </div>
      {data.chunks.map((chunk: any) => (
        <div key={chunk.id} className="bg-background border rounded-md p-4 text-sm font-mono whitespace-pre-wrap leading-relaxed shadow-sm">
          <div className="flex items-center justify-between mb-2 text-xs text-muted-foreground border-b pb-2">
            <span className="font-semibold text-foreground">Chunk #{chunk.chunk_index}</span>
            <div className="flex gap-3">
              {chunk.section && <span>Section: {chunk.section}</span>}
              <span className="flex items-center gap-1" title="Tokens"><Activity className="w-3 h-3" /> {chunk.token_count}</span>
            </div>
          </div>
          {chunk.content}
        </div>
      ))}
    </>
  );
}

export default function DocumentDetailsPage() {
  const params = useParams();
  const documentId = params.id as string;
  const { data: document, isLoading, isError } = useDocument(documentId);
  const { data: chunkData } = useDocumentChunks(documentId);
  const reembedMutation = useReembedDocument();

  const handleReembed = () => {
    if (confirm("Are you sure you want to regenerate embeddings for this document? This may take a moment and will incur API costs.")) {
      reembedMutation.mutate(documentId);
    }
  };

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
        <div className="flex-1">
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
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={handleReembed}
            disabled={reembedMutation.isPending || document.status === "PROCESSING"}
          >
            {reembedMutation.isPending ? "Queuing..." : "Regenerate Embeddings"}
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Document Preview</CardTitle>
                <CardDescription>Content extracted and chunked</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <div className="bg-muted/30 border rounded-md h-[500px] overflow-auto flex flex-col p-4 gap-4">
                {document.file_type === "FAQ" ? (
                  <div className="text-sm p-4 bg-background border rounded font-mono">
                    <strong>Q:</strong> {document.title}<br/><br/>
                    <strong>A:</strong> FAQ content
                  </div>
                ) : (
                  <ChunkPreview documentId={document.id} />
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
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><Database className="h-4 w-4" /> Embeddings</span>
                <span className="text-sm">
                  {chunkData ? `${chunkData.total} Generated` : 'Pending'}
                </span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><FileText className="h-4 w-4" /> Size</span>
                <span className="text-sm">{document.file_size ? `${(document.file_size / 1024).toFixed(2)} KB` : 'N/A'}</span>
              </div>
              {document.metadata && document.metadata.word_count && (
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><FileText className="h-4 w-4" /> Word Count</span>
                <span className="text-sm">{document.metadata.word_count} words</span>
              </div>
              )}
              {document.metadata && document.metadata.language && (
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><Globe className="h-4 w-4" /> Language</span>
                <span className="text-sm capitalize">{document.metadata.language}</span>
              </div>
              )}
              {document.metadata && document.metadata.pages_count && (
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-2"><File className="h-4 w-4" /> Pages</span>
                <span className="text-sm">{document.metadata.pages_count} pages</span>
              </div>
              )}
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
