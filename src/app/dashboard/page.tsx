import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { OverviewCharts } from "@/components/dashboard/overview-charts";
import { MessageSquare, Bot, Library, AlertCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { analyticsClient } from "@/lib/api/analytics-client";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardOverviewPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: analyticsClient.getStats,
  });

  const { data: recentConvs, isLoading: convsLoading } = useQuery({
    queryKey: ["recent-conversations"],
    queryFn: analyticsClient.getRecentConversations,
  });

  const { data: systemStatus, isLoading: statusLoading } = useQuery({
    queryKey: ["system-status"],
    queryFn: analyticsClient.getSystemStatus,
  });
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="text-muted-foreground">
          Here's what's happening with your SupportGPT agents today.
        </p>
      </div>

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

      <OverviewCharts />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Conversations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-8">
              {convsLoading ? (
                Array(3).fill(0).map((_, i) => (
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
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted">
                      <span className="text-sm font-medium">{conv.name[0]}</span>
                    </div>
                    <div className="flex flex-1 flex-col">
                      <p className="text-sm font-medium leading-none">{conv.name}</p>
                      <p className="text-sm text-muted-foreground truncate max-w-[200px] lg:max-w-[300px]">{conv.query}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{conv.status}</p>
                      <p className="text-xs text-muted-foreground">{conv.time}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {statusLoading ? (
                Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-6 w-full" />)
              ) : (
                <>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-emerald-500" />
                      <span className="text-sm font-medium">Vector Database</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{systemStatus?.vector_db_uptime || 'N/A'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-emerald-500" />
                      <span className="text-sm font-medium">LLM Gateway</span>
                    </div>
                    <span className="text-sm text-muted-foreground">Latency: {systemStatus?.llm_latency || 'N/A'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-amber-500" />
                      <span className="text-sm font-medium">Document Processor</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{systemStatus?.document_queue || 0} jobs in queue</span>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
