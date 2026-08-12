"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useExecutiveInsights } from "@/lib/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";
import { Lightbulb, TrendingUp, AlertTriangle } from "lucide-react";

export function ExecutiveInsights() {
  const { data: insights, isLoading } = useExecutiveInsights();

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Executive Insights</CardTitle>
          <CardDescription>AI-generated recommendations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  // Assuming backend returns an array of strings for MVP insights
  const mockInsights = [
    { type: "opportunity", text: "Adding 3 FAQs about 'Refunds' could increase AI resolution by 4%." },
    { type: "trend", text: "Technical escalations spiked 15% this week. Investigate the 'API Webhooks' topic." },
    { type: "alert", text: "Agent 'Sales SDR' is resolving tickets 20% slower than last month." },
  ];

  const displayInsights = Array.isArray(insights) && insights.length > 0 ? insights : mockInsights;

  return (
    <Card className="h-full border-primary/20 bg-primary/5">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary" />
          Executive Insights
        </CardTitle>
        <CardDescription>AI-generated recommendations based on recent activity</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {displayInsights.map((insight: any, i: number) => {
            const isOpportunity = insight.type === "opportunity" || typeof insight === 'string';
            const isAlert = insight.type === "alert";
            return (
              <li key={i} className="flex gap-3 text-sm border-b border-primary/10 pb-3 last:border-0 last:pb-0">
                <div className="mt-0.5 shrink-0">
                  {isAlert ? (
                    <AlertTriangle className="h-4 w-4 text-amber-500" />
                  ) : (
                    <TrendingUp className="h-4 w-4 text-emerald-500" />
                  )}
                </div>
                <div className="text-muted-foreground leading-relaxed">
                  {typeof insight === "string" ? insight : insight.text}
                </div>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
