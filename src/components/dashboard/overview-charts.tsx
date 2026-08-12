"use client";

import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Area, AreaChart } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useVolumeTrends, useResolutionTrends } from "@/lib/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";

export function OverviewCharts({ timeRange }: { timeRange: string }) {
  const { data: volumeData, isLoading: volumeLoading } = useVolumeTrends(timeRange);
  const { data: resolutionData, isLoading: resolutionLoading } = useResolutionTrends(timeRange);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>Conversation Volume</CardTitle>
          <CardDescription>
            Total number of customer interactions over the past week.
          </CardDescription>
        </CardHeader>
        <CardContent className="pl-2">
          <div className="h-[300px]">
            {volumeLoading ? (
              <Skeleton className="h-full w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={volumeData || []}>
                  <XAxis
                    dataKey="name"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}`}
                  />
                  <Tooltip 
                    cursor={{ fill: 'var(--muted)' }}
                    contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)', borderRadius: '8px' }}
                  />
                  <Bar
                    dataKey="total"
                    fill="currentColor"
                    radius={[4, 4, 0, 0]}
                    className="fill-primary"
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>AI Resolution Trend</CardTitle>
          <CardDescription>
            Percentage of tickets resolved entirely by AI.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            {resolutionLoading ? (
              <Skeleton className="h-full w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={resolutionData || []}>
                  <defs>
                    <linearGradient id="colorAi" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="currentColor" stopOpacity={0.8} className="text-primary"/>
                      <stop offset="95%" stopColor="currentColor" stopOpacity={0} className="text-primary"/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="name" 
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)', borderRadius: '8px' }}
                  />
                  <Area type="monotone" dataKey="ai" stroke="currentColor" fillOpacity={1} fill="url(#colorAi)" className="stroke-primary text-primary" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
