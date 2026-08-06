import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Plus, Settings2, Sparkles, MessageSquare, ArrowRight } from "lucide-react";
import Link from "next/link";

const agents = [
  {
    id: "agent_1",
    name: "Customer Support Agent",
    description: "Main support agent for handling general inquiries, billing questions, and password resets.",
    model: "gpt-4o",
    sources: 42,
    status: "Active",
    conversations: 8234
  },
  {
    id: "agent_2",
    name: "Technical Support",
    description: "Specialized agent trained on API documentation and developer guides.",
    model: "claude-3-5-sonnet",
    sources: 15,
    status: "Active",
    conversations: 1450
  },
  {
    id: "agent_3",
    name: "Sales Assistant",
    description: "Pre-sales agent designed to qualify leads and answer pricing questions.",
    model: "gemini-1.5-pro",
    sources: 8,
    status: "Draft",
    conversations: 0
  }
];

export default function AgentsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Agents</h1>
          <p className="text-muted-foreground">
            Build and manage your fleet of AI customer support agents.
          </p>
        </div>
        <Button className="shrink-0 gap-2">
          <Plus className="h-4 w-4" />
          Create Agent
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <Card key={agent.id} className="flex flex-col border bg-background shadow-sm transition-all hover:shadow-md">
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                </div>
                <Badge variant={agent.status === "Active" ? "default" : "secondary"} className={
                  agent.status === "Active" ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20" : ""
                }>
                  {agent.status}
                </Badge>
              </div>
              <CardTitle className="mt-4 text-xl">{agent.name}</CardTitle>
              <CardDescription className="line-clamp-2 h-10">
                {agent.description}
              </CardDescription>
            </CardHeader>
            <CardContent className="pb-4 flex-1">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex flex-col gap-1">
                  <span className="text-muted-foreground flex items-center gap-1">
                    <Sparkles className="h-3 w-3" /> Model
                  </span>
                  <span className="font-medium font-mono text-xs">{agent.model}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-muted-foreground flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" /> Chats
                  </span>
                  <span className="font-medium">{agent.conversations.toLocaleString()}</span>
                </div>
              </div>
            </CardContent>
            <div className="border-t px-6 py-4 flex items-center justify-between bg-muted/20">
              <span className="text-xs text-muted-foreground font-medium">
                {agent.sources} Knowledge Sources
              </span>
              <div className="flex gap-2">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                  <Settings2 className="h-4 w-4" />
                </Button>
                <Link href={`/dashboard/prompt-studio?agent=${agent.id}`}>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
