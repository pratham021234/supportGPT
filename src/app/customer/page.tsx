"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Ticket, MessageSquare, Bot, Clock, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function CustomerPortalPage() {
  const [email, setEmail] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [tickets, setTickets] = useState<any[]>([]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      setTimeout(() => {
        setTickets([
          {
            id: "TKT-1234",
            title: "Cannot access billing page",
            status: "OPEN",
            created_at: new Date().toISOString(),
            priority: "HIGH"
          },
          {
            id: "TKT-1235",
            title: "How to upgrade?",
            status: "RESOLVED",
            created_at: new Date(Date.now() - 86400000).toISOString(),
            priority: "LOW"
          }
        ]);
        setIsSubmitted(true);
        setIsLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error(error);
      setIsLoading(false);
    }
  };

  if (!isSubmitted) {
    return (
      <div className="min-h-screen bg-muted/20 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-4">
              <Bot className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold">Support Portal</h1>
            <p className="text-muted-foreground mt-2">Enter your email to view your tickets and conversations.</p>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="you@example.com" 
                    required 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Checking..." : "Continue"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/20 flex flex-col">
      <header className="bg-background border-b h-16 flex items-center px-6 justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-primary" />
          <span className="font-bold">Support Portal</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{email}</span>
          <Button variant="ghost" size="sm" onClick={() => setIsSubmitted(false)}>Sign out</Button>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-5xl mx-auto w-full grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">Your Tickets</h2>
            <Button size="sm">Create New Ticket</Button>
          </div>
          
          <div className="space-y-4">
            {tickets.map(ticket => (
              <Card key={ticket.id} className="hover:border-primary/50 cursor-pointer transition-colors">
                <CardContent className="p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm text-muted-foreground">{ticket.id}</span>
                      <Badge variant={ticket.status === "RESOLVED" ? "secondary" : "default"} className={ticket.status === "OPEN" ? "bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20" : ""}>
                        {ticket.status}
                      </Badge>
                      {ticket.priority === "HIGH" && <Badge variant="destructive" className="h-5 text-[10px]">High Priority</Badge>}
                    </div>
                    <h3 className="font-semibold text-lg">{ticket.title}</h3>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" /> Updated {new Date(ticket.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Button variant="outline" size="sm" className="shrink-0 gap-1">
                    View Details <ExternalLink className="w-3 h-3" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
        
        <div className="space-y-6">
          <h2 className="text-xl font-bold">Recent Conversations</h2>
          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                <div className="p-4 flex gap-3 hover:bg-muted/50 cursor-pointer transition-colors">
                  <div className="mt-0.5">
                    <MessageSquare className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium line-clamp-1">Chat about API rate limits</p>
                    <p className="text-xs text-muted-foreground mt-1">Yesterday</p>
                  </div>
                </div>
                <div className="p-4 flex gap-3 hover:bg-muted/50 cursor-pointer transition-colors">
                  <div className="mt-0.5">
                    <MessageSquare className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium line-clamp-1">Checking upgrade status</p>
                    <p className="text-xs text-muted-foreground mt-1">Last week</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
