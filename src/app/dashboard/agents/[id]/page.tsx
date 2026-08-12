"use client";

import { useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useAgent, usePublishAgent } from "@/lib/api/agents";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PromptConfig } from "@/components/agents/prompt-config";
import { ModelSelector } from "@/components/agents/model-selector";
import { EscalationRules } from "@/components/agents/escalation-rules";
import { KnowledgeAssignment } from "@/components/agents/knowledge-assignment";
import { AgentPlayground } from "@/components/agents/agent-playground";
import { AgentAnalytics } from "@/components/agents/agent-analytics";
import { AgentActivity } from "@/components/agents/agent-activity";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, Play, Settings, Database, Activity, Beaker, MoreVertical, Copy, Archive, Trash2 } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { useCloneAgent, useArchiveAgent } from "@/lib/api/agents";

export default function AgentDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const agentId = params.id as string;
  const initialTab = searchParams.get("tab") || "configuration";

  const { data: agent, isLoading, isError } = useAgent(agentId);
  const { mutate: publishAgent, isPending: isPublishing } = usePublishAgent(agentId);
  const { mutate: cloneAgent } = useCloneAgent();
  const { mutate: archiveAgent } = useArchiveAgent();

  const [activeTab, setActiveTab] = useState(initialTab);

  const handleTabChange = (val: string) => {
    setActiveTab(val);
    router.replace(`/dashboard/agents/${agentId}?tab=${val}`, { scroll: false });
  };

  const handlePublish = () => {
    publishAgent(undefined, {
      onSuccess: () => {
        // Could show a toast here
      }
    });
  };

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 pb-10">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div className="space-y-2">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-[500px] w-full" />
      </div>
    );
  }

  if (isError || !agent) {
    return (
      <div className="p-8 text-center text-muted-foreground border rounded-lg">
        Failed to load agent. Please return to the <Link href="/dashboard/agents" className="text-primary underline">Agents list</Link>.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 pb-10">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/agents">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{agent.name}</h1>
            <Badge variant={agent.status === "ACTIVE" ? "default" : "secondary"} className={
              agent.status === "ACTIVE" ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20" : ""
            }>
              {agent.status}
            </Badge>
            <Badge variant="outline" className="capitalize">{agent.agent_type}</Badge>
          </div>
          <p className="text-muted-foreground">{agent.description || "No description provided."}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handlePublish} disabled={isPublishing}>
            <Play className="h-4 w-4 mr-2" />
            {isPublishing ? "Publishing..." : "Publish Version"}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger render={
              <Button variant="outline" size="icon">
                <MoreVertical className="h-4 w-4" />
              </Button>
            } />
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => cloneAgent(agentId)} className="cursor-pointer">
                <Copy className="h-4 w-4 mr-2" /> Duplicate Agent
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => archiveAgent(agentId)} className="cursor-pointer text-destructive focus:text-destructive">
                <Archive className="h-4 w-4 mr-2" /> Archive Agent
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-4 md:w-[600px] mb-6">
          <TabsTrigger value="configuration" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            <span className="hidden sm:inline">Config</span>
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            <span className="hidden sm:inline">Knowledge</span>
          </TabsTrigger>
          <TabsTrigger value="testing" className="flex items-center gap-2">
            <Beaker className="h-4 w-4" />
            <span className="hidden sm:inline">Playground</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <span className="hidden sm:inline">Analytics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="configuration" className="space-y-6 mt-0">
          <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
            <div className="space-y-6">
              <PromptConfig agentId={agentId} />
              <EscalationRules agentId={agentId} />
            </div>
            <div className="space-y-6">
              <ModelSelector agentId={agentId} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="knowledge" className="mt-0">
          <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
            <KnowledgeAssignment agentId={agentId} />
            <div className="space-y-6">
              {/* Optional: we can put a small widget here, like "Knowledge Health" */}
              <div className="p-4 border rounded-lg bg-muted/20">
                <h3 className="font-semibold mb-2">How Knowledge Works</h3>
                <p className="text-sm text-muted-foreground">
                  The agent will search through the assigned documents when answering a user's question. 
                  Make sure to provide high-quality documents to improve accuracy.
                </p>
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="testing" className="mt-0">
          <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
            <AgentPlayground agentId={agentId} />
            <div className="space-y-6">
              <div className="p-4 border rounded-lg bg-muted/20">
                <h3 className="font-semibold mb-2">Testing Tips</h3>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>Ask questions that require knowledge from assigned documents.</li>
                  <li>Check the confidence score to ensure it meets your escalation thresholds.</li>
                  <li>Verify the tone matches your Prompt Configuration.</li>
                </ul>
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6 mt-0">
          <AgentAnalytics agentId={agentId} />
          <AgentActivity agentId={agentId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
