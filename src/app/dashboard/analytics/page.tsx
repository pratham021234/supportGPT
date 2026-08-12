"use client";

import { useSearchParams } from "next/navigation";
import { useAnalyticsOverview, useVolumeTrends, useResolutionTrends, TimeRange, useExecutiveInsights } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AreaChartCard } from "@/components/analytics/charts/area-chart-card";
import { MessageSquare, CheckCircle, AlertTriangle, Lightbulb, TrendingUp } from "lucide-react";

export default function AnalyticsOverviewPage() {
  const searchParams = useSearchParams();
  const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: overview, isLoading: isLoadingOverview } = useAnalyticsOverview(timeRange);
  const { data: volume, isLoading: isLoadingVolume } = useVolumeTrends(timeRange);
  const { data: resolution, isLoading: isLoadingResolution } = useResolutionTrends(timeRange);
  const { data: insights, isLoading: isLoadingInsights } = useExecutiveInsights();

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Conversations</CardTitle>
            <MessageSquare className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            {isLoadingOverview ? <Skeleton className="h-8 w-20" /> : (
              <>
                <div className="text-2xl font-bold">{overview?.total_conversations?.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1 text-emerald-600">
                  <TrendingUp className="h-3 w-3" /> +14.2% from last period
                </p>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Resolution Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            {isLoadingOverview ? <Skeleton className="h-8 w-20" /> : (
              <>
                <div className="text-2xl font-bold">{overview?.ai_resolution_rate ?? 0}%</div>
                <p className="text-xs text-muted-foreground mt-1 text-emerald-600">
                  Target: 80%
                </p>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Escalations</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            {isLoadingOverview ? <Skeleton className="h-8 w-20" /> : (
              <>
                <div className="text-2xl font-bold">{overview?.total_escalations?.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground mt-1 text-rose-600">
                  Human handoffs required
                </p>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Coverage</CardTitle>
            <Lightbulb className="h-4 w-4 text-indigo-500" />
          </CardHeader>
          <CardContent>
            {isLoadingOverview ? <Skeleton className="h-8 w-20" /> : (
              <>
                <div className="text-2xl font-bold">{overview?.knowledge_coverage ?? 0}%</div>
                <p className="text-xs text-muted-foreground mt-1">Queries answered via docs</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <div className="md:col-span-1 lg:col-span-4">
          <AreaChartCard 
            title="Conversation Volume" 
            description={`Inbound requests for ${timeRange}`}
            data={volume?.trends || []}
            dataKey="value"
            xAxisKey="date"
            color="#3b82f6" // blue-500
            isLoading={isLoadingVolume}
          />
        </div>
        
        <div className="md:col-span-1 lg:col-span-3">
          <AreaChartCard 
            title="AI Resolution Trend" 
            description={`Daily resolution rate for ${timeRange}`}
            data={resolution?.trends || []}
            dataKey="value"
            xAxisKey="date"
            color="#10b981" // emerald-500
            isLoading={isLoadingResolution}
          />
        </div>
      </div>

      {/* Insights Engine */}
      <Card className="border-indigo-100 shadow-sm bg-indigo-50/30">
        <CardHeader>
          <CardTitle className="flex items-center text-indigo-900">
              <Lightbulb className="w-5 h-5 mr-2 text-indigo-500" /> 
              Executive Insights Engine
          </CardTitle>
          <CardDescription>AI-generated recommendations based on knowledge gaps and customer escalations.</CardDescription>
        </CardHeader>
        <CardContent>
            {isLoadingInsights ? (
                <div className="space-y-3">
                    <Skeleton className="h-16 w-full rounded-md" />
                    <Skeleton className="h-16 w-full rounded-md" />
                </div>
            ) : !insights || insights.length === 0 ? (
                <div className="text-sm text-zinc-500 p-4 bg-white rounded-md border text-center">No critical insights detected at this time.</div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {insights.map((insight, idx) => (
                        <div key={idx} className="bg-white p-4 rounded-xl border border-indigo-100 shadow-sm relative overflow-hidden flex flex-col justify-between">
                            <div>
                              <div className={`absolute top-0 right-0 px-2 py-1 text-[10px] font-bold tracking-wider text-white ${insight.impact === 'HIGH' ? 'bg-rose-500' : 'bg-amber-500'} rounded-bl-lg`}>
                                  {insight.impact} IMPACT
                              </div>
                              <h3 className="font-semibold text-zinc-900 text-sm pr-16">{insight.title}</h3>
                              <p className="text-xs text-zinc-600 mt-2">{insight.description}</p>
                            </div>
                            <div className="mt-4 pt-3 border-t border-zinc-100">
                                <span className="text-xs font-semibold text-indigo-600 block mb-1">Recommended Action:</span>
                                <span className="text-xs text-zinc-700">{insight.action}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </CardContent>
      </Card>
    </div>
  );
}
