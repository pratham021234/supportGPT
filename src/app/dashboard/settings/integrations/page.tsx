"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Plug, Activity, CheckCircle2, ServerCrash, ExternalLink, RefreshCw, Loader2, Link as LinkIcon, Unlink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

export default function IntegrationsDashboardPage() {
  const { user } = useAuth();
  
  const [marketplace, setMarketplace] = useState<any[]>([]);
  const [connections, setConnections] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    try {
        const [mkRes, conRes, logRes] = await Promise.all([
            fetch("/api/v1/integrations/marketplace", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/integrations/", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/integrations/logs", { headers: { Authorization: `Bearer ${user.token}` } })
        ]);
        if (mkRes.ok) setMarketplace(await mkRes.json());
        if (conRes.ok) setConnections(await conRes.json());
        if (logRes.ok) setLogs(await logRes.json());
    } catch(e) {}
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleConnect = async (provider: string) => {
    if (!user) return;
    setActionLoading(provider);
    try {
        // In real app, this redirects to an OAuth consent screen which then returns the code
        const res = await fetch("/api/v1/integrations/connect", {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${user.token}` },
            body: JSON.stringify({ provider, auth_code: "mock_auth_code_from_oauth_callback" })
        });
        if (res.ok) {
            await loadData();
        }
    } catch(e) {}
    setActionLoading(null);
  };

  const handleDisconnect = async (connectionId: string, provider: string) => {
    if (!user || !confirm(`Are you sure you want to disconnect ${provider}?`)) return;
    setActionLoading(provider);
    try {
        await fetch(`/api/v1/integrations/${connectionId}/disconnect`, {
            method: "POST",
            headers: { Authorization: `Bearer ${user.token}` }
        });
        await loadData();
    } catch(e) {}
    setActionLoading(null);
  };

  if (loading) {
      return (
          <div className="p-8 space-y-4">
              <Skeleton className="h-12 w-[300px]" />
              <Skeleton className="h-[400px] w-full" />
          </div>
      );
  }

  return (
    <div className="flex flex-col gap-6 p-8 overflow-y-auto h-[calc(100vh-64px)]">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Integrations & Marketplace</h1>
        <p className="text-zinc-500 mt-1">Connect SupportGPT to your CRM, Helpdesk, and Communication tools.</p>
      </div>

      <Tabs defaultValue="marketplace" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="marketplace" className="flex items-center"><Plug className="w-4 h-4 mr-2" /> App Marketplace</TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center"><Activity className="w-4 h-4 mr-2" /> Sync Health & Logs</TabsTrigger>
        </TabsList>
        
        {/* MARKETPLACE */}
        <TabsContent value="marketplace" className="space-y-6">
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                 {marketplace.map(app => {
                     const activeConnection = connections.find(c => c.provider === app.id && c.status === "CONNECTED");
                     
                     return (
                         <Card key={app.id} className="flex flex-col">
                             <CardHeader>
                                 <div className="flex justify-between items-start">
                                     <CardTitle className="text-xl">{app.name}</CardTitle>
                                     <Badge variant="outline">{app.category}</Badge>
                                 </div>
                                 <CardDescription className="mt-2 h-10">{app.description}</CardDescription>
                             </CardHeader>
                             <CardContent className="flex-grow">
                                 {activeConnection ? (
                                     <div className="flex items-center text-sm text-emerald-600 bg-emerald-50 px-3 py-2 rounded-md font-medium border border-emerald-100">
                                         <CheckCircle2 className="w-4 h-4 mr-2" /> Connected
                                     </div>
                                 ) : (
                                     <div className="flex items-center text-sm text-zinc-500 bg-zinc-50 px-3 py-2 rounded-md font-medium border">
                                         <Unlink className="w-4 h-4 mr-2" /> Not Connected
                                     </div>
                                 )}
                             </CardContent>
                             <CardFooter>
                                 {activeConnection ? (
                                     <Button 
                                        variant="destructive" 
                                        className="w-full" 
                                        disabled={actionLoading === app.id}
                                        onClick={() => handleDisconnect(activeConnection.id, app.id)}
                                    >
                                        {actionLoading === app.id ? <Loader2 className="w-4 h-4 animate-spin" /> : "Disconnect"}
                                     </Button>
                                 ) : (
                                     <Button 
                                        variant="default" 
                                        className="w-full"
                                        disabled={actionLoading === app.id}
                                        onClick={() => handleConnect(app.id)}
                                     >
                                         {actionLoading === app.id ? <Loader2 className="w-4 h-4 animate-spin" /> : "Connect"}
                                     </Button>
                                 )}
                             </CardFooter>
                         </Card>
                     );
                 })}
             </div>
        </TabsContent>

        {/* LOGS */}
        <TabsContent value="logs">
            <Card>
                <CardHeader>
                    <CardTitle className="flex justify-between items-center">
                        Sync History
                        <Button variant="outline" size="sm" onClick={loadData}><RefreshCw className="w-4 h-4 mr-2"/> Refresh</Button>
                    </CardTitle>
                    <CardDescription>View synchronization logs for all connected platforms.</CardDescription>
                </CardHeader>
                <CardContent>
                    {logs.length === 0 ? (
                        <div className="p-8 text-center text-zinc-500 border border-dashed rounded-lg">
                            <Activity className="w-8 h-8 mx-auto mb-2 text-zinc-300" />
                            <p>No synchronization events recorded yet.</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {logs.map(log => (
                                <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-zinc-50">
                                    <div className="flex flex-col">
                                        <div className="flex items-center space-x-2">
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                                                log.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-700' : 
                                                log.status === 'FAILED' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                                            }`}>
                                                {log.status}
                                            </span>
                                            <span className="font-semibold text-sm capitalize">{log.provider}</span>
                                            <span className="text-sm text-zinc-500">{log.action} {log.resource_type} ({log.resource_id})</span>
                                        </div>
                                        {log.error_message && (
                                            <p className="text-xs text-rose-500 mt-1 flex items-center"><ServerCrash className="w-3 h-3 mr-1"/> {log.error_message}</p>
                                        )}
                                    </div>
                                    <span className="text-xs text-zinc-400">{new Date(log.created_at).toLocaleString()}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
