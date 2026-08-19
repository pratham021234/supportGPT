"use client";

import { useAgentSummary } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Users, Star } from "lucide-react";

export default function AgentAnalyticsPage() {
  const { data: summary, isLoading } = useAgentSummary();

  if (isLoading) {
      return <div className="p-8 space-y-4"><Skeleton className="h-10 w-48" /><Skeleton className="h-64 w-full" /></div>
  }

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div>
          <h2 className="text-2xl font-bold tracking-tight">Agent Analytics</h2>
          <p className="text-muted-foreground">Monitor performance and workload across your human support team.</p>
      </div>

      <Card>
          <CardHeader>
              <CardTitle>Agent Performance Board</CardTitle>
          </CardHeader>
          <CardContent>
              <Table>
                  <TableHeader>
                      <TableRow>
                          <TableHead>Agent Name</TableHead>
                          <TableHead className="text-right">Conversations Handled</TableHead>
                          <TableHead className="text-right">Resolution Rate</TableHead>
                          <TableHead className="text-right">Avg Response Time</TableHead>
                          <TableHead className="text-right">CSAT</TableHead>
                      </TableRow>
                  </TableHeader>
                  <TableBody>
                      {summary?.agents?.map((agent) => (
                          <TableRow key={agent.id}>
                              <TableCell className="font-medium flex items-center gap-2"><Users className="w-4 h-4 text-zinc-400"/> {agent.name}</TableCell>
                              <TableCell className="text-right">{agent.workload}</TableCell>
                              <TableCell className="text-right">{agent.resolution_rate}%</TableCell>
                              <TableCell className="text-right">{agent.response_time_mins} mins</TableCell>
                              <TableCell className="text-right flex items-center justify-end gap-1"><Star className="w-3 h-3 text-amber-500 fill-amber-500"/> {agent.csat}</TableCell>
                          </TableRow>
                      ))}
                      {(!summary?.agents || summary.agents.length === 0) && (
                          <TableRow>
                              <TableCell colSpan={5} className="text-center text-muted-foreground py-8">No agents found</TableCell>
                          </TableRow>
                      )}
                  </TableBody>
              </Table>
          </CardContent>
      </Card>
    </div>
  );
}
