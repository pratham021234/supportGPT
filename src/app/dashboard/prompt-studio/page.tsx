"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Save, Play, Bot, Sparkles, MessageSquare } from "lucide-react";

export default function PromptStudioPage() {
  const [systemPrompt, setSystemPrompt] = useState(
    "You are a helpful customer support agent for SupportGPT. Your goal is to resolve customer issues quickly and accurately using the provided knowledge base.\n\nAlways maintain a professional, empathetic tone. If you are unsure of an answer, DO NOT guess. Instead, offer to escalate the ticket to a human agent."
  );

  return (
    <div className="flex flex-col gap-6 h-[calc(100vh-8rem)]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Prompt Studio</h1>
          <p className="text-muted-foreground">
            Configure agent behavior, system prompts, and test responses.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="agent_1">
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select Agent" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="agent_1">Customer Support Agent</SelectItem>
              <SelectItem value="agent_2">Technical Support</SelectItem>
              <SelectItem value="agent_3">Sales Assistant</SelectItem>
            </SelectContent>
          </Select>
          <Button className="gap-2">
            <Save className="h-4 w-4" /> Save Changes
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 flex-1 min-h-0">
        {/* Configuration Panel */}
        <div className="flex flex-col gap-6 overflow-y-auto pr-2 pb-8">
          <Card>
            <CardHeader>
              <CardTitle>System Prompt</CardTitle>
              <CardDescription>
                The core instructions that dictate how the AI agent behaves and responds.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Textarea 
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  className="min-h-[250px] font-mono text-sm resize-y" 
                />
                <div className="flex justify-between items-center text-sm text-muted-foreground">
                  <span>Tokens: ~64</span>
                  <Button variant="ghost" size="sm" className="h-8 gap-2 text-primary">
                    <Sparkles className="h-4 w-4" /> Optimize Prompt
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Tabs defaultValue="behavior">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="behavior">Behavior</TabsTrigger>
              <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
              <TabsTrigger value="escalation">Escalation</TabsTrigger>
            </TabsList>
            
            <TabsContent value="behavior" className="mt-4">
              <Card>
                <CardContent className="space-y-6 pt-6">
                  <div className="space-y-2">
                    <Label>Model</Label>
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
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <Label>Temperature</Label>
                      <span className="text-sm text-muted-foreground">0.2</span>
                    </div>
                    <input type="range" min="0" max="1" step="0.1" defaultValue="0.2" className="w-full" />
                    <p className="text-xs text-muted-foreground">Lower values mean more focused and deterministic responses.</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="knowledge" className="mt-4">
              <Card>
                <CardContent className="space-y-6 pt-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Include Citations</Label>
                      <p className="text-xs text-muted-foreground">Attach source links to AI answers.</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Strict Grounding</Label>
                      <p className="text-xs text-muted-foreground">Refuse to answer if not in knowledge base.</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="escalation" className="mt-4">
              <Card>
                <CardContent className="space-y-6 pt-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto-Escalate on Low Confidence</Label>
                      <p className="text-xs text-muted-foreground">Transfer to human agent automatically.</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="space-y-2">
                    <Label>Confidence Threshold</Label>
                    <Select defaultValue="70">
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
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Testing Playground */}
        <div className="flex flex-col h-full overflow-hidden border rounded-xl bg-background shadow-sm">
          <div className="h-12 border-b bg-muted/30 flex items-center px-4 justify-between shrink-0">
            <div className="flex items-center gap-2 font-medium text-sm">
              <Play className="h-4 w-4 text-primary" /> Playground Preview
            </div>
            <Button variant="ghost" size="sm" className="h-8 text-xs">Clear Chat</Button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div className="flex w-max max-w-[80%] flex-col gap-2 rounded-lg px-3 py-2 text-sm bg-primary text-primary-foreground ml-auto">
              How do I invite team members?
            </div>
            <div className="flex w-max max-w-[80%] flex-col gap-2 rounded-lg px-3 py-2 text-sm bg-muted">
              To invite team members to SupportGPT, follow these steps:
              <br/><br/>
              1. Go to the <strong>Team</strong> section in your dashboard.<br/>
              2. Click on the <strong>Invite Users</strong> button.<br/>
              3. Enter their email address and select their role.<br/>
              4. Click <strong>Send Invite</strong>.
              <br/><br/>
              <span className="text-xs text-muted-foreground mt-2 border-t pt-2 block border-border">
                Sources: <a href="#" className="text-primary hover:underline">Team Management Guide</a>
              </span>
            </div>
          </div>
          
          <div className="p-4 border-t bg-background shrink-0">
            <div className="relative">
              <Input placeholder="Type a message to test..." className="pr-10" />
              <Button size="icon" variant="ghost" className="absolute right-0 top-0 h-full rounded-l-none text-primary">
                <MessageSquare className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
