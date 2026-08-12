"use client";

import { useConversation } from "@/lib/api/conversations";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Mail, Phone, Clock, FileText, CheckCircle2 } from "lucide-react";

export function CustomerPanel({ conversationId }: { conversationId: string | null }) {
  const { data: conversation, isLoading } = useConversation(conversationId);

  if (!conversationId) {
    return (
      <div className="w-1/4 min-w-[300px] border-l bg-background hidden lg:flex flex-col items-center justify-center text-muted-foreground p-6 text-center">
        Select a conversation to view customer details.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="w-1/4 min-w-[300px] border-l bg-background hidden lg:flex flex-col">
        <div className="p-6 border-b flex flex-col items-center">
          <Skeleton className="h-20 w-20 rounded-full mb-4" />
          <Skeleton className="h-6 w-32 mb-2" />
          <Skeleton className="h-4 w-24" />
        </div>
        <div className="p-6 space-y-6">
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
        </div>
      </div>
    );
  }

  if (!conversation || !conversation.customer) {
    return (
      <div className="w-1/4 min-w-[300px] border-l bg-background hidden lg:flex flex-col items-center justify-center text-muted-foreground p-6 text-center">
        No customer data available for this conversation.
      </div>
    );
  }

  const { customer } = conversation;

  return (
    <div className="w-1/4 min-w-[300px] border-l bg-background hidden lg:flex flex-col">
      <div className="p-6 border-b text-center shrink-0">
        <Avatar className="h-20 w-20 mx-auto mb-4">
          <AvatarFallback className="text-2xl">
            {customer.name?.[0]?.toUpperCase() || customer.email?.[0]?.toUpperCase() || "U"}
          </AvatarFallback>
        </Avatar>
        <h3 className="font-bold text-lg">{customer.name || "Unknown User"}</h3>
        <p className="text-muted-foreground text-sm truncate max-w-full">
          Customer ID: <span className="font-mono text-xs">{customer.id.split('-')[0]}</span>
        </p>
      </div>
      
      <ScrollArea className="flex-1 p-6">
        <div className="space-y-8">
          <div>
            <h4 className="font-semibold text-sm mb-3">Contact Details</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3 text-muted-foreground truncate max-w-full">
                <Mail className="h-4 w-4 shrink-0" /> 
                <span className="truncate">{customer.email || "No email provided"}</span>
              </div>
              <div className="flex items-center gap-3 text-muted-foreground">
                <Phone className="h-4 w-4 shrink-0" /> 
                <span>{customer.phone || "No phone provided"}</span>
              </div>
              <div className="flex items-center gap-3 text-muted-foreground">
                <Clock className="h-4 w-4 shrink-0" /> 
                <span>First seen: {new Date(customer.first_seen_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-sm mb-3">Recent Activity</h4>
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-muted before:to-transparent">
              
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-6 h-6 rounded-full border border-background bg-primary text-primary-foreground shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow">
                  <FileText className="h-3 w-3" />
                </div>
                <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] ml-3 md:ml-0 p-3 rounded border bg-background shadow-sm">
                  <div className="flex items-center justify-between space-x-2 mb-1">
                    <div className="font-medium text-xs">Chat Started</div>
                  </div>
                  <div className="text-[10px] text-muted-foreground">{new Date(conversation.started_at).toLocaleString()}</div>
                </div>
              </div>
              
              {conversation.resolved_at && (
                <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full border border-background bg-emerald-500 text-emerald-50 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow">
                    <CheckCircle2 className="h-3 w-3" />
                  </div>
                  <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] ml-3 md:ml-0 p-3 rounded border bg-background shadow-sm">
                    <div className="flex items-center justify-between space-x-2 mb-1">
                      <div className="font-medium text-xs">Resolved</div>
                    </div>
                    <div className="text-[10px] text-muted-foreground">{new Date(conversation.resolved_at).toLocaleString()}</div>
                  </div>
                </div>
              )}
              
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
