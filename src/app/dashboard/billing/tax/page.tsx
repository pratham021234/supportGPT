"use client";

import { useTaxInfo, useUpdateTaxInfo } from "@/lib/api/billing";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

export default function TaxPage() {
  const { data: taxInfo, isLoading } = useTaxInfo();
  const { mutate: updateTax, isPending } = useUpdateTaxInfo();

  const [formData, setFormData] = useState({ company_name: '', address: '', vat_id: '' });

  useEffect(() => {
    if (taxInfo) setFormData(taxInfo);
  }, [taxInfo]);

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateTax(formData);
  };

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Tax & Business Info</h2>
        <p className="text-muted-foreground mt-1">
          Manage your company details for invoicing and compliance.
        </p>
      </div>

      <Card>
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle>Company Details</CardTitle>
            <CardDescription>This information will appear on all future invoices.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Company Name</Label>
              <Input 
                value={formData.company_name} 
                onChange={e => setFormData(prev => ({...prev, company_name: e.target.value}))} 
              />
            </div>
            <div className="space-y-2">
              <Label>Billing Address</Label>
              <Input 
                value={formData.address} 
                onChange={e => setFormData(prev => ({...prev, address: e.target.value}))} 
              />
            </div>
            <div className="space-y-2">
              <Label>VAT / GST ID</Label>
              <Input 
                value={formData.vat_id} 
                onChange={e => setFormData(prev => ({...prev, vat_id: e.target.value}))} 
                placeholder="e.g. IE1234567X"
              />
            </div>
          </CardContent>
          <CardFooter className="border-t pt-6">
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Save Details
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
