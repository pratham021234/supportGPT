"use client";

import { useAiProviders } from "@/lib/api/settings";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Loader2, AlertCircle, ExternalLink, Settings2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AiProvidersPage() {
  const { data: providers, isLoading } = useAiProviders();

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">AI Providers</h2>
        <p className="text-muted-foreground mt-1">
          Configure which LLM providers are enabled and set fallback priorities.
        </p>
      </div>

      <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-4 flex gap-3">
        <AlertCircle className="h-5 w-5 shrink-0 mt-0.5 text-amber-600" />
        <div>
          <h5 className="font-semibold text-amber-900 mb-1">Billing Notice</h5>
          <p className="text-sm">
            Using third-party AI providers directly via your own API keys bypasses SupportGPT's included usage quotas, but you will be billed directly by the provider (e.g. OpenAI, Anthropic).
          </p>
        </div>
      </div>

      <div className="grid gap-6">
        {isLoading ? (
          <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
        ) : (
          providers?.map(provider => (
            <Card key={provider.id} className={provider.is_enabled ? "border-primary/50" : ""}>
              <CardHeader className="flex flex-row items-center justify-between pb-4">
                <div className="space-y-1">
                  <CardTitle className="text-xl flex items-center gap-2">
                    {provider.name}
                    {provider.priority === 1 && <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full font-normal">Primary</span>}
                  </CardTitle>
                  <CardDescription>Use {provider.name} for generating responses and processing tickets.</CardDescription>
                </div>
                <Switch checked={provider.is_enabled} />
              </CardHeader>
              <CardContent>
                {provider.is_enabled && (
                  <div className="space-y-4 p-4 bg-muted/20 border rounded-md">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">API Key</span>
                      <span className="text-xs font-mono text-muted-foreground bg-background px-2 py-1 rounded border">sk-...xxxx</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Priority Routing</span>
                      <span className="text-sm text-muted-foreground">Level {provider.priority}</span>
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter className="bg-muted/10 border-t px-6 py-3 flex justify-between">
                <Button variant="link" className="px-0 h-auto text-muted-foreground" size="sm">
                  View Documentation <ExternalLink className="w-3 h-3 ml-1" />
                </Button>
                <Button variant="outline" size="sm" className="gap-2" disabled={!provider.is_enabled}>
                  <Settings2 className="w-4 h-4" /> Configure
                </Button>
              </CardFooter>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
