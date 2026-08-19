"use client";

import { useState, useEffect } from "react";
import { useAdminWidgetSettings, useUpdateWidgetSettings, useWidgetAnalytics } from "@/lib/api/widget-client";
import { useAgents } from "@/lib/api/agents";
import { useAuthStore } from "@/store/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Palette, MessageSquare, Bot, Code, BarChart3, Save, ExternalLink } from "lucide-react";

export default function WidgetBuilderPage() {
  const workspaceId = useAuthStore(state => state.workspace?.id);
  const { data: config, isLoading: loadingConfig } = useAdminWidgetSettings();
  const { data: analytics, isLoading: loadingAnalytics } = useWidgetAnalytics();
  const { data: agents, isLoading: loadingAgents } = useAgents();
  const { mutate: updateSettings, isPending: saving } = useUpdateWidgetSettings();

  const [localConfig, setLocalConfig] = useState<any>({});

  useEffect(() => {
    if (config) {
      setLocalConfig(config);
    }
  }, [config]);

  const handleSave = () => {
    updateSettings(localConfig, {
      onSuccess: () => {
        const iframe = document.getElementById("widget-preview-iframe") as HTMLIFrameElement;
        if (iframe) iframe.src = iframe.src; // Reload preview
      }
    });
  };

  if (loadingConfig || loadingAgents) {
    return <div className="flex justify-center items-center h-full"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const embedCode = `<script src="https://cdn.supportgpt.ai/widget.js"></script>\n<script>\n  SupportGPT.init({\n    workspaceId: "${workspaceId}",\n    agentId: "${localConfig.assigned_agent_id || ''}"\n  });\n</script>`;

  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      {/* Editor Panel */}
      <div className="w-[55%] flex flex-col border-r">
        <div className="p-6 border-b flex justify-between items-center bg-card">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Widget Builder</h1>
            <p className="text-muted-foreground mt-1">Design and configure your embedded customer experience.</p>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
            Publish Changes
          </Button>
        </div>

        <Tabs defaultValue="appearance" className="flex-1 flex flex-col overflow-hidden">
          <div className="px-6 pt-4 border-b">
            <TabsList className="grid grid-cols-5 w-full max-w-3xl">
              <TabsTrigger value="appearance" className="gap-2"><Palette className="w-4 h-4"/> Appearance</TabsTrigger>
              <TabsTrigger value="content" className="gap-2"><MessageSquare className="w-4 h-4"/> Content</TabsTrigger>
              <TabsTrigger value="agent" className="gap-2"><Bot className="w-4 h-4"/> Agent</TabsTrigger>
              <TabsTrigger value="install" className="gap-2"><Code className="w-4 h-4"/> Install</TabsTrigger>
              <TabsTrigger value="analytics" className="gap-2"><BarChart3 className="w-4 h-4"/> Analytics</TabsTrigger>
            </TabsList>
          </div>

          <div className="flex-1 overflow-y-auto p-6 bg-muted/10">
            <TabsContent value="appearance" className="m-0 space-y-6">
              <Card>
                <CardHeader><CardTitle>Theme & Colors</CardTitle></CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>Theme Preference</Label>
                    <Select value={localConfig.theme || 'light'} onValueChange={v => setLocalConfig({...localConfig, theme: v})}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">Light Mode</SelectItem>
                        <SelectItem value="dark">Dark Mode</SelectItem>
                        <SelectItem value="system">System Default</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Primary Brand Color</Label>
                    <div className="flex gap-4">
                      <Input 
                        type="color" 
                        className="w-14 h-10 p-1 cursor-pointer"
                        value={localConfig.primary_color || "#000000"}
                        onChange={e => setLocalConfig({...localConfig, primary_color: e.target.value})}
                      />
                      <Input 
                        type="text" 
                        value={localConfig.primary_color || "#000000"}
                        onChange={e => setLocalConfig({...localConfig, primary_color: e.target.value})}
                        className="font-mono"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Company Logo URL</Label>
                    <Input 
                      type="url" 
                      placeholder="https://..." 
                      value={localConfig.logo_url || ""}
                      onChange={e => setLocalConfig({...localConfig, logo_url: e.target.value})}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Positioning</CardTitle></CardHeader>
                <CardContent>
                  <Select value={localConfig.position || 'bottom-right'} onValueChange={v => setLocalConfig({...localConfig, position: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bottom-right">Bottom Right</SelectItem>
                      <SelectItem value="bottom-left">Bottom Left</SelectItem>
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="content" className="m-0 space-y-6">
              <Card>
                <CardHeader><CardTitle>Greeting Experience</CardTitle></CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>Launcher Text</Label>
                    <Input 
                      value={localConfig.launcher_text || ""}
                      onChange={e => setLocalConfig({...localConfig, launcher_text: e.target.value})}
                      placeholder="e.g. Chat with us"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Welcome Message</Label>
                    <Textarea 
                      value={localConfig.welcome_message || ""}
                      onChange={e => setLocalConfig({...localConfig, welcome_message: e.target.value})}
                      placeholder="Hi there! How can we help you today?"
                      rows={2}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Offline Message</Label>
                    <Textarea 
                      value={localConfig.offline_message || ""}
                      onChange={e => setLocalConfig({...localConfig, offline_message: e.target.value})}
                      placeholder="We are currently offline."
                      rows={2}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Suggested Questions (comma separated)</Label>
                    <Textarea 
                      value={localConfig.suggested_questions?.join(", ") || ""}
                      onChange={e => setLocalConfig({...localConfig, suggested_questions: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean)})}
                      placeholder="How to reset password, Talk to sales"
                      rows={2}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="agent" className="m-0 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>AI Assignment</CardTitle>
                  <CardDescription>Select which AI Agent will power this widget's conversations.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Label>Assigned Agent</Label>
                    <Select 
                      value={localConfig.assigned_agent_id || ''} 
                      onValueChange={v => setLocalConfig({...localConfig, assigned_agent_id: v})}
                    >
                      <SelectTrigger><SelectValue placeholder="Select an Agent" /></SelectTrigger>
                      <SelectContent>
                        {agents?.map(a => (
                          <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="install" className="m-0 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Installation Center</CardTitle>
                  <CardDescription>Embed this code into your website's HTML.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-muted text-foreground p-4 rounded-md text-sm font-mono whitespace-pre-wrap border overflow-x-auto">
                    {embedCode}
                  </div>
                  <Button variant="secondary" className="w-full" onClick={() => navigator.clipboard.writeText(embedCode)}>
                    Copy Code
                  </Button>
                </CardContent>
                <CardFooter className="border-t bg-muted/20 px-6 py-4 flex gap-4 text-sm">
                  <a href="#" className="flex items-center text-primary hover:underline">Next.js Guide <ExternalLink className="w-3 h-3 ml-1"/></a>
                  <a href="#" className="flex items-center text-primary hover:underline">React Guide <ExternalLink className="w-3 h-3 ml-1"/></a>
                  <a href="#" className="flex items-center text-primary hover:underline">WordPress Guide <ExternalLink className="w-3 h-3 ml-1"/></a>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Security</CardTitle>
                  <CardDescription>Restrict which domains can load your widget.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Allowed Domains (comma separated)</Label>
                    <Input 
                      value={localConfig.allowed_domains?.join(", ") || ""}
                      onChange={e => setLocalConfig({...localConfig, allowed_domains: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean)})}
                      placeholder="example.com, app.example.com"
                    />
                    <p className="text-xs text-muted-foreground">If empty, the widget can be embedded anywhere.</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analytics" className="m-0 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Widget Opens</CardTitle></CardHeader>
                  <CardContent><div className="text-3xl font-bold">{analytics?.total_opens.toLocaleString()}</div></CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Messages Sent</CardTitle></CardHeader>
                  <CardContent><div className="text-3xl font-bold">{analytics?.total_messages.toLocaleString()}</div></CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">AI Resolution Rate</CardTitle></CardHeader>
                  <CardContent><div className="text-3xl font-bold text-emerald-600">{analytics?.resolution_rate}%</div></CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Human Escalations</CardTitle></CardHeader>
                  <CardContent><div className="text-3xl font-bold text-amber-600">{analytics?.escalations.toLocaleString()}</div></CardContent>
                </Card>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </div>

      {/* Live Preview Panel */}
      <div className="w-[45%] bg-zinc-100 flex items-center justify-center relative p-8">
        <div className="absolute top-4 left-6 flex items-center gap-2 text-sm font-semibold text-zinc-500 uppercase tracking-wider">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Live Preview
        </div>
        
        {/* Mock Browser Window */}
        <div className="w-full max-w-[400px] h-[700px] bg-white rounded-xl shadow-2xl overflow-hidden border border-zinc-200 relative flex flex-col">
          <div className="h-10 bg-zinc-100 border-b flex items-center px-4 gap-2">
            <div className="w-3 h-3 rounded-full bg-rose-400" />
            <div className="w-3 h-3 rounded-full bg-amber-400" />
            <div className="w-3 h-3 rounded-full bg-emerald-400" />
            <div className="mx-auto bg-white px-4 py-1 rounded text-xs text-zinc-500 w-48 text-center truncate">yourwebsite.com</div>
          </div>
          <div className="flex-1 bg-zinc-50 relative">
            {workspaceId && (
              <iframe 
                id="widget-preview-iframe"
                src={`/widget?workspaceId=${workspaceId}&preview=true&agentId=${localConfig.assigned_agent_id || ''}`} 
                className="absolute inset-0 w-full h-full border-none z-10 bg-transparent"
                allow="microphone"
              />
            )}
            <div className="absolute inset-0 p-8">
              <div className="h-8 w-3/4 bg-zinc-200 rounded mb-4" />
              <div className="h-4 w-full bg-zinc-200 rounded mb-2" />
              <div className="h-4 w-full bg-zinc-200 rounded mb-2" />
              <div className="h-4 w-5/6 bg-zinc-200 rounded mb-8" />
              <div className="h-32 w-full bg-zinc-200 rounded" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
