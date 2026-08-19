"use client";

import { useSearchParams } from "next/navigation";
import { useKnowledgeGaps, useTopQuestions, TimeRange } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BookOpen, FileQuestion, TrendingUp } from "lucide-react";

export default function KnowledgeAnalyticsPage() {
  const searchParams = useSearchParams();
  const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: topQuestions, isLoading: loadingTop } = useTopQuestions(timeRange);
  const { data: gaps, isLoading: loadingGaps } = useKnowledgeGaps();

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div>
          <h2 className="text-2xl font-bold tracking-tight">Knowledge Analytics</h2>
          <p className="text-muted-foreground">Identify content gaps and most frequently asked topics.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2"><TrendingUp className="w-4 h-4 text-emerald-500"/> Top Customer Questions</CardTitle>
                <CardDescription>Most frequently matched queries by the RAG engine.</CardDescription>
            </CardHeader>
            <CardContent>
                {loadingTop ? <Skeleton className="h-64 w-full" /> : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Query</TableHead>
                                <TableHead className="text-right">Frequency</TableHead>
                                <TableHead className="text-right">Avg Confidence</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {topQuestions?.questions?.map((q, i) => (
                                <TableRow key={i}>
                                    <TableCell className="font-medium text-sm">{q.query}</TableCell>
                                    <TableCell className="text-right">{q.frequency}</TableCell>
                                    <TableCell className="text-right">{q.confidence}%</TableCell>
                                </TableRow>
                            ))}
                            {(!topQuestions?.questions || topQuestions.questions.length === 0) && (
                                <TableRow>
                                    <TableCell colSpan={3} className="text-center text-muted-foreground py-8">No data available</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                )}
            </CardContent>
        </Card>

        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2"><FileQuestion className="w-4 h-4 text-rose-500"/> Knowledge Gaps</CardTitle>
                <CardDescription>Queries that resulted in low confidence or escalation.</CardDescription>
            </CardHeader>
            <CardContent>
                {loadingGaps ? <Skeleton className="h-64 w-full" /> : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Unanswered Query</TableHead>
                                <TableHead className="text-right">Escalations</TableHead>
                                <TableHead className="text-right">Confidence</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {gaps?.gaps?.map((gap, i) => (
                                <TableRow key={i}>
                                    <TableCell className="font-medium text-sm">{gap.query}</TableCell>
                                    <TableCell className="text-right text-rose-600">{gap.escalation_count}</TableCell>
                                    <TableCell className="text-right">{(gap.confidence_average * 100).toFixed(1)}%</TableCell>
                                </TableRow>
                            ))}
                            {(!gaps?.gaps || gaps.gaps.length === 0) && (
                                <TableRow>
                                    <TableCell colSpan={3} className="text-center text-muted-foreground py-8">No gaps detected</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                )}
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
