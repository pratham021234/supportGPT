"use client";

import { usePaymentMethods, useCustomerPortal } from "@/lib/api/billing";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, CreditCard, ExternalLink, Plus } from "lucide-react";

export default function PaymentMethodsPage() {
  const { data: methods, isLoading } = usePaymentMethods();
  const { mutate: openPortal, isPending } = useCustomerPortal();

  return (
    <div className="max-w-4xl space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Payment Methods</h2>
          <p className="text-muted-foreground mt-1">
            Manage your credit cards and billing information.
          </p>
        </div>
        <Button onClick={() => openPortal()} disabled={isPending} className="gap-2">
          {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          Add Payment Method
        </Button>
      </div>

      <div className="grid gap-6">
        {isLoading ? (
          <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
        ) : methods?.map((pm) => (
          <Card key={pm.id} className={pm.is_default ? "border-primary/50" : ""}>
            <CardHeader className="flex flex-row items-center justify-between pb-4">
              <div className="space-y-1">
                <CardTitle className="text-xl flex items-center gap-2">
                  <CreditCard className="w-6 h-6 text-muted-foreground" />
                  {pm.brand} ending in {pm.last4}
                  {pm.is_default && <Badge className="ml-2">Default</Badge>}
                </CardTitle>
                <CardDescription>Expires {pm.exp_month}/{pm.exp_year}</CardDescription>
              </div>
            </CardHeader>
            <CardFooter className="bg-muted/10 border-t px-6 py-3 flex justify-between">
              <Button variant="link" className="px-0 h-auto text-muted-foreground" size="sm" onClick={() => openPortal()}>
                Manage in Stripe <ExternalLink className="w-3 h-3 ml-1" />
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
