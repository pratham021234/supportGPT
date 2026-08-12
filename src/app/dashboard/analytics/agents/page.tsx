"use client";

import { useSearchParams } from "next/navigation";
import { useAgentSummary, TimeRange } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";

export default function AgentsAnalyticsPage() {
  const searchParams = useSearchParams();
  // We can pass timeRange to useAgentSummary if the API supported it, currently mock/backend supports general summary
  // const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: summary, isLoading } = useAgentSummary();

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-semibold">Agent Performance</h2>
          <p className="text-sm text-muted-foreground">Monitor resolution rates, workload, and customer satisfaction per agent.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Team Leaderboard</CardTitle>
          <CardDescription>Performance metrics for all active agents</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : !summary?.agents || summary.agents.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-8">No agent data available</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent</TableHead>
                  <TableHead className="text-right">Workload Score</TableHead>
                  <TableHead className="text-right">Escalations</TableHead>
                  <TableHead className="text-right">Avg Response (min)</TableHead>
                  <TableHead className="text-right">Resolution Rate</TableHead>
                  <TableHead className="text-right">CSAT</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {summary.agents.map((agent) => (
                  <TableRow key={agent.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>{agent.name.charAt(0)}</AvatarFallback>
                        </Avatar>
                        <span className="font-medium">{agent.name}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex flex-col items-end gap-1">
                        <span className="text-xs font-semibold">{agent.workload}%</span>
                        <Progress value={agent.workload} className="h-1.5 w-16" />
                      </div>
                    </TableCell>
                    <TableCell className="text-right text-rose-600 font-medium">{agent.escalations}</TableCell>
                    <TableCell className="text-right">{agent.response_time_mins}m</TableCell>
                    <TableCell className="text-right font-medium text-emerald-600">{agent.resolution_rate}%</TableCell>
                    <TableCell className="text-right font-bold">{agent.csat.toFixed(1)}/5.0</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
