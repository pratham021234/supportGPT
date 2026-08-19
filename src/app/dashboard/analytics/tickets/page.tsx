"use client";

import { useSearchParams } from "next/navigation";
import { useTicketAnalytics, TimeRange } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Ticket, Clock, CheckCircle, AlertTriangle } from "lucide-react";

export default function TicketAnalyticsPage() {
  const searchParams = useSearchParams();
  const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: tickets, isLoading } = useTicketAnalytics(timeRange);

  if (isLoading) {
      return <div className="p-8 space-y-4">
          <Skeleton className="h-10 w-48" />
          <div className="grid grid-cols-4 gap-4"><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div>
      </div>
  }

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div>
          <h2 className="text-2xl font-bold tracking-tight">Ticket Analytics</h2>
          <p className="text-muted-foreground">Monitor support queue health and resolution metrics.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tickets Created</CardTitle>
            <Ticket className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tickets?.created || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tickets Resolved</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tickets?.resolved || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Tickets</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tickets?.open || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
            <Clock className="h-4 w-4 text-indigo-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tickets?.avg_resolution_time_hrs || 0} hrs</div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
          <CardHeader>
              <CardTitle>SLA Compliance</CardTitle>
              <CardDescription>Percentage of tickets resolved within required SLAs</CardDescription>
          </CardHeader>
          <CardContent>
              <div className="text-4xl font-bold text-emerald-600">{tickets?.sla_compliance || 0}%</div>
          </CardContent>
      </Card>
    </div>
  );
}
