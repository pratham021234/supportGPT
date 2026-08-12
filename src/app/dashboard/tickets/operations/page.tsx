"use client";

import Link from "next/link";
import { useTicketOperations, useAgentWorkload, useTicketAnalytics } from "@/lib/api/tickets";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, CheckCircle2, AlertTriangle, TrendingUp, Users, Clock, FileText, CheckCircle } from "lucide-react";

export default function TicketOperationsDashboard() {
  const { data: operations, isLoading: isLoadingOps } = useTicketOperations();
  const { data: workload, isLoading: isLoadingWorkload } = useAgentWorkload();
  const { data: analytics, isLoading: isLoadingAnalytics } = useTicketAnalytics();

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild className="shrink-0">
            <Link href="/dashboard/tickets"><ArrowLeft className="h-5 w-5" /></Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Support Operations</h1>
            <p className="text-muted-foreground">
              Executive overview of ticket volume, agent performance, and SLA compliance.
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Tickets</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoadingOps ? <Skeleton className="h-8 w-16" /> : (
              <>
                <div className="text-2xl font-bold">{operations?.open_tickets}</div>
                <p className="text-xs text-muted-foreground mt-1 text-amber-600 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> +12% from yesterday
                </p>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            {isLoadingOps ? <Skeleton className="h-8 w-16" /> : (
              <>
                <div className="text-2xl font-bold">{operations?.resolved_today}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Agent efficiency nominal
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">SLA Compliance</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${operations && operations.sla_compliance < 90 ? 'text-destructive' : 'text-muted-foreground'}`} />
          </CardHeader>
          <CardContent>
            {isLoadingOps ? <Skeleton className="h-8 w-16" /> : (
              <>
                <div className="text-2xl font-bold">{operations?.sla_compliance}%</div>
                <Progress value={operations?.sla_compliance ?? 0} className="h-2 mt-2" />
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoadingOps ? <Skeleton className="h-8 w-16" /> : (
              <>
                <div className="text-2xl font-bold">{operations?.avg_resolution_time}</div>
                <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3 rotate-180" /> -14m from last week
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        {/* Analytics Trends (Mocked chart area) */}
        <Card className="md:col-span-4">
          <CardHeader>
            <CardTitle>Ticket Volume Trends</CardTitle>
            <CardDescription>Daily ticket inflow over the past 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingAnalytics ? (
              <Skeleton className="h-[250px] w-full rounded-xl" />
            ) : (
              <div className="h-[250px] w-full flex items-end justify-between gap-2 px-2 pb-6 relative border-b border-l border-muted">
                {analytics?.volume_trends.map((item, i) => (
                  <div key={i} className="flex flex-col items-center flex-1 gap-2 group">
                    <div className="relative w-full flex justify-center h-full">
                      <div 
                        className="w-4/5 bg-primary/20 group-hover:bg-primary/40 rounded-t-sm transition-all absolute bottom-0" 
                        style={{ height: `${(item.count / 70) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-muted-foreground absolute -bottom-6">{item.date}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Agent Workload */}
        <Card className="md:col-span-3">
          <CardHeader>
            <CardTitle>Agent Workload</CardTitle>
            <CardDescription>Current capacity and resolution performance</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingWorkload ? (
              <div className="space-y-6">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : (
              <div className="space-y-6">
                {workload?.map((agent) => (
                  <div key={agent.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-9 w-9">
                        <AvatarFallback>{agent.name[0]}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium leading-none">{agent.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {agent.assigned} assigned • {agent.pending} pending
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <div className="text-sm font-bold">{agent.workload_score}%</div>
                      <Progress 
                        value={agent.workload_score} 
                        className="h-1.5 w-16" 
                        // @ts-ignore (Tailwind colors can be injected via class or style, we'll let shadcn default handle it, but we can visually tint if needed)
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
