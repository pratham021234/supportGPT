"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Bot, Building2, Headphones, Wrench, Code2, AlertCircle } from "lucide-react";
import { useCreateAgent } from "@/lib/api/agents";

export function CreateAgentModal() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [agentType, setAgentType] = useState("SUPPORT");
  const { mutate: createAgent, isPending, isError, error } = useCreateAgent();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    
    createAgent({ name, description, agent_type: agentType }, {
      onSuccess: () => {
        setOpen(false);
        // Reset form
        setName("");
        setDescription("");
        setAgentType("SUPPORT");
      }
    });
  };

  const getAgentTypeIcon = (type: string) => {
    switch (type) {
      case "SUPPORT": return <Headphones className="w-4 h-4 mr-2" />;
      case "SALES": return <Building2 className="w-4 h-4 mr-2" />;
      case "TECHNICAL": return <Wrench className="w-4 h-4 mr-2" />;
      case "CUSTOM": return <Code2 className="w-4 h-4 mr-2" />;
      default: return <Bot className="w-4 h-4 mr-2" />;
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button className="shrink-0 gap-2" />}>
        <Plus className="h-4 w-4" />
        Create Agent
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Agent</DialogTitle>
          <DialogDescription>
            Configure the basic settings for your new AI agent. You can customize prompts and knowledge later.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-2">
            <Label htmlFor="name">Agent Name</Label>
            <Input 
              id="name" 
              placeholder="e.g., Billing Support Bot" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea 
              id="description" 
              placeholder="What is the primary purpose of this agent?" 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="type">Agent Type</Label>
            <Select value={agentType} onValueChange={(val) => setAgentType(val as string)}>
              <SelectTrigger id="type">
                <SelectValue placeholder="Select an agent type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SUPPORT">
                  <div className="flex items-center">{getAgentTypeIcon("SUPPORT")} Customer Support</div>
                </SelectItem>
                <SelectItem value="SALES">
                  <div className="flex items-center">{getAgentTypeIcon("SALES")} Sales & Lead Gen</div>
                </SelectItem>
                <SelectItem value="TECHNICAL">
                  <div className="flex items-center">{getAgentTypeIcon("TECHNICAL")} Technical Support</div>
                </SelectItem>
                <SelectItem value="CUSTOM">
                  <div className="flex items-center">{getAgentTypeIcon("CUSTOM")} Custom Purpose</div>
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground mt-2">
              The agent type helps set default behaviors and metrics tracked on the dashboard.
            </p>
          </div>

          {isError && (
            <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Failed to create agent: {(error as any)?.message || "Unknown error"}
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={!name || isPending}>
              {isPending ? "Creating..." : "Create Agent"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
