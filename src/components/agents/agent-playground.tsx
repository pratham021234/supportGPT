"use client";

import { useState, useRef, useEffect } from "react";
import { useTestAgent } from "@/lib/api/agents";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, Send, Loader2, Gauge, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  latency?: number;
  sources?: any[];
}

export function AgentPlayground({ agentId }: { agentId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { mutate: testAgent, isPending } = useTestAgent(agentId);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isPending]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");

    testAgent(input, {
      onSuccess: (data) => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.answer,
          confidence: data.confidence,
          latency: data.latency_ms,
          sources: data.sources,
        };
        setMessages(prev => [...prev, aiMessage]);
      },
      onError: (err) => {
        const errorMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Error: ${(err as any)?.message || "Failed to reach agent backend."}`,
        };
        setMessages(prev => [...prev, errorMsg]);
      }
    });
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="pb-4 border-b">
        <CardTitle>Testing Playground</CardTitle>
        <CardDescription>Chat with your agent to verify prompts and knowledge retrieval.</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-4">
              <div className="bg-primary/10 p-4 rounded-full">
                <Bot className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="font-medium">Playground Ready</p>
                <p className="text-sm text-muted-foreground max-w-sm mt-1">
                  Send a message to test how the agent responds based on its current configuration.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 max-w-[85%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : ""}`}>
                  <div className={`flex shrink-0 h-8 w-8 items-center justify-center rounded-full ${msg.role === "user" ? "bg-muted" : "bg-primary text-primary-foreground"}`}>
                    {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  <div className={`flex flex-col gap-1.5 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                    <div className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                      msg.role === "user" ? "bg-primary text-primary-foreground rounded-tr-sm" : "bg-muted rounded-tl-sm"
                    }`}>
                      {msg.content}
                    </div>
                    {msg.role === "assistant" && msg.latency && (
                      <div className="flex items-center gap-3 mt-1">
                        <Badge variant="outline" className="text-[10px] font-normal flex items-center gap-1 border-emerald-500/30 text-emerald-600 bg-emerald-500/5">
                          <CheckCircle2 className="h-3 w-3" />
                          {(msg.confidence! * 100).toFixed(1)}% Confidence
                        </Badge>
                        <Badge variant="outline" className="text-[10px] font-normal flex items-center gap-1 border-muted-foreground/30 text-muted-foreground">
                          <Gauge className="h-3 w-3" />
                          {msg.latency}ms
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isPending && (
                <div className="flex gap-3 max-w-[85%]">
                  <div className="flex shrink-0 h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="bg-muted px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Agent is thinking...</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
        <div className="p-4 border-t bg-background">
          <form onSubmit={handleSend} className="flex gap-2">
            <Input 
              placeholder="Type a test message..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isPending}
              className="flex-1"
            />
            <Button type="submit" size="icon" disabled={!input.trim() || isPending}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
