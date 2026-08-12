"use client";

import { useUsage } from "@/lib/api/billing";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Loader2, MessageSquare, FileText, Users, Cpu, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function UsagePage() {
  const { data: usage, isLoading } = useUsage();

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const renderUsageCard = (title: string, current: number = 0, limit: number = 100, icon: React.ReactNode) => {
    const percentage = Math.min(Math.round((current / limit) * 100), 100);
    const isWarning = percentage >= 80;
    const isCritical = percentage >= 100;
    
    return (
      <Card className={isCritical ? 'border-destructive/50' : isWarning ? 'border-amber-500/50' : ''}>
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
          <Progress 
            value={percentage} 
            className={`h-2 ${isCritical ? 'text-destructive [&>div]:bg-destructive' : isWarning ? 'text-amber-500 [&>div]:bg-amber-500' : ''}`} 
          />
          <p className="text-xs text-muted-foreground mt-3 flex justify-between">
            <span>{percentage}% utilized</span>
            {isCritical && <span className="text-destructive font-medium">Limit reached</span>}
            {!isCritical && isWarning && <span className="text-amber-600 font-medium">Approaching limit</span>}
          </p>
        </CardContent>
      </Card>
    );
  };

  const isAnyLimitReached = usage && (
    usage.conversations_count >= usage.conversations_limit ||
    usage.documents_count >= usage.documents_limit ||
    usage.agents_count >= usage.agents_limit ||
    usage.api_calls_count >= usage.api_calls_limit
  );

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Usage & Limits</h2>
        <p className="text-muted-foreground mt-1">
          Monitor your platform consumption. Limits reset at the beginning of your next billing cycle.
        </p>
      </div>

      {isAnyLimitReached && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive rounded-lg p-4 flex gap-3">
          <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
          <div className="flex-1 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h5 className="font-semibold mb-1">Action Required</h5>
              <p className="text-sm">You have reached one or more of your plan limits. Functionality will be restricted until you upgrade.</p>
            </div>
            <Link href="/dashboard/billing/plans" passHref legacyBehavior>
              <Button size="sm" variant="outline" className="text-destructive border-destructive hover:bg-destructive/10 shrink-0">Upgrade Now</Button>
            </Link>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {renderUsageCard("AI Conversations", usage?.conversations_count, usage?.conversations_limit, <MessageSquare className="w-4 h-4" />)}
        {renderUsageCard("Knowledge Documents", usage?.documents_count, usage?.documents_limit, <FileText className="w-4 h-4" />)}
        {renderUsageCard("Active Agents", usage?.agents_count, usage?.agents_limit, <Users className="w-4 h-4" />)}
        {renderUsageCard("API Requests", usage?.api_calls_count, usage?.api_calls_limit, <Cpu className="w-4 h-4" />)}
      </div>
    </div>
  );
}
