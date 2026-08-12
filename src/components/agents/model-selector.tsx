"use client";

import { useState, useEffect } from "react";
import { useAgent, useModels, useUpdateModelConfig } from "@/lib/api/agents";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { AlertCircle, CheckCircle2, Cpu } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

export function ModelSelector({ agentId }: { agentId: string }) {
  const { data: agent } = useAgent(agentId);
  const { data: models, isLoading: isLoadingModels } = useModels();
  const { mutate: updateModel, isPending, isSuccess, isError, error } = useUpdateModelConfig(agentId);
  
  const [model, setModel] = useState("");
  const [temperature, setTemperature] = useState([0.7]);
  const [maxTokens, setMaxTokens] = useState([1024]);

  useEffect(() => {
    if (agent) {
      setModel(agent.model || "gemini-1.5-flash");
      setTemperature([agent.temperature ?? 0.7]);
      // Assuming max_tokens comes from a mock or is extended
      setMaxTokens([(agent as any).max_tokens ?? 1024]);
    }
  }, [agent]);

  const handleSave = () => {
    updateModel({
      model: model,
      temperature: temperature[0],
      max_tokens: maxTokens[0],
    });
  };

  const modelList = models || [
    { id: "gemini-1.5-flash", name: "Gemini 1.5 Flash", provider: "google" },
    { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro", provider: "google" },
    { id: "gpt-4o", name: "GPT-4o", provider: "openai" },
    { id: "gpt-4o-mini", name: "GPT-4o Mini", provider: "openai" }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Cpu className="h-5 w-5" /> Model Configuration</CardTitle>
        <CardDescription>Select the underlying LLM and adjust generation parameters.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        <div className="space-y-2">
          <Label>Foundation Model</Label>
          {isLoadingModels ? (
            <Skeleton className="h-10 w-full" />
          ) : (
            <Select value={model} onValueChange={(val) => setModel(val as string)}>
              <SelectTrigger>
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {modelList.map((m) => (
                  <SelectItem key={m.id} value={m.id}>
                    {m.name} <span className="text-muted-foreground text-xs ml-2 capitalize">({m.provider})</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <p className="text-xs text-muted-foreground">
            Flash/Mini models are faster and cheaper. Pro models are better for complex reasoning.
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Temperature</Label>
            <span className="text-sm font-medium">{temperature[0]}</span>
          </div>
          <Slider 
            min={0} max={2} step={0.1} 
            value={temperature} 
            onValueChange={setTemperature}
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Precise / Analytical</span>
            <span>Creative / Random</span>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Max Output Tokens</Label>
            <span className="text-sm font-medium">{maxTokens[0]}</span>
          </div>
          <Slider 
            min={256} max={8192} step={256} 
            value={maxTokens} 
            onValueChange={setMaxTokens}
          />
          <p className="text-xs text-muted-foreground">
            The maximum length of the agent's response.
          </p>
        </div>

        {isError && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Failed to update model: {(error as any)?.message || "Unknown error"}
          </div>
        )}

        {isSuccess && (
          <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Model settings saved successfully.
          </div>
        )}

        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isPending}>
            {isPending ? "Saving..." : "Save Model Settings"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
