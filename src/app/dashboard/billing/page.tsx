"use client";

import { useSubscription, useUsage, useCustomerPortal } from "@/lib/api/billing";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Loader2, ArrowRight, CreditCard, Activity, CalendarDays, ExternalLink } from "lucide-react";
import Link from "next/link";

export default function BillingOverviewPage() {
  const { data: subscription, isLoading: subLoading } = useSubscription();
  const { data: usage, isLoading: usageLoading } = useUsage();
  const { mutate: openPortal, isPending: openingPortal } = useCustomerPortal();

  if (subLoading || usageLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const renderUsageBar = (label: string, current: number = 0, limit: number = 100) => {
    const percentage = Math.min(Math.round((current / limit) * 100), 100);
    return (
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium text-muted-foreground">{label}</span>
          <span>{current.toLocaleString()} / {limit.toLocaleString()}</span>
        </div>
        <Progress value={percentage} className="h-2" />
      </div>
    );
  };

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Billing Overview</h2>
        <p className="text-muted-foreground mt-1">
          Manage your subscription, view your usage, and update your payment details.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Current Plan */}
        <Card className="md:col-span-2 border-primary/20 bg-primary/5">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-xl">Current Plan</CardTitle>
                <CardDescription>You are currently on the <span className="font-semibold text-foreground">{subscription?.plan.name || "Free"}</span> plan.</CardDescription>
              </div>
              <Badge variant={subscription?.status === 'active' ? 'default' : 'destructive'} className="capitalize">
                {subscription?.status || 'Active'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight mb-6">
              ${subscription?.plan.price_monthly || 0}<span className="text-lg text-muted-foreground font-normal">/mo</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground bg-background p-4 rounded-md border">
              <div className="flex items-center gap-2"><CalendarDays className="w-4 h-4"/> Renews: <span className="font-semibold text-foreground">{subscription?.current_period_end ? new Date(subscription.current_period_end).toLocaleDateString() : 'N/A'}</span></div>
              <div className="flex items-center gap-2"><CreditCard className="w-4 h-4"/> Auto-renew: <span className="font-semibold text-foreground">{subscription?.cancel_at_period_end ? "Off" : "On"}</span></div>
            </div>
          </CardContent>
          <CardFooter className="flex gap-4">
            <Link href="/dashboard/billing/plans" passHref legacyBehavior>
              <Button>Upgrade Plan <ArrowRight className="w-4 h-4 ml-2" /></Button>
            </Link>
            <Button variant="outline" onClick={() => openPortal()} disabled={openingPortal}>
              {openingPortal ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Manage Billing <ExternalLink className="w-4 h-4 ml-2" />
            </Button>
          </CardFooter>
        </Card>

        {/* Quick Usage Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2"><Activity className="w-5 h-5 text-muted-foreground" /> Usage Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {renderUsageBar("API Requests", usage?.api_calls_count, usage?.api_calls_limit)}
            {renderUsageBar("Conversations", usage?.conversations_count, usage?.conversations_limit)}
            {renderUsageBar("Agents", usage?.agents_count, usage?.agents_limit)}
          </CardContent>
          <CardFooter>
            <Link href="/dashboard/billing/usage" className="text-sm text-primary hover:underline flex items-center">
              View detailed usage <ArrowRight className="w-3 h-3 ml-1" />
            </Link>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
