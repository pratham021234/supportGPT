"use client";

import { useBillingHistory } from "@/lib/api/billing";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

export default function HistoryPage() {
  const { data: history, isLoading } = useBillingHistory();

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Transaction History</h2>
        <p className="text-muted-foreground mt-1">
          A ledger of all plan changes, payments, and refunds.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Event Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history?.map((event) => (
                  <TableRow key={event.id}>
                    <TableCell>{new Date(event.date).toLocaleDateString()}</TableCell>
                    <TableCell className="font-medium">{event.type}</TableCell>
                    <TableCell>${event.amount.toFixed(2)}</TableCell>
                    <TableCell>
                      <Badge variant={event.status === 'Success' ? 'outline' : 'secondary'} className={event.status === 'Success' ? 'text-emerald-600 border-emerald-200' : ''}>
                        {event.status}
                      </Badge>
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
