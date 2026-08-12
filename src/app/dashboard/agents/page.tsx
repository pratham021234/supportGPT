"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Settings2, Sparkles, MessageSquare, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useAgents } from "@/lib/api/agents";
import { Skeleton } from "@/components/ui/skeleton";
import { CreateAgentModal } from "@/components/agents/create-agent-modal";
import { EmptyState, ErrorState } from "@/components/ui/empty-state";
import { ErrorBoundary } from "react-error-boundary";

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <ErrorState 
      title="Failed to load agents" 
      message={error.message} 
      onRetry={resetErrorBoundary} 
    />
  );
}

export default function AgentsPage() {
  const { data: agents, isLoading, isError, refetch } = useAgents();

  return (
    <div className="flex flex-col gap-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Agents</h1>
          <p className="text-muted-foreground">
            Build and manage your fleet of AI customer support agents.
          </p>
        </div>
        <CreateAgentModal />
      </div>

      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {isLoading ? (
            Array(3).fill(0).map((_, i) => (
              <Card key={i} className="flex flex-col border shadow-sm h-[250px]">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <Skeleton className="h-10 w-10 rounded-lg" />
                    <Skeleton className="h-5 w-16 rounded-full" />
                  </div>
                  <Skeleton className="h-6 w-3/4 mt-4" />
                  <Skeleton className="h-10 w-full mt-2" />
                </CardHeader>
                <CardContent className="pb-4 flex-1">
                  <Skeleton className="h-8 w-full" />
                </CardContent>
              </Card>
            ))
          ) : isError ? (
            <div className="col-span-full">
              <ErrorState 
                title="Failed to load agents" 
                message="Check your connection and try again."
                onRetry={() => refetch()}
              />
            </div>
          ) : !agents || agents.length === 0 ? (
            <div className="col-span-full">
              <EmptyState 
                icon={<Bot className="h-12 w-12 text-muted-foreground" />}
                title="No agents found"
                description="Click 'Create Agent' to start building your first AI assistant."
              />
            </div>
          ) : (
            agents.map((agent) => (
              <Card key={agent.id} className="flex flex-col border bg-background shadow-sm transition-all hover:shadow-md">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <Bot className="h-5 w-5 text-primary" />
                      </div>
                    </div>
                    <Badge variant={agent.status === "ACTIVE" ? "default" : "secondary"} className={
                      agent.status === "ACTIVE" ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20" : ""
                    }>
                      {agent.status}
                    </Badge>
                  </div>
                  <CardTitle className="mt-4 text-xl">{agent.name}</CardTitle>
                  <CardDescription className="line-clamp-2 h-10">
                    {agent.description || "No description provided."}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-4 flex-1">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex flex-col gap-1">
                      <span className="text-muted-foreground flex items-center gap-1">
                        <Sparkles className="h-3 w-3" /> Model
                      </span>
                      <span className="font-medium font-mono text-xs truncate" title={agent.model || "Default"}>
                        {agent.model || "Default"}
                      </span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-muted-foreground flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" /> Chats
                      </span>
                      <span className="font-medium">{agent.conversations?.toLocaleString() || 0}</span>
                    </div>
                  </div>
                </CardContent>
                <div className="border-t px-6 py-4 flex items-center justify-between bg-muted/20">
                  <span className="text-xs text-muted-foreground font-medium">
                    {agent.sources || 0} Knowledge Sources
                  </span>
                  <div className="flex gap-2">
                    <Link href={`/dashboard/agents/${agent.id}`}>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                        <Settings2 className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Link href={`/dashboard/agents/${agent.id}?tab=testing`}>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </ErrorBoundary>
    </div>
  );
}
