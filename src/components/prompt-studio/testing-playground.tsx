"use client";

import { useState } from "react";
import { useTestAgent } from "@/lib/api/prompt-studio";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Play, MessageSquare, Loader2, Zap, AlertTriangle, ShieldCheck } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface TestingPlaygroundProps {
  agentId: string;
}

export function TestingPlayground({ agentId }: TestingPlaygroundProps) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Array<{role: 'user' | 'agent', content: string, meta?: any}>>([]);
  
  const { mutate: testAgent, isPending } = useTestAgent(agentId);

  const handleTest = () => {
    if (!query.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    const currentQuery = query;
    setQuery("");

    testAgent(currentQuery, {
      onSuccess: (data) => {
        setMessages(prev => [...prev, { 
          role: 'agent', 
          content: data.answer,
          meta: {
            confidence: data.confidence,
            latency: data.latency_ms,
            sources: data.sources,
            escalated: data.requires_escalation
          }
        }]);
      }
    });
  };

  return (
    <div className="flex flex-col h-full border-l bg-background shadow-sm w-80 lg:w-96 shrink-0 z-10">
      <div className="h-14 border-b bg-muted/30 flex items-center px-4 justify-between shrink-0">
        <div className="flex items-center gap-2 font-semibold text-sm">
          <Play className="h-4 w-4 text-primary fill-primary/20" /> Playground
        </div>
        <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => setMessages([])}>
          Clear
        </Button>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4 pb-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 text-muted-foreground mt-20">
              <BotIcon className="w-12 h-12 mb-4 opacity-20" />
              <p className="text-sm">Enter a customer query below to test this agent's response and configuration.</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex flex-col gap-1 max-w-[90%] ${msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}>
                <div className={`px-3 py-2 rounded-xl text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted border'}`}>
                  {msg.content}
                </div>
                
                {msg.role === 'agent' && msg.meta && (
                  <div className="flex flex-wrap gap-2 mt-1">
                    <Badge variant="outline" className="text-[10px] h-5 px-1.5 font-normal gap-1">
                      <Zap className="w-3 h-3 text-amber-500" /> {msg.meta.latency}ms
                    </Badge>
                    <Badge variant="outline" className={`text-[10px] h-5 px-1.5 font-normal gap-1 ${msg.meta.confidence < 70 ? 'text-amber-600 border-amber-200' : 'text-emerald-600 border-emerald-200'}`}>
                      <ShieldCheck className="w-3 h-3" /> {(msg.meta.confidence).toFixed(1)}% Conf
                    </Badge>
                    {msg.meta.escalated && (
                      <Badge variant="destructive" className="text-[10px] h-5 px-1.5 font-normal gap-1">
                        <AlertTriangle className="w-3 h-3" /> Escalated
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
          {isPending && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground mr-auto bg-muted px-3 py-2 rounded-xl">
              <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
            </div>
          )}
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t bg-background shrink-0">
        <div className="relative">
          <Input 
            placeholder="Test a query..." 
            className="pr-10 bg-muted/50" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleTest()}
            disabled={isPending}
          />
          <Button 
            size="icon" 
            variant="ghost" 
            className="absolute right-0 top-0 h-full rounded-l-none text-primary hover:bg-transparent"
            onClick={handleTest}
            disabled={isPending || !query.trim()}
          >
            <MessageSquare className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function BotIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 8V4H8" />
      <rect width="16" height="12" x="4" y="8" rx="2" />
      <path d="M2 14h2" />
      <path d="M20 14h2" />
      <path d="M15 13v2" />
      <path d="M9 13v2" />
    </svg>
  );
}
