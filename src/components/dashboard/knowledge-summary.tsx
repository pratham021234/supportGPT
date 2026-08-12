"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useMostReferencedDocs, useConfidenceAlerts } from "@/lib/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, AlertOctagon, ArrowUpRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function KnowledgeSummary() {
  const { data: topDocs, isLoading: docsLoading } = useMostReferencedDocs();
  const { data: alerts, isLoading: alertsLoading } = useConfidenceAlerts();

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Most Referenced Documents
          </CardTitle>
          <CardDescription>Top knowledge base articles utilized by AI</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {docsLoading ? (
              Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)
            ) : topDocs?.length === 0 ? (
              <p className="text-sm text-muted-foreground py-2 text-center">No documents referenced yet.</p>
            ) : (
              topDocs?.map((doc, i) => (
                <div key={doc.id || i} className="flex items-center justify-between">
                  <div className="flex flex-col truncate max-w-[200px] lg:max-w-[300px]">
                    <span className="text-sm font-medium truncate">{doc.name}</span>
                    <span className="text-xs text-muted-foreground">{doc.uses} references</span>
                  </div>
                  <Badge variant="secondary" className="text-xs shrink-0 flex items-center gap-1 text-emerald-600 bg-emerald-500/10">
                    <ArrowUpRight className="h-3 w-3" />
                    {doc.confidence_impact}
                  </Badge>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="border-amber-500/20">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2 text-amber-600">
            <AlertOctagon className="h-5 w-5" />
            Low Confidence Alerts
          </CardTitle>
          <CardDescription>Topics where AI is struggling to resolve</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {alertsLoading ? (
              Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)
            ) : alerts?.length === 0 ? (
              <p className="text-sm text-muted-foreground py-2 text-center">No low confidence topics found.</p>
            ) : (
              alerts?.map((alert, i) => (
                <div key={i} className="flex flex-col gap-1 border-b pb-3 last:border-0 last:pb-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{alert.topic}</span>
                    <span className="text-xs font-bold text-amber-600">{alert.confidence}% conf</span>
                  </div>
                  <span className="text-xs text-muted-foreground">Action: {alert.suggested_action}</span>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
