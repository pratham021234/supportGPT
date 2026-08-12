"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useAgentSummary } from "@/lib/api/dashboard";
import { Skeleton } from "@/components/ui/skeleton";
import { Users, Star, ArrowUpRight, ArrowDownRight } from "lucide-react";

export function AgentPerformance() {
  const { data: agents, isLoading } = useAgentSummary();

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Users className="h-5 w-5" />
          Agent Performance
        </CardTitle>
        <CardDescription>Resolution and satisfaction metrics by agent</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
              <tr>
                <th className="px-4 py-3 rounded-tl-lg rounded-bl-lg">Agent Name</th>
                <th className="px-4 py-3 text-right">Resolution</th>
                <th className="px-4 py-3 text-right">CSAT</th>
                <th className="px-4 py-3 text-right rounded-tr-lg rounded-br-lg">Volume</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array(3).fill(0).map((_, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="px-4 py-3"><Skeleton className="h-4 w-32" /></td>
                    <td className="px-4 py-3 text-right"><Skeleton className="h-4 w-12 ml-auto" /></td>
                    <td className="px-4 py-3 text-right"><Skeleton className="h-4 w-12 ml-auto" /></td>
                    <td className="px-4 py-3 text-right"><Skeleton className="h-4 w-12 ml-auto" /></td>
                  </tr>
                ))
              ) : agents?.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-4 text-center text-muted-foreground">No agent data available</td>
                </tr>
              ) : (
                agents?.map((agent, i) => (
                  <tr key={i} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-medium">{agent.name}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {agent.resolution_rate}%
                        {agent.resolution_rate > 85 ? (
                          <ArrowUpRight className="h-3 w-3 text-emerald-500" />
                        ) : (
                          <ArrowDownRight className="h-3 w-3 text-amber-500" />
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {agent.satisfaction}
                        <Star className="h-3 w-3 text-amber-400 fill-amber-400" />
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-muted-foreground">
                      {agent.conversations.toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
