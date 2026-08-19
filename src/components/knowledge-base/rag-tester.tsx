"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Send, Bot, User, CheckCircle2, AlertTriangle, Clock } from "lucide-react";
import { useAuth } from "@/lib/auth/auth-context";

interface Citation {
  chunk_id: string;
  claim: string;
  document_title?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: number;
  latency?: number;
  isStreaming?: boolean;
}

export function RAGTester() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { session } = useAuth();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    const startTime = Date.now();

    // Add empty assistant message
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", isStreaming: true }
    ]);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rag/query/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({ query: userMessage.content })
      });

      if (!response.ok) throw new Error("Failed to connect to RAG engine");
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      
      if (!reader) throw new Error("No reader");

      let currentAnswer = "";
      let confidence = 0;
      let citations: Citation[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim();
            if (dataStr === "[DONE]") {
              break;
            }
            if (!dataStr) continue;
            
            try {
              const event = JSON.parse(dataStr);
              if (event.event === "generation_chunk" && event.data.text) {
                currentAnswer += event.data.text;
                setMessages((prev) => {
                  const newMsgs = [...prev];
                  newMsgs[newMsgs.length - 1].content = currentAnswer;
                  return newMsgs;
                });
              } else if (event.event === "generation" && event.data.answer) {
                // Non-streaming fallback
                currentAnswer = event.data.answer;
                setMessages((prev) => {
                  const newMsgs = [...prev];
                  newMsgs[newMsgs.length - 1].content = currentAnswer;
                  return newMsgs;
                });
              } else if (event.event === "validation") {
                confidence = event.data.confidence_score;
              }
            } catch (e) {
              console.error("Failed to parse SSE JSON", e);
            }
          }
        }
      }
      
      const latencyMs = Date.now() - startTime;
      
      setMessages((prev) => {
        const newMsgs = [...prev];
        const last = newMsgs[newMsgs.length - 1];
        last.isStreaming = false;
        last.confidence = confidence;
        last.latency = latencyMs;
        // In real app, we would parse citations from backend. Mocking empty list for UI.
        last.citations = []; 
        return newMsgs;
      });
      
    } catch (error) {
      console.error(error);
      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].content = "Error: Failed to fetch response.";
        newMsgs[newMsgs.length - 1].isStreaming = false;
        return newMsgs;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full flex flex-col h-[500px] border-primary/20 shadow-lg">
      <CardHeader className="bg-muted/30 border-b pb-4">
        <CardTitle className="text-lg flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          RAG Engine Tester
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50 space-y-4 py-10">
              <Bot className="h-12 w-12" />
              <p>Ask a question to test semantic search and response generation.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  {msg.role === "assistant" && (
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div className={`flex flex-col gap-1 max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
                    <div className={`px-4 py-2 rounded-lg text-sm ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                      {msg.content || (msg.isStreaming ? <Loader2 className="h-4 w-4 animate-spin" /> : null)}
                    </div>
                    {msg.role === "assistant" && !msg.isStreaming && (
                      <div className="flex flex-wrap items-center gap-2 mt-1">
                        {msg.confidence !== undefined && (
                          <Badge variant={msg.confidence > 70 ? "secondary" : "destructive"} className="text-[10px] gap-1 px-1.5 py-0 shadow-none">
                            {msg.confidence > 70 ? <CheckCircle2 className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
                            {msg.confidence}% Confidence
                          </Badge>
                        )}
                        {msg.latency !== undefined && (
                          <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {msg.latency}ms
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                      <User className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
        <div className="p-4 border-t bg-muted/10">
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Test semantic retrieval..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
