"use client";

import { useSearchParams } from "next/navigation";
import { useWidgetAnalyticsOverview, TimeRange } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquare, MousePointerClick, Send, Ticket } from "lucide-react";

export default function WidgetAnalyticsPage() {
  const searchParams = useSearchParams();
  const timeRange = (searchParams.get("range") as TimeRange) || "7d";

  const { data: widget, isLoading } = useWidgetAnalyticsOverview(timeRange);

  if (isLoading) {
      return <div className="p-8 space-y-4">
          <Skeleton className="h-10 w-48" />
          <div className="grid grid-cols-4 gap-4"><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div>
      </div>
  }

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div>
          <h2 className="text-2xl font-bold tracking-tight">Widget Analytics</h2>
          <p className="text-muted-foreground">Monitor funnel metrics from your embedded widget.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Widget Opens</CardTitle>
            <MousePointerClick className="h-4 w-4 text-indigo-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{widget?.widget_opens?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Chat Starts</CardTitle>
            <MessageSquare className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{widget?.chat_starts?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages Sent</CardTitle>
            <Send className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{widget?.messages_sent?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tickets Created via Widget</CardTitle>
            <Ticket className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{widget?.tickets_created?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
