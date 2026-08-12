"use client";

import { useState, useEffect } from "react";
import { useAgent, useUpdateAgentPrompt } from "@/lib/api/agents";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, CheckCircle2 } from "lucide-react";

export function PromptConfig({ agentId }: { agentId: string }) {
  const { data: agent } = useAgent(agentId);
  const { mutate: updatePrompt, isPending, isSuccess, isError, error } = useUpdateAgentPrompt(agentId);
  
  const [systemPrompt, setSystemPrompt] = useState("");
  const [welcomeMessage, setWelcomeMessage] = useState("");
  const [fallbackMessage, setFallbackMessage] = useState("");

  // Initialize state once agent loads
  useEffect(() => {
    if (agent) {
      // In a real app, these would come from agent.prompt_config. Mocking logic to avoid breaking if not present.
      setSystemPrompt((agent as any).system_prompt || "You are a helpful AI assistant for SupportGPT.");
      setWelcomeMessage((agent as any).welcome_message || "Hi, how can I help you today?");
      setFallbackMessage((agent as any).fallback_message || "I'm sorry, I don't know the answer to that. Let me connect you with a human.");
    }
  }, [agent]);

  const handleSave = () => {
    updatePrompt({
      system_prompt: systemPrompt,
      welcome_message: welcomeMessage,
      fallback_message: fallbackMessage,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Prompt Configuration</CardTitle>
        <CardDescription>Control how your agent behaves and responds to users.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>System Prompt / Core Instructions</Label>
          <Textarea 
            className="min-h-[150px] font-mono text-sm"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="You are a helpful AI assistant..."
          />
          <p className="text-xs text-muted-foreground">
            These instructions run before every interaction. Define the persona, tone, and strict rules here.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-2">
            <Label>Welcome Message</Label>
            <Input 
              value={welcomeMessage}
              onChange={(e) => setWelcomeMessage(e.target.value)}
              placeholder="Hi there! How can I help?"
            />
            <p className="text-xs text-muted-foreground">Sent automatically when a chat begins.</p>
          </div>
          <div className="space-y-2">
            <Label>Fallback Message</Label>
            <Input 
              value={fallbackMessage}
              onChange={(e) => setFallbackMessage(e.target.value)}
              placeholder="I'm not sure. Let me get a human."
            />
            <p className="text-xs text-muted-foreground">Sent when the AI cannot answer safely.</p>
          </div>
        </div>

        {isError && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Failed to update prompt: {(error as any)?.message || "Unknown error"}
          </div>
        )}

        {isSuccess && (
          <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Prompt configuration saved successfully.
          </div>
        )}

        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isPending}>
            {isPending ? "Saving..." : "Save Prompt Settings"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
