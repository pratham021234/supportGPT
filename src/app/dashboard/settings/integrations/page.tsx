"use client";

import { useMarketplace, useConnections, useConnectIntegration, useDisconnectIntegration } from "@/lib/api/integrations";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Settings, MessageSquare, Database, HardDrive, CheckCircle2, Unlink } from "lucide-react";

export default function IntegrationsPage() {
  const { data: marketplaceApps, isLoading: loadingApps } = useMarketplace();
  const { data: connections, isLoading: loadingConns } = useConnections();
  const { mutate: connect, isPending: connecting } = useConnectIntegration();
  const { mutate: disconnect, isPending: disconnecting } = useDisconnectIntegration();

  if (loadingApps || loadingConns) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const getCategoryIcon = (cat: string) => {
    switch(cat.toLowerCase()) {
      case 'communication': return <MessageSquare className="w-8 h-8 text-blue-500" />;
      case 'crm': return <Database className="w-8 h-8 text-orange-500" />;
      case 'helpdesk': return <Database className="w-8 h-8 text-rose-500" />;
      case 'storage': return <HardDrive className="w-8 h-8 text-emerald-500" />;
      default: return <Settings className="w-8 h-8 text-slate-500" />;
    }
  };

  const handleConnect = (providerId: string) => {
    // In reality, this would redirect to an OAuth flow. 
    // We mock the successful callback by just passing a dummy code.
    connect({ provider: providerId, auth_code: "mock_oauth_code" });
  };

  return (
    <div className="max-w-6xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Integrations Hub</h2>
        <p className="text-muted-foreground mt-1">
          Connect SupportGPT with your existing tools to synchronize data and streamline workflows.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {marketplaceApps?.map(app => {
          // Check if connected
          const activeConn = connections?.find(c => c.provider === app.id && c.status === "CONNECTED");

          return (
            <Card key={app.id} className="flex flex-col">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center">
                    {getCategoryIcon(app.category)}
                  </div>
                  {activeConn && (
                    <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50 gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Connected
                    </Badge>
                  )}
                </div>
                <CardTitle className="mt-4">{app.name}</CardTitle>
                <CardDescription className="text-xs uppercase font-semibold text-muted-foreground">{app.category}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <p className="text-sm text-muted-foreground">{app.description}</p>
                {activeConn ? (
                    <div className="flex items-center text-sm text-emerald-600 bg-emerald-50 px-3 py-2 rounded-md font-medium border border-emerald-100 mt-4">
                        <CheckCircle2 className="w-4 h-4 mr-2" /> Connected
                    </div>
                ) : (
                    <div className="flex items-center text-sm text-zinc-500 bg-zinc-50 px-3 py-2 rounded-md font-medium border mt-4">
                        <Unlink className="w-4 h-4 mr-2" /> Not Connected
                    </div>
                )}
              </CardContent>
              <CardFooter className="border-t px-6 py-4">
                {activeConn ? (
                  <Button 
                    variant="outline" 
                    className="w-full text-destructive hover:bg-destructive/10" 
                    onClick={() => disconnect(activeConn.id)}
                    disabled={disconnecting}
                  >
                    Disconnect
                  </Button>
                ) : (
                  <Button 
                    className="w-full" 
                    onClick={() => handleConnect(app.id)}
                    disabled={connecting}
                  >
                    Connect
                  </Button>
                )}
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
