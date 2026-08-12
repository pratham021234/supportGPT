"use client";

import { useState, useEffect } from "react";
import { useAgent, useUpdateEscalation } from "@/lib/api/agents";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { AlertCircle, CheckCircle2, ShieldAlert } from "lucide-react";

export function EscalationRules({ agentId }: { agentId: string }) {
  const { data: agent } = useAgent(agentId);
  const { mutate: updateEscalation, isPending, isSuccess, isError, error } = useUpdateEscalation(agentId);
  
  const [confidenceThreshold, setConfidenceThreshold] = useState([75]);
  const [autoHandoff, setAutoHandoff] = useState(true);
  const [autoTicket, setAutoTicket] = useState(false);

  useEffect(() => {
    if (agent) {
      setConfidenceThreshold([(agent as any).confidence_threshold ?? 75]);
      setAutoHandoff((agent as any).auto_handoff ?? true);
      setAutoTicket((agent as any).auto_create_ticket ?? false);
    }
  }, [agent]);

  const handleSave = () => {
    updateEscalation({
      confidence_threshold: confidenceThreshold[0],
      auto_handoff: autoHandoff,
      auto_create_ticket: autoTicket,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><ShieldAlert className="h-5 w-5" /> Escalation Rules</CardTitle>
        <CardDescription>Define when and how this agent hands off to human agents.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Confidence Threshold (%)</Label>
            <span className="text-sm font-medium">{confidenceThreshold[0]}%</span>
          </div>
          <Slider 
            min={50} max={100} step={1} 
            value={confidenceThreshold} 
            onValueChange={setConfidenceThreshold}
          />
          <p className="text-xs text-muted-foreground">
            If the AI's confidence in its answer is below this percentage, it will trigger an escalation.
          </p>
        </div>

        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="space-y-0.5">
            <Label className="text-base">Automatic Human Handoff</Label>
            <p className="text-sm text-muted-foreground">
              Directly transfer the chat to an available human agent if confidence is low.
            </p>
          </div>
          <Switch checked={autoHandoff} onCheckedChange={setAutoHandoff} />
        </div>

        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="space-y-0.5">
            <Label className="text-base">Auto-Create Ticket</Label>
            <p className="text-sm text-muted-foreground">
              Create a support ticket automatically when escalating outside business hours.
            </p>
          </div>
          <Switch checked={autoTicket} onCheckedChange={setAutoTicket} />
        </div>

        {isError && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Failed to update rules: {(error as any)?.message || "Unknown error"}
          </div>
        )}

        {isSuccess && (
          <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Escalation rules saved successfully.
          </div>
        )}

        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isPending}>
            {isPending ? "Saving..." : "Save Escalation Rules"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
