"use client";

import { useAgentAnalytics } from "@/lib/api/agents";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquare, ThumbsUp, ShieldAlert, Gauge, Activity } from "lucide-react";

export function AgentAnalytics({ agentId }: { agentId: string }) {
  const { data: analytics, isLoading, isError } = useAgentAnalytics(agentId);

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

  if (isError || !analytics) {
    return (
      <div className="p-8 text-center text-sm text-muted-foreground border rounded-lg border-dashed">
        <Activity className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
        No analytics data available for this agent yet.
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Conversations</CardTitle>
          <MessageSquare className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{analytics.questions_answered?.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">Total queries handled</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Resolution Rate</CardTitle>
          <ThumbsUp className="h-4 w-4 text-emerald-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-emerald-600">{analytics.resolution_rate}%</div>
          <p className="text-xs text-muted-foreground">Resolved without human</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Escalations</CardTitle>
          <ShieldAlert className="h-4 w-4 text-amber-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-amber-600">{analytics.escalation_rate}%</div>
          <p className="text-xs text-muted-foreground">Handed off to humans</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
          <Gauge className="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{analytics.avg_response_time_ms}ms</div>
          <p className="text-xs text-muted-foreground">Response time</p>
        </CardContent>
      </Card>
    </div>
  );
}
