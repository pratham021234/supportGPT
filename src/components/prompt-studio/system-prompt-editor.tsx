"use client";

import { useState, useEffect } from "react";
import { useUpdatePrompt } from "@/lib/api/prompt-studio";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Sparkles, Save, Loader2 } from "lucide-react";
import { useDebounce } from "@/hooks/use-debounce"; // Need to create this or use a simple timeout
import { Agent } from "@/lib/api/agents";

interface SystemPromptEditorProps {
  agent: Agent;
}

export function SystemPromptEditor({ agent }: SystemPromptEditorProps) {
  // Try to parse the behavior_rules if it stores system_prompt, else use description for MVP if no direct field
  // The API allows updating system_prompt via PATCH /agents/{id}/prompt.
  const [prompt, setPrompt] = useState(
    "You are a helpful support agent for SupportGPT..." // Default mock string since Agent model doesn't strictly type system_prompt in frontend yet
  );
  
  const [isDirty, setIsDirty] = useState(false);
  
  const { mutate: updatePrompt, isPending } = useUpdatePrompt(agent.id);

  const handleSave = () => {
    updatePrompt({ system_prompt: prompt }, {
      onSuccess: () => setIsDirty(false)
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-end">
        <div>
          <h3 className="text-lg font-medium">System Prompt</h3>
          <p className="text-sm text-muted-foreground">The core instructions that dictate how the AI agent behaves and responds.</p>
        </div>
        <Button 
          size="sm" 
          onClick={handleSave} 
          disabled={!isDirty || isPending}
          className="gap-2"
        >
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          {isPending ? "Saving..." : "Save Draft"}
        </Button>
      </div>
      
      <div className="relative">
        <Textarea 
          value={prompt}
          onChange={(e) => {
            setPrompt(e.target.value);
            setIsDirty(true);
          }}
          className="min-h-[300px] font-mono text-sm leading-relaxed p-4 resize-y bg-muted/30" 
          placeholder="You are a helpful assistant..."
        />
      </div>
      
      <div className="flex justify-between items-center text-xs text-muted-foreground">
        <span>Characters: {prompt.length}</span>
        <Button variant="ghost" size="sm" className="h-8 gap-2 text-primary hover:text-primary hover:bg-primary/10">
          <Sparkles className="h-4 w-4" /> Optimize Prompt
        </Button>
      </div>
    </div>
  );
}
