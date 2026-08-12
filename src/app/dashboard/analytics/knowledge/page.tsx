"use client";

import { useSearchParams } from "next/navigation";
import { useKnowledgeGaps, useTopQuestions, TimeRange } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function KnowledgeAnalyticsPage() {
  const searchParams = useSearchParams();
  const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: topQuestions, isLoading: isLoadingQs } = useTopQuestions(timeRange);
  const { data: gaps, isLoading: isLoadingGaps } = useKnowledgeGaps();

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div className="grid gap-6 md:grid-cols-2">
        {/* Top Questions */}
        <Card className="h-[500px] flex flex-col">
          <CardHeader className="shrink-0">
            <CardTitle>Top Questions</CardTitle>
            <CardDescription>Most frequently asked customer queries</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            {isLoadingQs ? (
              <div className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : !topQuestions?.questions || topQuestions.questions.length === 0 ? (
              <div className="text-sm text-muted-foreground text-center py-8">No data available</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Question</TableHead>
                    <TableHead className="text-right">Freq</TableHead>
                    <TableHead className="text-right">Conf</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {topQuestions.questions.map((q, i) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium max-w-[200px] truncate" title={q.query}>{q.query}</TableCell>
                      <TableCell className="text-right">{q.frequency}</TableCell>
                      <TableCell className="text-right">
                        <Badge variant={q.confidence > 85 ? "default" : "secondary"}>
                          {q.confidence}%
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Knowledge Gaps */}
        <Card className="h-[500px] flex flex-col">
          <CardHeader className="shrink-0">
            <CardTitle className="text-rose-600">Knowledge Gaps</CardTitle>
            <CardDescription>Topics with low confidence or high escalation rates</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            {isLoadingGaps ? (
              <div className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : !gaps?.gaps || gaps.gaps.length === 0 ? (
              <div className="text-sm text-muted-foreground text-center py-8">No critical gaps detected.</div>
            ) : (
              <div className="space-y-4">
                {gaps.gaps.map((item, i) => (
                  <div key={i} className="flex flex-col p-4 bg-rose-50/50 rounded-lg border border-rose-100">
                    <span className="text-sm font-semibold mb-2">{item.query}</span>
                    <div className="flex justify-between items-center text-xs">
                        <span className="text-rose-600 font-semibold">{item.escalation_count} escalations</span>
                        <span className="text-muted-foreground">Avg Confidence: {(item.confidence_average * 100).toFixed(1)}%</span>
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
