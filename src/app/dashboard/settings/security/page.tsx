"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Shield, Key, Download, Trash2, Smartphone, AlertTriangle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";

export default function SecurityDashboardPage() {
  const { user } = useAuth();
  
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [newKeyName, setNewKeyName] = useState("");
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [gdprLoading, setGdprLoading] = useState(false);

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    try {
        const [kRes, sRes, aRes] = await Promise.all([
            fetch("/api/v1/security/api-keys", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/security/sessions", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/security/alerts", { headers: { Authorization: `Bearer ${user.token}` } })
        ]);
        if (kRes.ok) setApiKeys(await kRes.json());
        if (sRes.ok) setSessions(await sRes.json());
        if (aRes.ok) setAlerts(await aRes.json());
    } catch(e) {}
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [user]);
  
  const handleCreateKey = async () => {
      if (!user) return;
      setGenerating(true);
      try {
          const res = await fetch("/api/v1/security/api-keys", {
              method: "POST",
              headers: { "Content-Type": "application/json", Authorization: `Bearer ${user.token}` },
              body: JSON.stringify({ name: newKeyName, scopes: ["read:all"] })
          });
          if (res.ok) {
              const data = await res.json();
              setGeneratedKey(data.raw_key);
              setNewKeyName("");
              await loadData();
          }
      } catch(e) {}
      setGenerating(false);
  };
  
  const handleRevokeKey = async (id: string) => {
      if (!user) return;
      await fetch(`/api/v1/security/api-keys/${id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${user.token}` }
      });
      await loadData();
  };
  
  const handleRevokeSession = async (id: string) => {
      if (!user) return;
      await fetch(`/api/v1/security/sessions/${id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${user.token}` }
      });
      await loadData();
  };
  
  const handleGdprExport = async () => {
      if (!user) return;
      setGdprLoading(true);
      try {
          const res = await fetch("/api/v1/security/compliance/export", {
              method: "POST",
              headers: { Authorization: `Bearer ${user.token}` }
          });
          if (res.ok) {
              const data = await res.json();
              const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `gdpr_export_${new Date().getTime()}.json`;
              a.click();
              window.URL.revokeObjectURL(url);
          }
      } catch (e) {}
      setGdprLoading(false);
  };

  return (
    <div className="flex flex-col gap-6 p-8 overflow-y-auto h-[calc(100vh-64px)]">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Enterprise Security Center</h1>
        <p className="text-zinc-500 mt-1">Manage API Keys, active sessions, and compliance controls.</p>
      </div>

      <Tabs defaultValue="api-keys" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="api-keys" className="flex items-center"><Key className="w-4 h-4 mr-2" /> API Keys</TabsTrigger>
          <TabsTrigger value="sessions" className="flex items-center"><Smartphone className="w-4 h-4 mr-2" /> Active Sessions</TabsTrigger>
          <TabsTrigger value="alerts" className="flex items-center"><AlertTriangle className="w-4 h-4 mr-2" /> Security Alerts</TabsTrigger>
          <TabsTrigger value="compliance" className="flex items-center"><Shield className="w-4 h-4 mr-2" /> GDPR Compliance</TabsTrigger>
        </TabsList>
        
        {/* API KEYS */}
        <TabsContent value="api-keys" className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Create API Key</CardTitle>
                    <CardDescription>Generate a new token for programmatic access.</CardDescription>
                </CardHeader>
                <CardContent>
                    {generatedKey ? (
                        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                            <p className="text-sm text-emerald-800 font-semibold mb-2">Please copy your API key now. It will not be shown again.</p>
                            <code className="text-xs break-all bg-white p-2 rounded border">{generatedKey}</code>
                            <Button className="mt-4 w-full" variant="outline" onClick={() => setGeneratedKey(null)}>I have copied it</Button>
                        </div>
                    ) : (
                        <div className="flex space-x-2">
                            <Input placeholder="Key Name (e.g. CI/CD Script)" value={newKeyName} onChange={e => setNewKeyName(e.target.value)} />
                            <Button onClick={handleCreateKey} disabled={!newKeyName || generating}>
                                {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : "Generate"}
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Active API Keys</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        {loading ? <Skeleton className="h-20" /> : apiKeys.filter(k => k.is_active).length === 0 ? (
                            <p className="text-sm text-zinc-500">No active keys.</p>
                        ) : (
                            apiKeys.filter(k => k.is_active).map(key => (
                                <div key={key.id} className="flex justify-between items-center p-3 border rounded-lg">
                                    <div>
                                        <p className="font-semibold">{key.name}</p>
                                        <p className="text-xs font-mono text-zinc-500 mt-1">{key.prefix}••••••••••</p>
                                    </div>
                                    <Button variant="ghost" size="icon" className="text-rose-500 hover:text-rose-600 hover:bg-rose-50" onClick={() => handleRevokeKey(key.id)}>
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            ))
                        )}
                    </div>
                </CardContent>
            </Card>
        </TabsContent>
        
        {/* SESSIONS */}
        <TabsContent value="sessions" className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Active Devices & Sessions</CardTitle>
                    <CardDescription>Review and revoke access across your devices.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        {loading ? <Skeleton className="h-20" /> : sessions.filter(s => !s.is_revoked).length === 0 ? (
                            <p className="text-sm text-zinc-500">No active sessions.</p>
                        ) : (
                            sessions.filter(s => !s.is_revoked).map(session => (
                                <div key={session.id} className="flex justify-between items-center p-3 border rounded-lg">
                                    <div>
                                        <p className="font-medium text-sm">IP: {session.ip_address || "Unknown"}</p>
                                        <p className="text-xs text-zinc-500 mt-1 truncate max-w-[400px]">{session.user_agent}</p>
                                        <p className="text-[10px] text-zinc-400 mt-1">Last Active: {new Date(session.last_active).toLocaleString()}</p>
                                    </div>
                                    <Button variant="outline" size="sm" className="text-rose-500" onClick={() => handleRevokeSession(session.id)}>
                                        Revoke
                                    </Button>
                                </div>
                            ))
                        )}
                    </div>
                </CardContent>
            </Card>
        </TabsContent>

        {/* ALERTS */}
        <TabsContent value="alerts" className="space-y-6">
             <Card>
                <CardHeader>
                    <CardTitle>Security Monitoring</CardTitle>
                    <CardDescription>Automated threat detection and anomaly alerts.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        {loading ? <Skeleton className="h-20" /> : alerts.length === 0 ? (
                            <div className="p-4 bg-emerald-50 text-emerald-800 rounded-lg text-sm font-semibold flex items-center">
                                <Shield className="w-4 h-4 mr-2" /> No security threats detected.
                            </div>
                        ) : (
                            alerts.map(alert => (
                                <div key={alert.id} className="p-4 border border-rose-100 bg-rose-50 rounded-lg">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-white bg-rose-500 px-2 py-0.5 rounded mr-2">{alert.severity}</span>
                                            <span className="font-semibold text-rose-900">{alert.alert_type}</span>
                                        </div>
                                        <span className="text-xs text-rose-400">{new Date(alert.created_at).toLocaleString()}</span>
                                    </div>
                                    <p className="text-sm text-rose-800 mt-2">{alert.message}</p>
                                </div>
                            ))
                        )}
                    </div>
                </CardContent>
            </Card>
        </TabsContent>

        {/* COMPLIANCE */}
        <TabsContent value="compliance" className="space-y-6">
             <Card>
                <CardHeader>
                    <CardTitle>Data Privacy (GDPR)</CardTitle>
                    <CardDescription>Tools for Right to Access and Right to Erasure.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="flex items-center justify-between p-4 border rounded-lg bg-zinc-50">
                        <div>
                            <p className="font-semibold">Export Account Data</p>
                            <p className="text-xs text-zinc-500">Download a JSON file containing all your personal data.</p>
                        </div>
                        <Button variant="outline" onClick={handleGdprExport} disabled={gdprLoading}>
                            {gdprLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                            Export Data
                        </Button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 border border-rose-100 bg-rose-50 rounded-lg">
                        <div>
                            <p className="font-semibold text-rose-900">Delete Account & Data</p>
                            <p className="text-xs text-rose-600">Permanently erase all personal data from the system.</p>
                        </div>
                        <Button variant="destructive">
                            Delete Account
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
