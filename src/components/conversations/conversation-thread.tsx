"use client";

import { useRef, useEffect, useState } from "react";
import { useConversation, useMessages, useSendMessage, useAssignConversation, useResolveConversation } from "@/lib/api/conversations";
import { useConversationWebSocket } from "@/hooks/use-websocket";
import { useAuthStore } from "@/store/authStore";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { MoreVertical, Send, Bot, CheckCircle2, ShieldAlert, FileText, Lock, Paperclip } from "lucide-react";

export function ConversationThread({ conversationId }: { conversationId: string | null }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [inputText, setInputText] = useState("");
  const [isInternal, setIsInternal] = useState(false);

  const { data: conversation, isLoading: isLoadingConv } = useConversation(conversationId);
  const { data: messages, isLoading: isLoadingMsgs } = useMessages(conversationId);
  
  const { mutate: sendMessage, isPending: isSending } = useSendMessage(conversationId || "");
  const { mutate: assignToHuman, isPending: isAssigning } = useAssignConversation(conversationId || "");
  const { mutate: resolveConv, isPending: isResolving } = useResolveConversation(conversationId || "");
  const user = useAuthStore(state => state.user);

  // Initialize WebSocket connection for live updates
  const { isConnected, isTyping, streamingMessage } = useConversationWebSocket(conversationId);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isSending) return;
    
    sendMessage({ content: inputText, is_internal: isInternal }, {
      onSuccess: () => {
        setInputText("");
      }
    });
  };

  const handleTakeOver = () => {
    if (user?.id) {
      assignToHuman(user.id);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && !isSending) {
      // Stub: in a real app, upload file to s3, get URL, then send message with attachment URL
      sendMessage({ content: `[Agent attached file: ${file.name}]`, is_internal: isInternal });
    }
  };

  if (!conversationId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-muted/10 p-8 text-center text-muted-foreground h-full">
        <div className="bg-background p-4 rounded-full border mb-4 shadow-sm">
          <Bot className="h-8 w-8 text-muted-foreground/50" />
        </div>
        <p className="font-medium text-foreground mb-1">No Conversation Selected</p>
        <p className="text-sm">Select a conversation from the list to view the thread.</p>
      </div>
    );
  }

  if (isLoadingConv) {
    return (
      <div className="flex-1 flex flex-col h-full bg-background">
        <div className="h-16 border-b flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div>
              <Skeleton className="h-4 w-32 mb-2" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>
        </div>
        <div className="flex-1 p-6 space-y-6">
          <Skeleton className="h-16 w-2/3 rounded-xl" />
          <Skeleton className="h-16 w-2/3 rounded-xl ml-auto" />
          <Skeleton className="h-16 w-1/2 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!conversation) return null;

  return (
    <div className="flex-1 flex flex-col h-full bg-background relative">
      {/* Header */}
      <div className="h-16 border-b flex items-center justify-between px-4 sm:px-6 shrink-0 bg-background/95 backdrop-blur z-10">
        <div className="flex items-center gap-4 overflow-hidden">
          <Avatar className="h-10 w-10 shrink-0">
            <AvatarFallback>{conversation.customer?.name?.[0]?.toUpperCase() || "U"}</AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <h3 className="font-semibold text-sm truncate">
              {conversation.customer?.name || conversation.customer?.email || "Unknown User"}
            </h3>
            <div className="flex items-center gap-2 text-xs">
              {!conversation.is_human_active ? (
                <span className="flex items-center gap-1.5 text-emerald-500">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  AI is handling
                </span>
              ) : (
                <span className="text-amber-500">Agent Active</span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {!conversation.is_human_active && conversation.status !== "RESOLVED" && (
            <Button variant="outline" size="sm" onClick={handleTakeOver} disabled={isAssigning} className="hidden sm:flex">
              Take Over
            </Button>
          )}
          {conversation.status !== "RESOLVED" && (
            <Button variant="outline" size="sm" onClick={() => resolveConv()} disabled={isResolving} className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50">
              <CheckCircle2 className="h-4 w-4 mr-2 hidden sm:block" />
              Resolve
            </Button>
          )}
          <Button variant="ghost" size="icon">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Thread */}
      <ScrollArea className="flex-1 p-4 sm:p-6" ref={scrollRef}>
        <div className="space-y-6">
          <div className="flex justify-center">
            <Badge variant="outline" className="text-xs font-normal text-muted-foreground bg-background">
              Conversation Started • {new Date(conversation.started_at).toLocaleString()}
            </Badge>
          </div>
          
          {isLoadingMsgs ? (
            <div className="flex justify-center py-4">
              <div className="animate-pulse flex space-x-2 items-center text-muted-foreground">
                <div className="h-2 w-2 bg-muted-foreground/30 rounded-full"></div>
                <div className="h-2 w-2 bg-muted-foreground/30 rounded-full"></div>
                <div className="h-2 w-2 bg-muted-foreground/30 rounded-full"></div>
              </div>
            </div>
          ) : (
            messages?.map((msg) => {
              // System Messages
              if (msg.sender_type === "SYSTEM" || msg.message_type === "SYSTEM_EVENT") {
                const isInternalNote = msg.message_type === "TEXT" && msg.sender_type === "SYSTEM";
                
                if (isInternalNote) {
                  return (
                    <div key={msg.id} className="flex flex-col items-center my-4">
                      <div className="bg-amber-500/10 border border-amber-500/20 text-amber-700 px-4 py-2 rounded-lg text-sm max-w-[85%] w-full flex gap-3">
                        <Lock className="h-4 w-4 shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="font-semibold text-xs mb-1 opacity-70">Internal Note • {new Date(msg.created_at).toLocaleTimeString()}</p>
                          <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                      </div>
                    </div>
                  );
                }

                return (
                  <div key={msg.id} className="flex justify-center my-4">
                    <Badge variant="outline" className="text-xs font-normal text-muted-foreground bg-muted/30 py-1 px-3">
                      {msg.content} • {new Date(msg.created_at).toLocaleTimeString()}
                    </Badge>
                  </div>
                );
              }

              const isCustomer = msg.sender_type === "CUSTOMER";
              const isAI = msg.sender_type === "AI";
              
              return (
                <div key={msg.id} className={`flex items-end gap-3 ${isCustomer ? "" : "flex-row-reverse"}`}>
                  <Avatar className={`h-8 w-8 shrink-0 ${isAI ? "bg-primary/10" : ""}`}>
                    <AvatarFallback className={isAI ? "bg-transparent text-primary" : ""}>
                      {isAI ? <Bot className="h-5 w-5" /> : (conversation.customer?.name?.[0]?.toUpperCase() || "U")}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className={`grid gap-1 max-w-[85%] ${isCustomer ? "" : "text-right"}`}>
                    <div className={`font-semibold text-sm flex items-center gap-2 ${isCustomer ? "" : "justify-end"}`}>
                      {isCustomer ? (
                        <>
                          {conversation.customer?.name || "Customer"} 
                          <span className="text-xs text-muted-foreground font-normal">{new Date(msg.created_at).toLocaleTimeString()}</span>
                        </>
                      ) : (
                        <>
                          <span className="text-xs text-muted-foreground font-normal">{new Date(msg.created_at).toLocaleTimeString()}</span>
                          {isAI ? "Support AI" : "Support Agent"}
                        </>
                      )}
                    </div>
                    
                    <div className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                      isCustomer 
                        ? "bg-muted rounded-bl-sm" 
                        : "bg-primary text-primary-foreground rounded-br-sm text-left"
                    }`}>
                      {msg.content}
                    </div>
                    
                    {/* AI Metadata Display */}
                    {isAI && msg.metadata_ && (
                      <div className="flex flex-wrap items-center justify-end gap-2 mt-1 text-xs text-muted-foreground">
                        {msg.metadata_.confidence !== undefined && (
                          <span className={`flex items-center gap-1 ${(msg.metadata_.confidence < 0.7) ? "text-amber-500" : ""}`}>
                            Confidence: {(msg.metadata_.confidence * 100).toFixed(0)}%
                          </span>
                        )}
                        {msg.metadata_.sources && msg.metadata_.sources.length > 0 && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <FileText className="h-3 w-3" /> {msg.metadata_.sources.length} sources
                            </span>
                          </>
                        )}
                        {msg.metadata_.latency_ms !== undefined && (
                          <>
                            <span>•</span>
                            <span>{msg.metadata_.latency_ms}ms</span>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}

          {/* Streaming Message Display */}
          {(isTyping || streamingMessage) && (
            <div className="flex items-end gap-3">
              <Avatar className="h-8 w-8 shrink-0 bg-primary/10">
                <AvatarFallback className="bg-transparent text-primary">
                  <Bot className="h-5 w-5" />
                </AvatarFallback>
              </Avatar>
              <div className="grid gap-1 max-w-[85%] text-right">
                <div className="font-semibold text-sm flex items-center gap-2 justify-end">
                  Support AI
                </div>
                <div className="px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap bg-primary text-primary-foreground rounded-br-sm text-left">
                  {streamingMessage || (isTyping ? "..." : "")}
                  <span className="inline-block w-1 h-3 ml-1 bg-primary-foreground animate-pulse" />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t bg-background shrink-0">
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2">
            {!conversation.is_human_active && conversation.status !== "RESOLVED" && (
              <span className="text-xs text-muted-foreground flex items-center gap-1.5">
                <Bot className="h-3.5 w-3.5" /> AI is currently handling this conversation.
              </span>
            )}
            {conversation.status === "RESOLVED" && (
              <span className="text-xs text-muted-foreground flex items-center gap-1.5 text-emerald-600">
                <CheckCircle2 className="h-3.5 w-3.5" /> This conversation has been resolved.
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Switch id="internal-note" checked={isInternal} onCheckedChange={setIsInternal} />
            <Label htmlFor="internal-note" className={`text-xs cursor-pointer ${isInternal ? "text-amber-600 font-semibold" : "text-muted-foreground"}`}>
              Internal Note
            </Label>
          </div>
        </div>
        
        <form onSubmit={handleSend} className="relative flex items-center">
          <div className="absolute left-2 top-2 h-8 w-8 flex items-center justify-center cursor-pointer hover:bg-muted rounded-full z-10 overflow-hidden">
             <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleFileUpload} />
             <Paperclip className="h-4 w-4 text-muted-foreground" />
          </div>
          <Input 
            placeholder={isInternal ? "Type a private internal note..." : "Type a reply to the customer..."} 
            className={`pl-12 pr-24 py-6 ${isInternal ? "bg-amber-500/5 border-amber-500/30 focus-visible:ring-amber-500" : ""}`}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={conversation.status === "RESOLVED" || isSending}
          />
          <Button 
            type="submit" 
            size="sm" 
            className={`absolute right-2 top-2 h-8 ${isInternal ? "bg-amber-600 hover:bg-amber-700" : ""}`} 
            disabled={!inputText.trim() || conversation.status === "RESOLVED" || isSending}
          >
            {isSending ? "..." : (isInternal ? "Save Note" : "Send")} <Send className="ml-2 h-3 w-3" />
          </Button>
        </form>
      </div>
    </div>
  );
}
