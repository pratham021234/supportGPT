"use client";

import { useDetailedUsage } from "@/lib/api/settings";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Loader2, MessageSquare, FileText, Users, Cpu, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function UsagePage() {
  const { data: usage, isLoading } = useDetailedUsage();

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const renderUsageCard = (title: string, current: number = 0, limit: number = 100, icon: React.ReactNode) => {
    const percentage = Math.min(Math.round((current / limit) * 100), 100);
    const isNearingLimit = percentage > 80;
    
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-md flex justify-between items-center text-muted-foreground font-medium">
            {title} {icon}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-end mb-2">
            <span className="text-2xl font-bold">{current.toLocaleString()}</span>
            <span className="text-sm text-muted-foreground">/ {limit.toLocaleString()}</span>
          </div>
          <Progress value={percentage} className={`h-2 ${isNearingLimit ? 'text-amber-500' : ''}`} />
          <p className="text-xs text-muted-foreground mt-3">
            {percentage}% utilized this billing period.
          </p>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Usage Analytics</h2>
          <p className="text-muted-foreground mt-1">
            Monitor your platform utilization against your current plan limits.
          </p>
        </div>
        <Button variant="outline" className="gap-2"><Download className="w-4 h-4" /> Export Report</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {renderUsageCard("AI Conversations", usage?.conversations_count, usage?.conversations_limit, <MessageSquare className="w-4 h-4" />)}
        {renderUsageCard("Knowledge Documents", usage?.documents_count, usage?.documents_limit, <FileText className="w-4 h-4" />)}
        {renderUsageCard("Active Agents", usage?.agents_count, usage?.agents_limit, <Users className="w-4 h-4" />)}
        {renderUsageCard("API Requests", usage?.api_calls_count, usage?.api_calls_limit, <Cpu className="w-4 h-4" />)}
      </div>
      
      <Card className="mt-8 bg-muted/20 border-dashed">
        <CardHeader>
          <CardTitle>Need higher limits?</CardTitle>
          <CardDescription>
            You are currently on the Pro plan. Upgrade to Enterprise for unlimited usage, custom SLA, and dedicated support.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button>Contact Sales for Enterprise</Button>
        </CardContent>
      </Card>
    </div>
  );
}
