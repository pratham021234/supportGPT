"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ArrowRight, Bot, AlertCircle, Clock, ShieldAlert } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function EscalationQueuePage() {
  const router = useRouter();
  const user = useAuthStore(state => state.user);

  // Fetch escalated conversations
  // In a real app we'd fetch this from /api/v1/conversations?status=ESCALATED
  // Mocking for MVP
  const { data: escalations, isLoading } = useQuery({
    queryKey: ["escalated_conversations"],
    queryFn: async () => {
      // Mock network delay
      await new Promise(r => setTimeout(r, 600));
      return [
        {
          id: "conv-1234",
          customer_name: "Jane Doe",
          reason: "Low AI Confidence (35%)",
          escalated_at: new Date(Date.now() - 120000).toISOString(),
          preview: "I need to talk to a manager about my billing issue. The bot is not understanding."
        },
        {
          id: "conv-1235",
          customer_name: "John Smith",
          reason: "Explicit Human Request",
          escalated_at: new Date(Date.now() - 360000).toISOString(),
          preview: "Human please"
        }
      ];
    }
  });

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-rose-600 flex items-center gap-2">
            <ShieldAlert className="h-8 w-8" />
            Escalation Queue
          </h1>
          <p className="text-muted-foreground mt-1">Conversations requiring immediate human attention.</p>
        </div>
      </div>

      <div className="grid gap-4">
        {isLoading ? (
          <div className="text-muted-foreground">Loading queue...</div>
        ) : escalations?.length === 0 ? (
          <div className="bg-muted/30 border rounded-xl p-12 text-center flex flex-col items-center">
            <div className="h-16 w-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-4">
              <Bot className="h-8 w-8" />
            </div>
            <h3 className="text-xl font-bold mb-2">Queue is Empty</h3>
            <p className="text-muted-foreground max-w-md">The AI is successfully handling all current conversations. No manual intervention is needed right now.</p>
          </div>
        ) : (
          escalations?.map((esc) => (
            <div key={esc.id} className="bg-background border rounded-xl p-5 shadow-sm hover:border-rose-200 transition-colors flex items-start justify-between gap-4">
              <div className="flex gap-4">
                <Avatar className="h-12 w-12 border bg-rose-50 text-rose-600">
                  <AvatarFallback>{esc.customer_name[0]}</AvatarFallback>
                </Avatar>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-lg">{esc.customer_name}</h3>
                    <Badge variant="destructive" className="text-[10px] h-5 bg-rose-500">
                      {esc.reason}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3 flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> 
                    Escalated {Math.floor((Date.now() - new Date(esc.escalated_at).getTime()) / 60000)} mins ago
                  </p>
                  <div className="bg-muted/50 p-3 rounded-lg text-sm italic border-l-2 border-rose-300">
                    "{esc.preview}"
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col gap-2 min-w-[140px]">
                <Button 
                  className="w-full bg-rose-600 hover:bg-rose-700 text-white shadow-sm"
                  onClick={() => router.push(`/dashboard/conversations?id=${esc.id}`)}
                >
                  Take Over <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
