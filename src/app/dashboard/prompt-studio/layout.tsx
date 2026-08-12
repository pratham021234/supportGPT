"use client";

import { useState } from "react";
import { usePromptStudioAgents } from "@/lib/api/prompt-studio";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Bot, Plus, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export default function PromptStudioLayout({ children }: { children: React.ReactNode }) {
  const { data: agents, isLoading } = usePromptStudioAgents();
  const [searchTerm, setSearchTerm] = useState("");

  const filteredAgents = agents?.filter(a => a.name.toLowerCase().includes(searchTerm.toLowerCase())) || [];

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] border rounded-xl bg-background overflow-hidden">
      <div className="flex h-full">
        {/* Left Sidebar: Agent Selector */}
        <div className="w-64 border-r bg-muted/20 flex flex-col shrink-0">
          <div className="p-4 border-b space-y-4 shrink-0">
            <h2 className="font-semibold text-lg flex items-center gap-2">
              <Bot className="w-5 h-5 text-primary" /> Prompt Studio
            </h2>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search agents..."
                className="pl-8 bg-background h-9"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {isLoading ? (
              <div className="space-y-2 p-2">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : filteredAgents.length === 0 ? (
              <div className="text-sm text-muted-foreground text-center p-4">No agents found</div>
            ) : (
              <div className="space-y-1">
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Active Agents
                </div>
                {filteredAgents.map((agent) => {
                  const isActive = false; // We'll manage active state via URL or Context in page.tsx
                  return (
                    <Button
                      key={agent.id}
                      variant="ghost"
                      className="w-full justify-start font-normal"
                      onClick={() => {
                        // For MVP without complex routing, we will just pass a query param
                        window.history.pushState(null, '', `?agent=${agent.id}`);
                        window.dispatchEvent(new Event('popstate'));
                      }}
                    >
                      <span className="truncate">{agent.name}</span>
                    </Button>
                  );
                })}
              </div>
            )}
          </div>
          <div className="p-4 border-t shrink-0">
            <Button variant="outline" className="w-full justify-start text-muted-foreground">
              <Plus className="w-4 h-4 mr-2" /> New Agent
            </Button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {children}
        </div>
      </div>
    </div>
  );
}
