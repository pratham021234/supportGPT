"use client";

import { usePlans, useSubscription, useCheckout } from "@/lib/api/billing";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2 } from "lucide-react";

export default function PlansPage() {
  const { data: plans, isLoading: plansLoading } = usePlans();
  const { data: subscription, isLoading: subLoading } = useSubscription();
  const { mutate: checkout, isPending: checkingOut } = useCheckout();

  if (plansLoading || subLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  return (
    <div className="max-w-6xl space-y-8">
      <div className="text-center max-w-2xl mx-auto mb-12">
        <h2 className="text-3xl font-bold tracking-tight">Simple, transparent pricing</h2>
        <p className="text-muted-foreground mt-2">
          Choose the plan that fits your business needs. Upgrade, downgrade, or cancel at any time.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans?.map((plan) => {
          const isCurrentPlan = subscription?.plan.id === plan.id;
          
          return (
            <Card key={plan.id} className={`flex flex-col relative ${isCurrentPlan ? 'border-primary ring-2 ring-primary/20' : ''}`}>
              {isCurrentPlan && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <Badge className="bg-primary hover:bg-primary">Current Plan</Badge>
                </div>
              )}
              <CardHeader className="text-center pb-4 pt-8">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <div className="mt-4 flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold tracking-tight">${plan.price_monthly}</span>
                  <span className="text-muted-foreground text-sm font-medium">/mo</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 mt-6">
                <ul className="space-y-4">
                  <li className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                    <span className="text-sm">Up to {plan.features.max_conversations} conversations</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                    <span className="text-sm">{plan.features.max_agents} AI Agents</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                    <span className="text-sm">{plan.features.max_documents} Knowledge Documents</span>
                  </li>
                  {plan.name === 'Enterprise' && (
                    <li className="flex items-center gap-3">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                      <span className="text-sm">SAML SSO & Advanced Audit Logs</span>
                    </li>
                  )}
                  {plan.name !== 'Starter' && (
                    <li className="flex items-center gap-3">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                      <span className="text-sm">Custom Webhooks & API Access</span>
                    </li>
                  )}
                </ul>
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full" 
                  variant={isCurrentPlan ? "outline" : "default"}
                  disabled={isCurrentPlan || checkingOut}
                  onClick={() => checkout(plan.id)}
                >
                  {isCurrentPlan ? "Current Plan" : checkingOut ? <Loader2 className="w-4 h-4 animate-spin" /> : "Upgrade"}
                </Button>
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
