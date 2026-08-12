"use client";

import { useAuditLogs } from "@/lib/api/workspaces";
import { useSecurityEvents, useTeamActivity } from "@/lib/api/team";
import { useAuthStore } from "@/store/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ShieldAlert, Activity, FileText, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function SecurityPage() {
  const workspaceId = useAuthStore(state => state.workspace?.id);
  
  const { data: auditLogs, isLoading: loadingLogs } = useAuditLogs(workspaceId || "");
  const { data: securityEvents, isLoading: loadingEvents } = useSecurityEvents();
  const { data: activity, isLoading: loadingActivity } = useTeamActivity();

  return (
    <Tabs defaultValue="audit" className="w-full space-y-6">
      <TabsList>
        <TabsTrigger value="audit" className="gap-2"><FileText className="w-4 h-4" /> Audit Logs</TabsTrigger>
        <TabsTrigger value="events" className="gap-2"><ShieldAlert className="w-4 h-4" /> Security Events</TabsTrigger>
        <TabsTrigger value="activity" className="gap-2"><Activity className="w-4 h-4" /> Team Activity</TabsTrigger>
      </TabsList>

      <TabsContent value="audit" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Audit Logs</CardTitle>
            <CardDescription>A complete immutable ledger of administrative actions within the workspace.</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingLogs ? (
              <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
            ) : !auditLogs || auditLogs.length === 0 ? (
              <div className="text-center p-8 text-muted-foreground border border-dashed rounded-md">No audit logs found.</div>
            ) : (
              <div className="border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Resource</TableHead>
                      <TableHead>IP Address</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {auditLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="text-muted-foreground text-sm whitespace-nowrap">
                          {new Date(log.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell className="font-medium">{log.user_email}</TableCell>
                        <TableCell><Badge variant="outline">{log.action}</Badge></TableCell>
                        <TableCell className="text-muted-foreground text-sm">{log.resource}</TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">{log.ip_address}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="events" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-destructive">Security Alerts</CardTitle>
            <CardDescription>Detected anomalies and security events requiring attention.</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingEvents ? (
              <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
            ) : !securityEvents || securityEvents.length === 0 ? (
              <div className="text-center p-8 text-muted-foreground border border-dashed rounded-md bg-emerald-50/50">
                <ShieldAlert className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-50" />
                No security alerts detected. Workspace is secure.
              </div>
            ) : (
              <div className="space-y-4">
                {securityEvents.map(event => (
                  <div key={event.id} className="flex gap-4 p-4 border rounded-md bg-muted/20 items-start">
                    <div className={`p-2 rounded-full mt-1 ${event.severity === 'high' ? 'bg-destructive/20 text-destructive' : 'bg-amber-500/20 text-amber-600'}`}>
                      <ShieldAlert className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h4 className="font-semibold">{event.type}</h4>
                        <span className="text-xs text-muted-foreground">{new Date(event.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="activity" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Team Activity Trends</CardTitle>
            <CardDescription>Recent general actions performed by team members.</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingActivity ? (
              <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
            ) : !activity || activity.length === 0 ? (
              <div className="text-center p-8 text-muted-foreground border border-dashed rounded-md">No recent activity.</div>
            ) : (
              <div className="space-y-4">
                {activity.map(act => (
                  <div key={act.id} className="flex gap-4 items-center p-3 border-b last:border-0">
                    <div className="w-2 h-2 rounded-full bg-primary/40" />
                    <div className="flex-1 text-sm">
                      <span className="font-semibold">{act.user}</span> {act.action}
                    </div>
                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                      {new Date(act.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
