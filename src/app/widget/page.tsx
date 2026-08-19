"use client";

import React, { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Send, Bot, Loader2, X, MoreHorizontal, Paperclip, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { widgetClient, WidgetConfig } from "@/lib/api/widget-client";
import { API_BASE_URL } from "@/lib/api/client";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  sender: string;
  content: string;
  sources?: any[];
  confidence?: number;
}

export default function WidgetPage() {
  const searchParams = useSearchParams();
  const workspaceId = searchParams.get("workspaceId");
  const agentId = searchParams.get("agentId") || "default";
  
  const [config, setConfig] = useState<WidgetConfig | null>(null);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [hasEscalated, setHasEscalated] = useState(false);
  const [ticketCreated, setTicketCreated] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    async function initWidget() {
      if (!workspaceId) return;
      
      try {
        const confData = await widgetClient.getPublicConfig(agentId);
        setConfig(confData);
        window.parent.postMessage(JSON.stringify({ type: "supportgpt:config", config: confData }), "*");

        // Check Support Hours
        if (confData.support_hours) {
          const day = new Date().toLocaleString('en-US', { weekday: 'long' });
          if (confData.support_hours[day] === "closed") {
             setIsOffline(true);
          }
        }
      } catch (e) {
        console.error("Failed to load config", e);
      }
      
      let token = localStorage.getItem(`sgpt_session_${workspaceId}_${agentId}`);
      
      try {
        if (!token) {
          const sesData = await widgetClient.initSession({ workspace_id: workspaceId, agent_id: agentId });
          token = sesData.session_token;
          localStorage.setItem(`sgpt_session_${workspaceId}_${agentId}`, token);
        }
        setSessionToken(token);
        
        // Load history
        const historyData = await widgetClient.getHistory(token);
        if (historyData.messages && historyData.messages.length > 0) {
            setMessages(historyData.messages.map((m: any) => ({
                id: m.id,
                sender: m.sender_type === "CUSTOMER" ? "CUSTOMER" : "AI_AGENT",
                content: m.content
            })));
        }
        
        const convData = await widgetClient.startConversation(token);
        setConversationId(convData.conversation_id);
      } catch(e) {
        console.error("Failed to init session", e);
        // Clear invalid token and retry once
        if (token) {
            localStorage.removeItem(`sgpt_session_${workspaceId}_${agentId}`);
            // Simple reload for MVP
            window.location.reload();
        }
      }
    }
    
    initWidget();
  }, [workspaceId, agentId]);

  useEffect(() => {
    if (!conversationId) return;
    
    const baseUrl = API_BASE_URL.replace(/^http/, 'ws');
    const socket = new WebSocket(`${baseUrl}/conversations/${conversationId}/ws`);
    
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
                return [...prev.slice(0, -1), { ...lastMsg, id: Date.now().toString(), sources: data.sources, confidence: data.confidence }];
            }
            return prev;
        });
      } else if (data.type === "system_event") {
        setMessages(prev => [...prev, { id: Date.now().toString(), sender: "SYSTEM", content: data.content }]);
      } else if (data.type === "message" && !data.is_internal) {
          setMessages(prev => [...prev, { id: Date.now().toString(), sender: "SUPPORT_AGENT", content: data.content }]);
      }
    };
    
    setWs(socket);
    
    return () => socket.close();
  }, [conversationId]);

  const handleSend = () => {
    if (!input.trim() || !ws) return;
    ws.send(JSON.stringify({ text: input }));
    setInput("");
  };

  const handleSuggestedQuestion = (q: string) => {
    if (!ws) return;
    ws.send(JSON.stringify({ text: q }));
  };

  const handleHandoff = async () => {
    if (!sessionToken) return;
    await widgetClient.handoff(sessionToken);
    setHasEscalated(true);
    setMessages(prev => [...prev, { id: Date.now().toString(), sender: "SYSTEM", content: "You will be connected to the next available agent." }]);
  };

  const handleCreateTicket = async () => {
    if (!sessionToken) return;
    try {
       const res = await widgetClient.createTicket(sessionToken, "Customer requested ticket creation from widget");
       setTicketCreated(res.ticket_number);
       setMessages(prev => [...prev, { id: Date.now().toString(), sender: "SYSTEM", content: `Ticket created: ${res.ticket_number}` }]);
    } catch(e) {}
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      // Mock File Upload
      const file = e.target.files?.[0];
      if (file && ws) {
          setMessages(prev => [...prev, { id: Date.now().toString(), sender: "CUSTOMER", content: `Attached: ${file.name}` }]);
          ws.send(JSON.stringify({ text: `[Customer attached file: ${file.name}]` }));
      }
  };

  const submitFeedback = (msgId: string, isHelpful: boolean) => {
      // Simple mock for MVP to show feedback registered visually
      setMessages(prev => prev.map(m => m.id === msgId ? { ...m, feedback: isHelpful } : m));
      // Real API call:
      // widgetClient.submitFeedback(conversationId, msgId, isHelpful);
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
        style={{ backgroundColor: config.primary_color || '#000000', color: "#fff" }}
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
            <h1 className="font-semibold text-sm leading-tight">{config.launcher_text || "Chat with us"}</h1>
            <p className="text-xs opacity-80 leading-tight">Usually replies instantly</p>
          </div>
        </div>
        <button onClick={closeWidget} className="p-1 hover:bg-white/20 rounded-md transition-colors">
            <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-zinc-50 scroll-smooth">
        {/* Welcome or Offline Message */}
        {isOffline ? (
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-amber-600" />
              </div>
              <div className="bg-white border rounded-2xl rounded-tl-sm px-4 py-2 shadow-sm text-sm max-w-[85%] whitespace-pre-wrap">
                  {config.offline_message}
              </div>
          </div>
        ) : config.welcome_message && (
          <div className="flex items-start space-x-2">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-blue-600" />
              </div>
              <div className="bg-white border rounded-2xl rounded-tl-sm px-4 py-2 shadow-sm text-sm max-w-[85%] whitespace-pre-wrap">
                  {config.welcome_message}
              </div>
          </div>
        )}

        {/* Suggested Questions */}
        {!isOffline && messages.length === 0 && config.suggested_questions && config.suggested_questions.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
                {config.suggested_questions.map((q, i) => (
                    <button key={i} onClick={() => handleSuggestedQuestion(q)} className="text-xs border rounded-full px-3 py-1.5 bg-white shadow-sm hover:bg-zinc-50 transition-colors" style={{ color: config.primary_color || '#000000', borderColor: config.primary_color ? `${config.primary_color}40` : '#00000040' }}>
                        {q}
                    </button>
                ))}
            </div>
        )}
        
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={cn(
                "flex items-start space-x-2 w-full",
                msg.sender === "CUSTOMER" ? "justify-end" : "justify-start"
            )}
          >
            {msg.sender !== "CUSTOMER" && msg.sender !== "SYSTEM" && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-blue-600" />
                </div>
            )}
            
            <div className="max-w-[85%] flex flex-col gap-1">
                <div 
                    className={cn(
                        "px-4 py-2 text-sm shadow-sm whitespace-pre-wrap",
                        msg.sender === "CUSTOMER" 
                            ? "bg-zinc-900 text-white rounded-2xl rounded-tr-sm" 
                            : msg.sender === "SYSTEM"
                                ? "bg-amber-50 text-amber-900 border border-amber-200 rounded-xl text-xs mx-auto text-center"
                                : "bg-white border rounded-2xl rounded-tl-sm prose prose-sm prose-zinc"
                    )}
                    style={msg.sender === "CUSTOMER" ? { backgroundColor: config.primary_color || '#000000' } : {}}
                >
                    {msg.sender === "AI_AGENT" || msg.sender === "SUPPORT_AGENT" ? (
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                    ) : (
                        msg.content
                    )}
                </div>
                
                {/* Confidence and Sources */}
                {(msg.sources && msg.sources.length > 0) || msg.confidence !== undefined ? (
                    <div className="pl-1 pt-1 flex flex-col gap-1">
                        {msg.confidence !== undefined && (
                            <span className="text-[10px] text-zinc-500 font-medium">Confidence: {(msg.confidence * 100).toFixed(1)}%</span>
                        )}
                        {msg.sources && msg.sources.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                                {msg.sources.map((src, i) => (
                                    <a key={i} href={src.url} target="_blank" rel="noreferrer" className="text-[10px] text-blue-600 border border-blue-200 bg-blue-50 px-1.5 py-0.5 rounded truncate max-w-[150px] inline-block hover:bg-blue-100">
                                        📄 {src.title || "Source"}
                                    </a>
                                ))}
                            </div>
                        )}
                    </div>
                ) : null}

                {/* Feedback System */}
                {(msg.sender === "AI_AGENT" || msg.sender === "SUPPORT_AGENT") && (msg.id !== "streaming") && (
                    <div className="pl-2 pt-1 flex items-center gap-2">
                        <button 
                            onClick={() => submitFeedback(msg.id, true)} 
                            className={cn("text-[10px] flex items-center gap-1 hover:text-emerald-600 transition-colors", (msg as any).feedback === true ? "text-emerald-600" : "text-zinc-400")}
                            title="Helpful"
                        >
                            👍
                        </button>
                        <button 
                            onClick={() => submitFeedback(msg.id, false)} 
                            className={cn("text-[10px] flex items-center gap-1 hover:text-rose-600 transition-colors", (msg as any).feedback === false ? "text-rose-600" : "text-zinc-400")}
                            title="Not Helpful"
                        >
                            👎
                        </button>
                    </div>
                )}
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
          <div className="absolute left-1 top-1 w-8 h-8 flex items-center justify-center overflow-hidden cursor-pointer hover:bg-zinc-100 rounded-full z-10">
              <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleFileUpload} />
              <Paperclip className="w-4 h-4 text-zinc-500" />
          </div>
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="pl-10 pr-12 rounded-full border-zinc-200 shadow-sm focus-visible:ring-1"
            disabled={!ws}
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={!input.trim() || !ws}
            className="absolute right-1 top-1 w-8 h-8 rounded-full"
            style={{ backgroundColor: config.primary_color || '#000000' }}
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
        <div className="text-center mt-2 flex justify-between items-center px-1 flex-wrap gap-1">
            <span className="text-[10px] text-zinc-400 font-medium tracking-wide uppercase flex-shrink-0">Powered by SupportGPT</span>
            <div className="flex items-center gap-2">
                {!ticketCreated && (
                    <Button variant="link" className="text-[10px] h-auto p-0 text-zinc-400 font-medium" onClick={handleCreateTicket}>Create Ticket</Button>
                )}
                {ticketCreated && (
                    <span className="text-[10px] text-emerald-600 flex items-center gap-1 font-medium"><CheckCircle className="w-3 h-3"/> {ticketCreated}</span>
                )}
                {!hasEscalated && (
                    <Button variant="link" className="text-[10px] h-auto p-0 text-zinc-500 font-medium" onClick={handleHandoff}>Talk to human</Button>
                )}
            </div>
        </div>
      </div>
    </div>
  );
}
