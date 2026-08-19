"use client";

import { useSearchParams } from "next/navigation";
import { useAiPerformance, TimeRange } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Brain, ShieldAlert, Zap, BookOpen } from "lucide-react";

export default function AiPerformancePage() {
  const searchParams = useSearchParams();
  const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: performance, isLoading } = useAiPerformance(timeRange);

  if (isLoading) {
      return <div className="p-8 space-y-4">
          <Skeleton className="h-10 w-48" />
          <div className="grid grid-cols-4 gap-4"><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div>
      </div>
  }

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div>
          <h2 className="text-2xl font-bold tracking-tight">AI Performance</h2>
          <p className="text-muted-foreground">Monitor the underlying metrics of the RAG engine.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Confidence</CardTitle>
            <Brain className="h-4 w-4 text-indigo-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(performance?.avg_confidence || 0) * 100}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Answer Accuracy</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{performance?.answer_accuracy || 0}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hallucination Risk</CardTitle>
            <ShieldAlert className="h-4 w-4 text-rose-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{performance?.hallucination_risk || 0}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Latency</CardTitle>
            <Zap className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{performance?.latency_ms || 0} ms</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
import { CheckCircle } from "lucide-react";
