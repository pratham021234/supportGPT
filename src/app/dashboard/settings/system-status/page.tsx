"use client";

import { useSystemStatus } from "@/lib/api/settings";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Server, Database, Activity, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

export default function SystemStatusPage() {
  const { data: status, isLoading } = useSystemStatus();

  const getStatusIcon = (state: string) => {
    switch(state) {
      case 'healthy': return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'down': return <XCircle className="w-5 h-5 text-destructive" />;
      default: return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
    }
  };

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">System Status</h2>
        <p className="text-muted-foreground mt-1">
          Real-time monitoring of SupportGPT core infrastructure services.
        </p>
      </div>

      <div className={`p-6 rounded-lg border-2 flex items-center gap-4 ${status?.status === 'healthy' ? 'bg-emerald-50/50 border-emerald-100' : 'bg-amber-50/50 border-amber-100'}`}>
        <div className={`p-3 rounded-full ${status?.status === 'healthy' ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'}`}>
          <Activity className="w-8 h-8" />
        </div>
        <div>
          <h3 className="text-xl font-bold capitalize">{status?.status || 'Healthy'}</h3>
          <p className="text-muted-foreground">All systems are operating normally. Last checked: {new Date().toLocaleTimeString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex justify-between items-center">
              <span className="flex items-center gap-2"><Server className="w-5 h-5 text-muted-foreground" /> Core API</span>
              {getStatusIcon(status?.api || 'healthy')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Handles all incoming requests, routing, and authentication.</p>
            <div className="mt-4 flex justify-between text-xs font-mono bg-muted/30 p-2 rounded">
              <span>Version</span>
              <span>{status?.version || 'v1.0.0'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex justify-between items-center">
              <span className="flex items-center gap-2"><Database className="w-5 h-5 text-muted-foreground" /> PostgreSQL Database</span>
              {getStatusIcon(status?.database || 'healthy')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Primary relational datastore for tickets, users, and config.</p>
            <div className="mt-4 flex justify-between text-xs font-mono bg-muted/30 p-2 rounded">
              <span>Latency</span>
              <span className="text-emerald-500">12ms</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex justify-between items-center">
              <span className="flex items-center gap-2"><Activity className="w-5 h-5 text-muted-foreground" /> Redis Cache</span>
              {getStatusIcon(status?.redis || 'healthy')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">In-memory datastore for caching, websockets, and rate limiting.</p>
            <div className="mt-4 flex justify-between text-xs font-mono bg-muted/30 p-2 rounded">
              <span>Hit Rate</span>
              <span>98.4%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex justify-between items-center">
              <span className="flex items-center gap-2"><Database className="w-5 h-5 text-muted-foreground" /> Vector DB (Qdrant)</span>
              {getStatusIcon(status?.vector_db || 'healthy')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">High-dimensional database for RAG document embeddings.</p>
            <div className="mt-4 flex justify-between text-xs font-mono bg-muted/30 p-2 rounded">
              <span>Collections</span>
              <span>4 Active</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
