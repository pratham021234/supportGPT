"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Lightbulb, AlertTriangle, CheckCircle, TrendingUp, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AnalyticsPage() {
  const { user } = useAuth();
  
  const [metrics, setMetrics] = useState<any>(null);
  const [gaps, setGaps] = useState<any[]>([]);
  const [docs, setDocs] = useState<any[]>([]);
  const [insights, setInsights] = useState<any[]>([]);
  
  const [loadingMetrics, setLoadingMetrics] = useState(true);
  const [loadingGaps, setLoadingGaps] = useState(true);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [loadingInsights, setLoadingInsights] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!user) return;
    
    // 1. Fetch Overview Metrics
    fetch("/api/v1/analytics/dashboard", { headers: { Authorization: `Bearer ${user.token}` } })
      .then(res => res.json())
      .then(data => { setMetrics(data); setLoadingMetrics(false); })
      .catch(() => setLoadingMetrics(false));
      
    // 2. Fetch Knowledge Gaps
    fetch("/api/v1/analytics/knowledge-gaps", { headers: { Authorization: `Bearer ${user.token}` } })
      .then(res => res.json())
      .then(data => { setGaps(data); setLoadingGaps(false); })
      .catch(() => setLoadingGaps(false));
      
    // 3. Fetch Most Referenced Docs
    fetch("/api/v1/analytics/knowledge/most-referenced", { headers: { Authorization: `Bearer ${user.token}` } })
      .then(res => res.json())
      .then(data => { setDocs(data); setLoadingDocs(false); })
      .catch(() => setLoadingDocs(false));
      
    // 4. Fetch Insights (LLM generated)
    fetch("/api/v1/analytics/insights", { headers: { Authorization: `Bearer ${user.token}` } })
      .then(res => res.json())
      .then(data => { setInsights(data); setLoadingInsights(false); })
      .catch(() => setLoadingInsights(false));
      
  }, [user]);
  
  const handleExport = async (type: "TICKETS" | "KNOWLEDGE_GAPS") => {
      if (!user) return;
      setExporting(true);
      try {
          const res = await fetch("/api/v1/analytics/reports/export", {
              method: "POST",
              headers: { 
                  "Content-Type": "application/json",
                  Authorization: `Bearer ${user.token}` 
              },
              body: JSON.stringify({ report_type: type, format: "CSV" })
          });
          if (res.ok) {
              const blob = await res.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `${type.toLowerCase()}_export.csv`;
              a.click();
              window.URL.revokeObjectURL(url);
          }
      } catch(e) {}
      setExporting(false);
  };

  return (
    <div className="flex flex-col gap-6 p-8 overflow-y-auto h-[calc(100vh-64px)]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Executive Dashboard</h1>
          <p className="text-zinc-500 mt-1">
            Real-time analytics, AI performance, and actionable insights.
          </p>
        </div>
        <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={() => handleExport("TICKETS")} disabled={exporting}>
                {exporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                Export Tickets
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExport("KNOWLEDGE_GAPS")} disabled={exporting}>
                {exporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                Export Gaps
            </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Resolution Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            {loadingMetrics ? <Skeleton className="h-8 w-20" /> : (
                <>
                    <div className="text-2xl font-bold">{metrics?.ai_resolution_rate ?? 0}%</div>
                    <p className="text-xs text-zinc-500 mt-1">+2.1% from last month</p>
                </>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Customer Satisfaction</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
             {loadingMetrics ? <Skeleton className="h-8 w-20" /> : (
                 <>
                    <div className="text-2xl font-bold">{metrics?.customer_satisfaction ?? 0}/5.0</div>
                    <p className="text-xs text-zinc-500 mt-1">Based on feedback ratings</p>
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
             {loadingMetrics ? <Skeleton className="h-8 w-20" /> : (
                 <>
                    <div className="text-2xl font-bold">{metrics?.total_escalations ?? 0}</div>
                    <p className="text-xs text-zinc-500 mt-1">Requiring human handoff</p>
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
             {loadingMetrics ? <Skeleton className="h-8 w-20" /> : (
                 <>
                    <div className="text-2xl font-bold">{metrics?.knowledge_coverage ?? 0}%</div>
                    <p className="text-xs text-zinc-500 mt-1">Queries answered by documents</p>
                 </>
             )}
          </CardContent>
        </Card>
      </div>

      {/* Insights Engine */}
      <Card className="border-indigo-100 shadow-sm bg-indigo-50/30">
        <CardHeader>
          <CardTitle className="flex items-center text-indigo-900">
              <Lightbulb className="w-5 h-5 mr-2 text-indigo-500" /> 
              Business Insights Engine
          </CardTitle>
          <CardDescription>AI-generated recommendations based on recent knowledge gaps and customer escalations.</CardDescription>
        </CardHeader>
        <CardContent>
            {loadingInsights ? (
                <div className="space-y-3">
                    <Skeleton className="h-16 w-full rounded-md" />
                    <Skeleton className="h-16 w-full rounded-md" />
                </div>
            ) : !insights || insights.length === 0 ? (
                <div className="text-sm text-zinc-500 p-4 bg-white rounded-md border text-center">No critical insights detected at this time. Great job!</div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {insights.map((insight, idx) => (
                        <div key={idx} className="bg-white p-4 rounded-xl border border-indigo-100 shadow-sm relative overflow-hidden">
                            <div className={`absolute top-0 right-0 px-2 py-1 text-[10px] font-bold tracking-wider text-white ${insight.impact === 'HIGH' ? 'bg-red-500' : 'bg-amber-500'} rounded-bl-lg`}>
                                {insight.impact} IMPACT
                            </div>
                            <h3 className="font-semibold text-zinc-900 text-sm pr-16">{insight.title}</h3>
                            <p className="text-xs text-zinc-600 mt-2">{insight.description}</p>
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

      <div className="grid gap-4 md:grid-cols-2">
        {/* Knowledge Gaps */}
        <Card>
          <CardHeader>
            <CardTitle>Raw Knowledge Gaps</CardTitle>
            <CardDescription>Topics where AI confidence is low or escalates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-4">
              {loadingGaps ? (
                Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)
              ) : !gaps || gaps.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center py-8">No data available</div>
              ) : (
                gaps.map((item, i) => (
                  <div key={i} className="flex flex-col p-3 bg-zinc-50 rounded-lg border">
                    <span className="text-sm font-medium mb-1">{item.query}</span>
                    <div className="flex justify-between items-center text-xs">
                        <span className="text-rose-600 font-semibold">{item.escalation_count} escalations</span>
                        <span className="text-zinc-500">Avg Confidence: {(item.confidence_average * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Most Referenced */}
        <Card>
          <CardHeader>
            <CardTitle>Most Referenced Documents</CardTitle>
            <CardDescription>Knowledge base usage by the AI</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loadingDocs ? (
                Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)
              ) : !docs || docs.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center py-8">No data available</div>
              ) : (
                docs.map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border-b last:border-0">
                    <div className="flex items-center">
                        <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold mr-3">{i+1}</div>
                        <span className="text-sm font-medium truncate max-w-[250px]">{item.name}</span>
                    </div>
                    <span className="text-xs font-semibold px-2 py-1 bg-zinc-100 rounded-md">{item.uses} references</span>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
