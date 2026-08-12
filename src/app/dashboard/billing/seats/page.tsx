"use client";

import { useSeats } from "@/lib/api/billing";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Loader2, Users, Plus, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function SeatsPage() {
  const { data: seats, isLoading } = useSeats();

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const percentage = seats ? Math.round((seats.used / seats.purchased) * 100) : 0;

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Seat Management</h2>
        <p className="text-muted-foreground mt-1">
          Allocate licenses to your team members.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Users className="w-5 h-5 text-muted-foreground"/> Current Allocation</CardTitle>
          <CardDescription>You are using {seats?.used} of {seats?.purchased} purchased seats.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
           <Progress value={percentage} className="h-4" />
           <div className="flex justify-between text-sm font-medium text-muted-foreground">
              <span>{seats?.used} Used</span>
              <span>{seats?.available} Available</span>
           </div>
        </CardContent>
        <CardFooter className="flex gap-4 border-t pt-6">
           <Link href="/dashboard/billing/plans" passHref legacyBehavior>
             <Button className="gap-2"><Plus className="w-4 h-4"/> Buy More Seats</Button>
           </Link>
           <Link href="/dashboard/team" passHref legacyBehavior>
             <Button variant="outline" className="gap-2">Manage Users <ArrowRight className="w-4 h-4"/></Button>
           </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
