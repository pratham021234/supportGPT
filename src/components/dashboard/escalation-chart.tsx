"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useEscalationTrends } from "@/lib/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { ArrowUpRight } from "lucide-react";

export function EscalationChart({ timeRange }: { timeRange: string }) {
  const { data: escalations, isLoading } = useEscalationTrends(timeRange);

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Escalations by Topic</CardTitle>
            <CardDescription>Topics that trigger the most human handoffs</CardDescription>
          </div>
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/10 text-destructive">
            <ArrowUpRight className="h-4 w-4" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[250px] w-full mt-4">
          {isLoading ? (
            <Skeleton className="h-full w-full" />
          ) : !escalations || escalations.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              No escalation data for this period
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={escalations} layout="vertical" margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
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
                  dataKey="escalations" 
                  fill="hsl(var(--destructive))" 
                  radius={[0, 4, 4, 0]} 
                  barSize={20}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
