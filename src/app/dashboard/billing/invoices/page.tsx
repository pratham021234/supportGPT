"use client";

import { useInvoices } from "@/lib/api/billing";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Download, Receipt, ExternalLink } from "lucide-react";

export default function InvoicesPage() {
  const { data: invoices, isLoading } = useInvoices();

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Invoices</h2>
        <p className="text-muted-foreground mt-1">
          View and download historical billing statements.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Billing History</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
          ) : !invoices || invoices.length === 0 ? (
            <div className="text-center p-12 text-muted-foreground border border-dashed rounded-md bg-muted/10">
              <Receipt className="w-8 h-8 mx-auto mb-3 opacity-20" />
              <p>No invoices generated yet.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice Number</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((inv) => (
                  <TableRow key={inv.id}>
                    <TableCell className="font-mono font-medium">{inv.stripe_invoice_id}</TableCell>
                    <TableCell>{new Date(inv.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>${inv.amount_paid.toFixed(2)}</TableCell>
                    <TableCell>
                      <Badge variant={inv.status === 'paid' ? 'outline' : 'secondary'} className={inv.status === 'paid' ? 'text-emerald-600 border-emerald-200 bg-emerald-50' : 'capitalize'}>
                        {inv.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button variant="ghost" size="sm" onClick={() => window.open(inv.invoice_pdf, '_blank')} disabled={!inv.invoice_pdf}>
                        <Download className="w-4 h-4 mr-2" /> PDF
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
