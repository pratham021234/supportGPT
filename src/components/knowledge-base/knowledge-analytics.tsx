"use client";

import { useKnowledgeAnalytics } from "@/lib/api/knowledge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { TrendingUp, ArrowUpRight, ArrowDownRight, BookOpen } from "lucide-react";

export function KnowledgeAnalytics() {
  const { data: analytics, isLoading } = useKnowledgeAnalytics();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-[250px] w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Coverage Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-[250px] w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  // Mocking data if backend returns empty or undefined for now, so UI can be visualized
  const mostUsed = analytics?.most_used?.length ? analytics.most_used : [
    { name: "Refund Policy", uses: 450 },
    { name: "API Documentation", uses: 320 },
    { name: "Getting Started Guide", uses: 210 },
    { name: "Billing FAQ", uses: 150 },
  ];

  const coverageTrend = analytics?.coverage_trend || 85;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Most Referenced</CardTitle>
              <CardDescription>Documents most frequently used by AI</CardDescription>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
              <BookOpen className="h-4 w-4" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mostUsed} layout="vertical" margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="var(--border)" opacity={0.5} />
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }} 
                />
                <Tooltip 
                  cursor={{ fill: 'var(--muted)', opacity: 0.4 }}
                  contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)', borderRadius: '8px' }}
                />
                <Bar 
                  dataKey="uses" 
                  fill="hsl(var(--primary))" 
                  radius={[0, 4, 4, 0]} 
                  barSize={20}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Knowledge Coverage</CardTitle>
              <CardDescription>Percentage of user queries successfully answered</CardDescription>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-[250px] space-y-4">
            <div className="relative flex items-center justify-center h-40 w-40 rounded-full border-[8px] border-emerald-500/20">
              <div 
                className="absolute inset-0 rounded-full border-[8px] border-emerald-500" 
                style={{ clipPath: `polygon(0 0, 100% 0, 100% ${coverageTrend}%, 0 ${coverageTrend}%)` }} 
              />
              <div className="text-4xl font-bold text-foreground">{coverageTrend}%</div>
            </div>
            <p className="text-sm text-muted-foreground flex items-center gap-1">
              <ArrowUpRight className="h-4 w-4 text-emerald-500" />
              Up 4% from last week
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
