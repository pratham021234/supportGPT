"use client";

import React, { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Send, User, Bot, Loader2, X, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export default function WidgetPage() {
  const searchParams = useSearchParams();
  const workspaceId = searchParams.get("workspaceId");
  const agentId = searchParams.get("agentId") || "default";
  
  const [config, setConfig] = useState<any>(null);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  
  const [messages, setMessages] = useState<Array<{id: string, sender: string, content: string}>>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    async function initWidget() {
      if (!workspaceId) return;
      
      // 1. Fetch Config
      try {
        const confRes = await fetch(`http://localhost:8000/api/v1/widget/config/${agentId}`);
        const confData = await confRes.json();
        setConfig(confData);
        
        // Notify parent iframe about config to change launcher color
        window.parent.postMessage(JSON.stringify({ type: "supportgpt:config", config: confData }), "*");
      } catch (e) {
        console.error("Failed to load config", e);
      }
      
      // 2. Initialize Session
      try {
        const sesRes = await fetch(`http://localhost:8000/api/v1/widget/session`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ workspace_id: workspaceId, agent_id: agentId })
        });
        const sesData = await sesRes.json();
        setSessionToken(sesData.session_token);
        
        // 3. Start Conversation
        const convRes = await fetch(`http://localhost:8000/api/v1/widget/conversations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_token: sesData.session_token })
        });
        const convData = await convRes.json();
        setConversationId(convData.conversation_id);
        
      } catch(e) {
        console.error("Failed to init session", e);
      }
    }
    
    initWidget();
  }, [workspaceId, agentId]);

  useEffect(() => {
    if (!conversationId) return;
    
    // Connect WebSocket
    const socket = new WebSocket(`ws://localhost:8000/api/v1/conversations/${conversationId}/ws`);
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "message_ack") {
        setMessages(prev => [...prev, { id: Date.now().toString(), sender: data.sender, content: data.content }]);
      } else if (data.type === "agent_typing") {
        setIsTyping(data.status);
      } else if (data.type === "token") {
        setMessages(prev => {
           const lastMsg = prev[prev.length - 1];
           if (lastMsg && lastMsg.sender === "AI_AGENT" && lastMsg.id === "streaming") {
               return [...prev.slice(0, -1), { ...lastMsg, content: lastMsg.content + data.content }];
           } else {
               return [...prev, { id: "streaming", sender: "AI_AGENT", content: data.content }];
           }
        });
      } else if (data.type === "message_complete") {
        setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.id === "streaming") {
                return [...prev.slice(0, -1), { ...lastMsg, id: Date.now().toString() }];
            }
            return prev;
        });
      } else if (data.type === "system_event") {
        setMessages(prev => [...prev, { id: Date.now().toString(), sender: "SYSTEM", content: data.content }]);
      } else if (data.type === "message" && !data.is_internal) {
          // Message from human agent
          setMessages(prev => [...prev, { id: Date.now().toString(), sender: "SUPPORT_AGENT", content: data.content }]);
      }
    };
    
    setWs(socket);
    
    return () => socket.close();
  }, [conversationId]);
  
  // Listen for identify messages from parent
  useEffect(() => {
    const handleMessage = (e: MessageEvent) => {
        try {
            const data = JSON.parse(e.data);
            if (data.type === "supportgpt:identify") {
                // In a real implementation, we would send this payload to a backend endpoint to update the Customer record.
                console.log("Identified user:", data.payload);
            }
        } catch(err) {}
    };
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  const handleSend = () => {
    if (!input.trim() || !ws) return;
    
    // We send via WS instead of POST so it uses realtime_service logic
    ws.send(JSON.stringify({ text: input }));
    setInput("");
  };

  if (!config) return <div className="flex h-full w-full items-center justify-center bg-white/50 backdrop-blur-md"><Loader2 className="animate-spin text-zinc-500" /></div>;

  const closeWidget = () => {
      window.parent.postMessage(JSON.stringify({ type: "supportgpt:close" }), "*");
  };

  return (
    <div className="flex h-screen w-full flex-col bg-white overflow-hidden text-zinc-900 border shadow-2xl sm:rounded-2xl">
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-4 shrink-0 transition-colors"
        style={{ backgroundColor: config.primary_color, color: "#fff" }}
      >
        <div className="flex items-center space-x-3">
            {config.logo_url ? (
                <img src={config.logo_url} alt="Logo" className="w-8 h-8 rounded-full object-cover bg-white" />
            ) : (
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                </div>
            )}
          <div>
            <h1 className="font-semibold text-sm leading-tight">{config.launcher_text}</h1>
            <p className="text-xs opacity-80 leading-tight">Usually replies instantly</p>
          </div>
        </div>
        <button onClick={closeWidget} className="p-1 hover:bg-white/20 rounded-md transition-colors">
            <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-zinc-50 scroll-smooth">
        {/* Welcome Message */}
        <div className="flex items-start space-x-2">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-blue-600" />
            </div>
            <div className="bg-white border rounded-2xl rounded-tl-sm px-4 py-2 shadow-sm text-sm max-w-[85%]">
                {config.welcome_message}
            </div>
        </div>
        
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={cn(
                "flex items-start space-x-2 w-full",
                msg.sender === "CUSTOMER" ? "justify-end" : "justify-start"
            )}
          >
            {msg.sender !== "CUSTOMER" && msg.sender !== "SYSTEM" && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-blue-600" />
                </div>
            )}
            
            <div 
                className={cn(
                    "px-4 py-2 text-sm shadow-sm max-w-[85%]",
                    msg.sender === "CUSTOMER" 
                        ? "bg-zinc-900 text-white rounded-2xl rounded-tr-sm" 
                        : msg.sender === "SYSTEM"
                            ? "bg-amber-50 text-amber-900 border border-amber-200 rounded-xl text-xs mx-auto w-full text-center"
                            : "bg-white border rounded-2xl rounded-tl-sm"
                )}
                style={msg.sender === "CUSTOMER" ? { backgroundColor: config.primary_color } : {}}
            >
                {msg.content}
            </div>
          </div>
        ))}
        
        {isTyping && (
            <div className="flex items-start space-x-2">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-blue-600" />
                </div>
                <div className="bg-white border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm text-sm">
                    <MoreHorizontal className="w-5 h-5 text-zinc-400 animate-pulse" />
                </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 bg-white border-t shrink-0">
        <form 
            className="flex items-center space-x-2 relative"
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        >
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="pr-12 rounded-full border-zinc-200 shadow-sm focus-visible:ring-1"
            disabled={!ws}
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={!input.trim() || !ws}
            className="absolute right-1 top-1 w-8 h-8 rounded-full"
            style={{ backgroundColor: config.primary_color }}
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
        <div className="text-center mt-2">
            <span className="text-[10px] text-zinc-400 font-medium tracking-wide uppercase">Powered by SupportGPT</span>
        </div>
      </div>
    </div>
  );
}
