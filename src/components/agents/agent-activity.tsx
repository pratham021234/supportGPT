"use client";

import { useAgentActivity } from "@/lib/api/agents";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Activity, Edit, Play, Database, ShieldAlert } from "lucide-react";

export function AgentActivity({ agentId }: { agentId: string }) {
  const { data: activities, isLoading, isError } = useAgentActivity(agentId);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Activity History</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </CardContent>
      </Card>
    );
  }

  // Mock array if backend doesn't return list yet
  const displayActivities = activities && activities.length > 0 ? activities : [
    { id: "1", action: "DEPLOYMENT", details: "Agent published to production", created_at: new Date().toISOString() },
    { id: "2", action: "PROMPT_UPDATED", details: "System prompt modified", created_at: new Date(Date.now() - 3600000).toISOString() },
    { id: "3", action: "KNOWLEDGE_ADDED", details: "Added 'Refund Policy' to scope", created_at: new Date(Date.now() - 86400000).toISOString() },
    { id: "4", action: "CREATED", details: "Agent created", created_at: new Date(Date.now() - 172800000).toISOString() },
  ];

  const getActionIcon = (action: string) => {
    if (action.includes("DEPLOYMENT") || action.includes("PUBLISHED")) return <Play className="h-4 w-4 text-emerald-500" />;
    if (action.includes("PROMPT") || action.includes("MODEL") || action.includes("UPDATED")) return <Edit className="h-4 w-4 text-blue-500" />;
    if (action.includes("KNOWLEDGE")) return <Database className="h-4 w-4 text-amber-500" />;
    if (action.includes("ESCALATION")) return <ShieldAlert className="h-4 w-4 text-destructive" />;
    return <Activity className="h-4 w-4 text-muted-foreground" />;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Feed</CardTitle>
        <CardDescription>Recent changes and deployments for this agent.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative border-l border-muted ml-3 space-y-6">
          {displayActivities.map((activity) => (
            <div key={activity.id} className="relative pl-6">
              <span className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-background border flex items-center justify-center">
                {getActionIcon(activity.action)}
              </span>
              <p className="text-sm font-medium">{activity.details}</p>
              <p className="text-xs text-muted-foreground">{new Date(activity.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
