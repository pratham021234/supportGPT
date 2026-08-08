"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CreditCard, Receipt, Zap, AlertCircle, CheckCircle2, FileText, ExternalLink, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";

export default function BillingDashboardPage() {
  const { user } = useAuth();
  
  const [subscription, setSubscription] = useState<any>(null);
  const [plans, setPlans] = useState<any[]>([]);
  const [usage, setUsage] = useState<any>({ usage: {}, limits: {} });
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [actionLoading, setActionLoading] = useState(false);

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    try {
        const [subRes, planRes, useRes, invRes] = await Promise.all([
            fetch("/api/v1/billing/subscription", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/billing/plans", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/billing/usage", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/billing/invoices", { headers: { Authorization: `Bearer ${user.token}` } })
        ]);
        if (subRes.ok) setSubscription(await subRes.json());
        if (planRes.ok) setPlans(await planRes.json());
        if (useRes.ok) setUsage(await useRes.json());
        if (invRes.ok) setInvoices(await invRes.json());
    } catch(e) {}
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleCheckout = async (planId: string) => {
    if (!user) return;
    setActionLoading(true);
    try {
        const res = await fetch("/api/v1/billing/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${user.token}` },
            body: JSON.stringify({ plan_id: planId })
        });
        if (res.ok) {
            const data = await res.json();
            // In real app, redirect to data.url
            alert(`Redirecting to Stripe Checkout: ${data.url}`);
            
            // Mock the webhook happening in the background
            await fetch("/api/v1/billing/webhooks/stripe", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    type: "checkout.session.completed",
                    data: { object: { client_reference_id: user.workspace_id } }
                })
            });
            await loadData();
        }
    } catch(e) {}
    setActionLoading(false);
  };

  const handleCustomerPortal = async () => {
    if (!user) return;
    setActionLoading(true);
    try {
        const res = await fetch("/api/v1/billing/customer-portal", {
            method: "POST",
            headers: { Authorization: `Bearer ${user.token}` }
        });
        if (res.ok) {
            const data = await res.json();
            alert(`Redirecting to Stripe Customer Portal: ${data.url}`);
        }
    } catch(e) {}
    setActionLoading(false);
  };

  const handleCancel = async () => {
      if (!user || !confirm("Are you sure you want to cancel your subscription?")) return;
      setActionLoading(true);
      await fetch("/api/v1/billing/cancel", {
          method: "POST",
          headers: { Authorization: `Bearer ${user.token}` }
      });
      await loadData();
      setActionLoading(false);
  };

  if (loading) {
      return (
          <div className="p-8 space-y-4">
              <Skeleton className="h-12 w-[300px]" />
              <Skeleton className="h-[400px] w-full" />
          </div>
      );
  }

  const activePlan = plans.find(p => p.id === subscription?.plan_id);

  return (
    <div className="flex flex-col gap-6 p-8 overflow-y-auto h-[calc(100vh-64px)]">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing & Plans</h1>
        <p className="text-zinc-500 mt-1">Manage your subscription, view invoices, and track usage.</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="overview" className="flex items-center"><Zap className="w-4 h-4 mr-2" /> Overview & Usage</TabsTrigger>
          <TabsTrigger value="plans" className="flex items-center"><CreditCard className="w-4 h-4 mr-2" /> Plans</TabsTrigger>
          <TabsTrigger value="invoices" className="flex items-center"><Receipt className="w-4 h-4 mr-2" /> Invoices</TabsTrigger>
        </TabsList>
        
        {/* OVERVIEW */}
        <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="col-span-1 md:col-span-2">
                    <CardHeader>
                        <CardTitle>Current Plan</CardTitle>
                        <CardDescription>Your workspace is currently on the {activePlan?.name || "Free Trial"} plan.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-between p-4 border rounded-lg bg-zinc-50">
                            <div>
                                <div className="flex items-center space-x-2">
                                    <p className="font-semibold text-lg">{activePlan?.name || "Starter"}</p>
                                    {subscription?.status === "TRIAL" && (
                                        <span className="bg-amber-100 text-amber-800 text-xs font-semibold px-2 py-0.5 rounded-full">Trial</span>
                                    )}
                                    {subscription?.status === "ACTIVE" && (
                                        <span className="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2 py-0.5 rounded-full">Active</span>
                                    )}
                                    {subscription?.status === "CANCELLED" && (
                                        <span className="bg-rose-100 text-rose-800 text-xs font-semibold px-2 py-0.5 rounded-full">Cancelled</span>
                                    )}
                                </div>
                                <p className="text-sm text-zinc-500 mt-1">
                                    {subscription?.renews_at 
                                        ? `Renews on ${new Date(subscription.renews_at).toLocaleDateString()}`
                                        : "Starts at $0/month"}
                                </p>
                            </div>
                            <div className="flex space-x-2">
                                {subscription?.status === "ACTIVE" ? (
                                    <>
                                        <Button variant="outline" onClick={handleCustomerPortal} disabled={actionLoading}>Manage Payment Method</Button>
                                        <Button variant="destructive" onClick={handleCancel} disabled={actionLoading}>Cancel</Button>
                                    </>
                                ) : (
                                    <Button onClick={() => document.querySelector('[value="plans"]')?.dispatchEvent(new MouseEvent('click', {bubbles: true}))}>
                                        Upgrade Plan
                                    </Button>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle>Payment Method</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {subscription?.status === "ACTIVE" ? (
                             <div className="flex items-center space-x-3 p-3 border rounded-lg">
                                <CreditCard className="w-8 h-8 text-zinc-400" />
                                <div>
                                    <p className="font-medium text-sm">•••• •••• •••• 4242</p>
                                    <p className="text-xs text-zinc-500">Expires 12/28</p>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center p-6 border border-dashed rounded-lg text-center">
                                <AlertCircle className="w-8 h-8 text-zinc-300 mb-2" />
                                <p className="text-sm text-zinc-500">No payment method on file</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Usage Limits</CardTitle>
                    <CardDescription>Track your workspace usage against your plan's allocations.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {["conversations", "agents"].map(metric => {
                        const used = usage.usage[metric] || 0;
                        const limit = usage.limits[metric] || 100;
                        const percent = Math.min(100, Math.round((used / limit) * 100));
                        
                        return (
                            <div key={metric}>
                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-sm font-medium capitalize">{metric}</span>
                                    <span className="text-sm text-zinc-500">{used} / {limit}</span>
                                </div>
                                <Progress value={percent} className={percent > 90 ? "bg-rose-100 [&>div]:bg-rose-500" : ""} />
                            </div>
                        );
                    })}
                </CardContent>
            </Card>
        </TabsContent>
        
        {/* PLANS */}
        <TabsContent value="plans" className="space-y-6">
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 {plans.map(plan => (
                     <Card key={plan.id} className={plan.id === subscription?.plan_id ? "border-indigo-500 shadow-sm" : ""}>
                         <CardHeader>
                             <CardTitle className="flex justify-between items-center">
                                 {plan.name}
                                 {plan.id === subscription?.plan_id && <CheckCircle2 className="w-5 h-5 text-indigo-500" />}
                             </CardTitle>
                             <div className="text-3xl font-bold mt-2">
                                 ${plan.monthly_price}<span className="text-sm font-normal text-zinc-500">/mo</span>
                             </div>
                             <CardDescription className="mt-2">{plan.description}</CardDescription>
                         </CardHeader>
                         <CardContent>
                             <ul className="space-y-2 text-sm">
                                 {plan.features.map((feature: string, idx: number) => (
                                     <li key={idx} className="flex items-center">
                                         <CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" />
                                         {feature}
                                     </li>
                                 ))}
                             </ul>
                         </CardContent>
                         <CardFooter>
                             <Button 
                                className="w-full" 
                                variant={plan.id === subscription?.plan_id ? "outline" : "default"}
                                disabled={plan.id === subscription?.plan_id || actionLoading}
                                onClick={() => handleCheckout(plan.id)}
                            >
                                 {plan.id === subscription?.plan_id ? "Current Plan" : "Upgrade"}
                             </Button>
                         </CardFooter>
                     </Card>
                 ))}
             </div>
        </TabsContent>

        {/* INVOICES */}
        <TabsContent value="invoices">
            <Card>
                <CardHeader>
                    <CardTitle>Billing History</CardTitle>
                    <CardDescription>View and download past invoices.</CardDescription>
                </CardHeader>
                <CardContent>
                    {invoices.length === 0 ? (
                        <div className="p-8 text-center text-zinc-500 border border-dashed rounded-lg">
                            <Receipt className="w-8 h-8 mx-auto mb-2 text-zinc-300" />
                            <p>No invoices found.</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {invoices.map(invoice => (
                                <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-zinc-50">
                                    <div className="flex items-center space-x-4">
                                        <div className="p-2 bg-indigo-50 text-indigo-600 rounded">
                                            <FileText className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-sm">{invoice.invoice_number}</p>
                                            <p className="text-xs text-zinc-500">{new Date(invoice.issued_at).toLocaleDateString()}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-6">
                                        <div className="text-right">
                                            <p className="font-semibold">${invoice.amount.toFixed(2)}</p>
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                                                invoice.status === 'PAID' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                                            }`}>
                                                {invoice.status}
                                            </span>
                                        </div>
                                        <Button variant="ghost" size="icon" className="text-zinc-500 hover:text-indigo-600">
                                            <ExternalLink className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
