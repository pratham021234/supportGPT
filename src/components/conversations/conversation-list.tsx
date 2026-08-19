"use client";

import { useState } from "react";
import { useConversations, Conversation, ConversationStatus } from "@/lib/api/conversations";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Search, Filter, Bot } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ConversationListProps {
  activeId: string | null;
  onSelect: (id: string) => void;
  statusFilter: ConversationStatus | "ALL";
  onStatusChange: (status: ConversationStatus | "ALL") => void;
}

export function ConversationList({ activeId, onSelect, statusFilter, onStatusChange }: ConversationListProps) {
  const [searchQuery, setSearchQuery] = useState("");
  // If "ALL" is selected, we fetch all by omitting the status arg
  const queryStatus = statusFilter === "ALL" ? undefined : statusFilter;
  const { data: conversations, isLoading } = useConversations(queryStatus);

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const filteredConversations = conversations?.filter(conv => {
    if (!searchQuery) return true;
    const nameMatch = conv.customer?.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const emailMatch = conv.customer?.email?.toLowerCase().includes(searchQuery.toLowerCase());
    return nameMatch || emailMatch;
  });

  return (
    <div className="w-full md:w-1/3 lg:w-[350px] border-r flex flex-col bg-muted/20 h-full overflow-hidden">
      <div className="p-4 border-b space-y-4 shrink-0 bg-background">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search conversations..." 
              className="pl-8 bg-background" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex gap-2 text-sm overflow-x-auto pb-1 scrollbar-hide">
          <Badge 
            variant={statusFilter === "ACTIVE" ? "secondary" : "outline"}
            className={statusFilter === "ACTIVE" ? "bg-primary/10 text-primary cursor-pointer" : "cursor-pointer"}
            onClick={() => onStatusChange("ACTIVE")}
          >
            Active
          </Badge>
          <Badge 
            variant={statusFilter === "ESCALATED" ? "secondary" : "outline"}
            className={statusFilter === "ESCALATED" ? "bg-destructive/10 text-destructive cursor-pointer hover:bg-destructive/20" : "cursor-pointer"}
            onClick={() => onStatusChange("ESCALATED")}
          >
            Escalated
          </Badge>
          <Badge 
            variant={statusFilter === "RESOLVED" ? "secondary" : "outline"}
            className={statusFilter === "RESOLVED" ? "bg-muted cursor-pointer" : "cursor-pointer"}
            onClick={() => onStatusChange("RESOLVED")}
          >
            Resolved
          </Badge>
        </div>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="flex flex-col">
          {isLoading ? (
            Array(5).fill(0).map((_, i) => (
              <div key={i} className="p-4 border-b">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 w-full">
                    <Skeleton className="h-4 w-32" />
                  </div>
                  <Skeleton className="h-3 w-8" />
                </div>
                <Skeleton className="h-3 w-2/3 mb-2" />
                <Skeleton className="h-5 w-16 rounded" />
              </div>
            ))
          ) : !filteredConversations || filteredConversations.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No {statusFilter !== "ALL" ? statusFilter.toLowerCase() : ""} conversations found.
            </div>
          ) : (
            filteredConversations.map((conv) => (
              <div 
                key={conv.id} 
                onClick={() => onSelect(conv.id)}
                className={`p-4 border-b cursor-pointer transition-colors hover:bg-muted/50 ${activeId === conv.id ? "bg-muted" : "bg-background"}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm truncate max-w-[150px]">
                      {conv.customer?.name || conv.customer?.email || "Unknown User"}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">{formatTime(conv.last_message_at)}</span>
                </div>
                
                <div className="flex flex-wrap items-center gap-2 mt-3">
                  {conv.status === "ESCALATED" && (
                    <Badge variant="destructive" className="h-5 text-[10px]">Escalated</Badge>
                  )}
                  {conv.status === "ACTIVE" && (
                    <Badge variant="outline" className="h-5 text-[10px] text-emerald-500 border-emerald-500/30">Active</Badge>
                  )}
                  {conv.status === "RESOLVED" && (
                    <Badge variant="outline" className="h-5 text-[10px]">Resolved</Badge>
                  )}
                  {!conv.is_human_active && (
                    <div className="flex items-center gap-1 text-[10px] text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">
                      <Bot className="h-3 w-3" /> AI Handling
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
