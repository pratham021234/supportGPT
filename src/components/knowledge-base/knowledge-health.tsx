"use client";

import { useKnowledgeHealth } from "@/lib/api/knowledge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, AlertCircle, FileText, Activity, Database } from "lucide-react";

export function KnowledgeHealthPanel() {
  const { data: health, isLoading } = useKnowledgeHealth();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array(4).fill(0).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-[100px]" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-[60px]" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Assuming missing elements from backend for UI completeness are mocked/derived
  const errorCount = health?.vector_storage?.collections?.error || 0;
  
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{health?.documents_count || 0}</div>
          <p className="text-xs text-muted-foreground">Processed and ready</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Chunks</CardTitle>
          <Database className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{health?.chunks_count || 0}</div>
          <p className="text-xs text-muted-foreground">Stored in Vector DB</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">System Health</CardTitle>
          <Activity className="h-4 w-4 text-emerald-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-emerald-600 capitalize">
            {health?.status || 'Unknown'}
          </div>
          <p className="text-xs text-muted-foreground">Vector database connected</p>
        </CardContent>
      </Card>
      <Card className={errorCount > 0 ? "border-destructive" : ""}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Processing Issues</CardTitle>
          {errorCount > 0 ? (
            <AlertCircle className="h-4 w-4 text-destructive" />
          ) : (
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          )}
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${errorCount > 0 ? "text-destructive" : "text-emerald-600"}`}>
            {errorCount}
          </div>
          <p className="text-xs text-muted-foreground">Documents failed processing</p>
        </CardContent>
      </Card>
    </div>
  );
}
