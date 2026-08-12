"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { OverviewCharts } from "@/components/dashboard/overview-charts";
import { MessageSquare, Bot, Library, AlertCircle } from "lucide-react";
import { 
  useDashboardStats, 
  useRecentConversations, 
  useSystemHealth 
} from "@/lib/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ErrorBoundary } from "react-error-boundary";
import { Button } from "@/components/ui/button";

import { ExecutiveInsights } from "@/components/dashboard/executive-insights";
import { AgentPerformance } from "@/components/dashboard/agent-performance";
import { KnowledgeSummary } from "@/components/dashboard/knowledge-summary";
import { EscalationChart } from "@/components/dashboard/escalation-chart";

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center bg-destructive/10 rounded-lg">
      <AlertCircle className="h-10 w-10 text-destructive mb-2" />
      <h3 className="font-semibold">Failed to load data</h3>
      <p className="text-sm text-muted-foreground mb-4">{error.message}</p>
      <Button variant="outline" onClick={resetErrorBoundary}>Try Again</Button>
    </div>
  );
}

export default function DashboardOverviewPage() {
  const [timeRange, setTimeRange] = useState("7d");
  
  const { data: stats, isLoading: statsLoading } = useDashboardStats(timeRange);
  const { data: recentConvs, isLoading: convsLoading } = useRecentConversations();
  const { data: systemStatus, isLoading: statusLoading } = useSystemHealth();

  return (
    <div className="flex flex-col gap-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          <p className="text-muted-foreground">
            Here's what's happening with your SupportGPT agents today.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground font-medium">Time Range:</span>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Select range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Conversations</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {statsLoading ? <Skeleton className="h-8 w-20" /> : (
                <>
                  <div className="text-2xl font-bold">{stats?.total_conversations || 0}</div>
                  <p className="text-xs text-muted-foreground">{stats?.conversations_trend || 'No data'}</p>
                </>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Resolution Rate</CardTitle>
              <Bot className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {statsLoading ? <Skeleton className="h-8 w-20" /> : (
                <>
                  <div className="text-2xl font-bold">{stats?.ai_resolution_rate || 0}%</div>
                  <p className="text-xs text-muted-foreground">{stats?.resolution_trend || 'No data'}</p>
                </>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Knowledge Sources</CardTitle>
              <Library className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {statsLoading ? <Skeleton className="h-8 w-20" /> : (
                <>
                  <div className="text-2xl font-bold">{stats?.knowledge_sources || 0}</div>
                  <p className="text-xs text-muted-foreground">{stats?.knowledge_trend || 'No data'}</p>
                </>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Tickets</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {statsLoading ? <Skeleton className="h-8 w-20" /> : (
                <>
                  <div className="text-2xl font-bold">{stats?.active_tickets || 0}</div>
                  <p className="text-xs text-muted-foreground">{stats?.tickets_trend || 'No data'}</p>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </ErrorBoundary>

      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <OverviewCharts timeRange={timeRange} />
      </ErrorBoundary>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <div className="col-span-3">
            <ExecutiveInsights />
          </div>
        </ErrorBoundary>
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <div className="col-span-4">
            <AgentPerformance />
          </div>
        </ErrorBoundary>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <div className="col-span-3">
            <KnowledgeSummary />
          </div>
        </ErrorBoundary>
        
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <Card className="col-span-4 flex flex-col h-full">
            <CardHeader>
              <CardTitle>Recent Conversations</CardTitle>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="space-y-8">
                {convsLoading ? (
                  Array(5).fill(0).map((_, i) => (
                    <div key={i} className="flex items-center gap-4">
                      <Skeleton className="h-9 w-9 rounded-full" />
                      <div className="space-y-2 flex-1">
                        <Skeleton className="h-4 w-[150px]" />
                        <Skeleton className="h-3 w-[250px]" />
                      </div>
                    </div>
                  ))
                ) : recentConvs?.length === 0 ? (
                  <div className="text-sm text-muted-foreground text-center py-4">No recent conversations</div>
                ) : (
                  recentConvs?.map((conv) => (
                    <div key={conv.id} className="flex items-center gap-4">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <span className="text-sm font-medium">{conv.name[0] || 'U'}</span>
                      </div>
                      <div className="flex flex-1 flex-col truncate">
                        <p className="text-sm font-medium leading-none truncate">{conv.name}</p>
                        <p className="text-sm text-muted-foreground truncate max-w-[200px] lg:max-w-[300px]">{conv.query}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-sm font-medium capitalize">{conv.status}</p>
                        <p className="text-xs text-muted-foreground">{conv.time}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <div className="col-span-3">
            <EscalationChart timeRange={timeRange} />
          </div>
        </ErrorBoundary>
        
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <Card className="col-span-4 flex flex-col">
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="space-y-4">
                {statusLoading ? (
                  Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-6 w-full" />)
                ) : (
                  <>
                    <div className="flex items-center justify-between p-3 rounded-lg border bg-card">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                        <span className="text-sm font-medium">Vector Database</span>
                      </div>
                      <span className="text-sm text-muted-foreground">{systemStatus?.vector_db_uptime || 'N/A'} Uptime</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border bg-card">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                        <span className="text-sm font-medium">LLM Gateway</span>
                      </div>
                      <span className="text-sm text-muted-foreground">Latency: {systemStatus?.llm_latency || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border bg-card">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                        <span className="text-sm font-medium">Document Processor</span>
                      </div>
                      <span className="text-sm text-muted-foreground">{systemStatus?.document_queue || 0} jobs in queue</span>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </ErrorBoundary>
      </div>
    </div>
  );
}
