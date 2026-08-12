"use client";

import { useSearchParams } from "next/navigation";
import { usePromptStudioAgents, useUpdateModelSettings, useUpdateEscalation } from "@/lib/api/prompt-studio";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from "lucide-react";

import { SystemPromptEditor } from "@/components/prompt-studio/system-prompt-editor";
import { TestingPlayground } from "@/components/prompt-studio/testing-playground";
import { VersionHistory } from "@/components/prompt-studio/version-history";
import { useState } from "react";

export default function PromptStudioPage() {
  const searchParams = useSearchParams();
  const agentId = searchParams.get("agent");

  const { data: agents, isLoading: isLoadingAgents } = usePromptStudioAgents();

  const { mutate: updateModel, isPending: isUpdatingModel } = useUpdateModelSettings(agentId || "");
  const { mutate: updateEscalation, isPending: isUpdatingEscalation } = useUpdateEscalation(agentId || "");

  // Local state for configuration sliders/switches (mocking some fields for MVP)
  const [temperature, setTemperature] = useState(0.2);
  const [autoEscalate, setAutoEscalate] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState("70");

  const activeAgent = agents?.find(a => a.id === agentId);

  if (!agentId || !activeAgent) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground p-8 text-center flex-col h-full">
        <h2 className="text-xl font-semibold mb-2">No Agent Selected</h2>
        <p className="text-sm">Please select an agent from the sidebar to configure its behavior and test its responses.</p>
      </div>
    );
  }

  const handleSaveModel = () => {
    updateModel({ temperature });
  };

  const handleSaveEscalation = () => {
    updateEscalation({ 
      auto_handoff: autoEscalate, 
      confidence_threshold: parseInt(confidenceThreshold) 
    });
  };

  return (
    <div className="flex flex-1 min-h-0 relative">
      {/* Configuration Panel */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="flex flex-col gap-1 pb-4 border-b">
          <h1 className="text-2xl font-bold tracking-tight">{activeAgent.name}</h1>
          <p className="text-muted-foreground text-sm">
            Configure agent behavior, system prompts, safety rules, and versioning.
          </p>
        </div>

        <Tabs defaultValue="prompt" className="w-full">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
            <TabsTrigger value="prompt">System Prompt</TabsTrigger>
            <TabsTrigger value="behavior">Behavior & Safety</TabsTrigger>
            <TabsTrigger value="escalation">Escalation</TabsTrigger>
            <TabsTrigger value="versions">Versions</TabsTrigger>
          </TabsList>
          
          <TabsContent value="prompt" className="mt-6">
            <SystemPromptEditor agent={activeAgent} />
          </TabsContent>

          <TabsContent value="behavior" className="mt-6 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Model Configuration</CardTitle>
                <CardDescription>Select the underlying LLM and set its sampling parameters.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2 max-w-sm">
                  <Label>Default Model</Label>
                  <Select defaultValue="gpt-4o">
                    <SelectTrigger>
                      <SelectValue placeholder="Select a model" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4o">GPT-4o (Recommended)</SelectItem>
                      <SelectItem value="claude-3-5-sonnet">Claude 3.5 Sonnet</SelectItem>
                      <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2 max-w-sm">
                  <div className="flex justify-between">
                    <Label>Temperature</Label>
                    <span className="text-sm text-muted-foreground">{temperature}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" max="1" step="0.1" 
                    value={temperature} 
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full" 
                  />
                  <p className="text-xs text-muted-foreground">Lower values mean more focused and deterministic responses. Higher values increase creativity.</p>
                </div>
              </CardContent>
              <CardFooter className="border-t pt-4">
                <Button onClick={handleSaveModel} disabled={isUpdatingModel}>
                  {isUpdatingModel && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Save Model Settings
                </Button>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Safety & Citations</CardTitle>
                <CardDescription>Configure how the agent handles unknown queries and citations.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Include Citations</Label>
                    <p className="text-xs text-muted-foreground">Attach source links to AI answers when resolving queries.</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Strict Grounding (Hallucination Prevention)</Label>
                    <p className="text-xs text-muted-foreground">Refuse to answer if the answer is not explicitly found in the knowledge base.</p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="escalation" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Escalation Rules</CardTitle>
                <CardDescription>Determine when this agent should hand off the conversation to a human.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Auto-Escalate on Low Confidence</Label>
                    <p className="text-xs text-muted-foreground">Transfer to human agent automatically if confidence is below threshold.</p>
                  </div>
                  <Switch 
                    checked={autoEscalate} 
                    onCheckedChange={setAutoEscalate} 
                  />
                </div>
                {autoEscalate && (
                  <div className="space-y-2 max-w-sm pl-4 border-l-2 border-muted mt-4">
                    <Label>Confidence Threshold</Label>
                    <Select value={confidenceThreshold} onValueChange={(val) => setConfidenceThreshold(val as string)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select threshold" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="90">High (90%)</SelectItem>
                        <SelectItem value="70">Medium (70%)</SelectItem>
                        <SelectItem value="50">Low (50%)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
                <div className="flex items-center justify-between mt-4">
                  <div className="space-y-0.5">
                    <Label>Auto-Create Ticket</Label>
                    <p className="text-xs text-muted-foreground">Create a ticket in the Operations dashboard when an escalation occurs.</p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </CardContent>
              <CardFooter className="border-t pt-4">
                <Button onClick={handleSaveEscalation} disabled={isUpdatingEscalation}>
                  {isUpdatingEscalation && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Save Escalation Rules
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          <TabsContent value="versions" className="mt-6">
            <VersionHistory agentId={activeAgent.id} />
          </TabsContent>
        </Tabs>
      </div>

      {/* Testing Playground Sidebar */}
      <TestingPlayground agentId={activeAgent.id} />
    </div>
  );
}
