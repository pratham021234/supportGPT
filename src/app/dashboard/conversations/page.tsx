"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { ConversationList } from "@/components/conversations/conversation-list";
import { ConversationThread } from "@/components/conversations/conversation-thread";
import { CustomerPanel } from "@/components/conversations/customer-panel";
import { ConversationStatus } from "@/lib/api/conversations";

export default function ConversationsPage() {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<ConversationStatus | "ALL">("ACTIVE");

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Conversations</h1>
          <p className="text-muted-foreground">
            Monitor and intervene in active AI support conversations.
          </p>
        </div>
      </div>

      <Card className="flex flex-1 overflow-hidden min-h-0 border rounded-xl shadow-sm bg-background">
        <ConversationList 
          activeId={activeConversationId} 
          onSelect={setActiveConversationId}
          statusFilter={statusFilter}
          onStatusChange={setStatusFilter}
        />
        
        <ConversationThread conversationId={activeConversationId} />
        
        <CustomerPanel conversationId={activeConversationId} />
      </Card>
    </div>
  );
}
