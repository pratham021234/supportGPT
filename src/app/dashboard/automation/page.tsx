"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Workflow, Plus, Trash2, ArrowRight, Loader2, PlayCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function AutomationPage() {
  const { user } = useAuth();
  const [rules, setRules] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [isCreating, setIsCreating] = useState(false);
  const [newRule, setNewRule] = useState({
      name: "",
      trigger_event: "LOW_CONFIDENCE",
      conditionField: "confidence",
      conditionOp: "lt",
      conditionVal: "0.6",
      actionType: "CREATE_TICKET"
  });

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    try {
        const [rRes, eRes] = await Promise.all([
            fetch("/api/v1/automation/rules", { headers: { Authorization: `Bearer ${user.token}` } }),
            fetch("/api/v1/automation/executions", { headers: { Authorization: `Bearer ${user.token}` } })
        ]);
        
        if (rRes.ok) setRules(await rRes.json());
        if (eRes.ok) setExecutions(await eRes.json());
    } catch(e) {}
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [user]);
  
  const handleCreateRule = async () => {
      if (!user) return;
      setIsCreating(true);
      
      const payload = {
          name: newRule.name,
          trigger_event: newRule.trigger_event,
          conditions: [{ field: newRule.conditionField, operator: newRule.conditionOp, value: parseFloat(newRule.conditionVal) || newRule.conditionVal }],
          actions: [{ type: newRule.actionType, payload: {} }]
      };
      
      try {
          await fetch("/api/v1/automation/rules", {
              method: "POST",
              headers: { 
                  "Content-Type": "application/json",
                  Authorization: `Bearer ${user.token}` 
              },
              body: JSON.stringify(payload)
          });
          setNewRule({ ...newRule, name: "" }); // Reset
          await loadData();
      } catch(e) {}
      setIsCreating(false);
  };
  
  const handleDelete = async (id: string) => {
      if (!user) return;
      await fetch(`/api/v1/automation/rules/${id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${user.token}` }
      });
      await loadData();
  };

  return (
    <div className="flex flex-col gap-6 p-8 overflow-y-auto h-[calc(100vh-64px)]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Automation Engine</h1>
          <p className="text-zinc-500 mt-1">
            Build proactive IF/THEN workflows to operationalize your support.
          </p>
        </div>
      </div>

      <Tabs defaultValue="rules" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="rules" className="flex items-center"><Workflow className="w-4 h-4 mr-2" /> Rules Engine</TabsTrigger>
          <TabsTrigger value="executions" className="flex items-center"><Clock className="w-4 h-4 mr-2" /> Execution Logs</TabsTrigger>
        </TabsList>
        
        <TabsContent value="rules" className="space-y-6">
            
            {/* Rule Builder */}
            <Card className="border-indigo-100 bg-indigo-50/20">
                <CardHeader>
                    <CardTitle className="text-lg flex items-center text-indigo-900">
                        <Plus className="w-5 h-5 mr-2 text-indigo-500" /> Create New Rule
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-6 md:grid-cols-4 items-end">
                        <div className="space-y-2">
                            <Label>Rule Name</Label>
                            <Input placeholder="e.g. Escalate Low Confidence" value={newRule.name} onChange={e => setNewRule({...newRule, name: e.target.value})} />
                        </div>
                        
                        <div className="space-y-2">
                            <Label>When Event Happens</Label>
                            <Select value={newRule.trigger_event} onValueChange={v => setNewRule({...newRule, trigger_event: v || ""})}>
                                <SelectTrigger><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="LOW_CONFIDENCE">Low Confidence Answer</SelectItem>
                                    <SelectItem value="TICKET_CREATED">Ticket Created</SelectItem>
                                    <SelectItem value="CUSTOMER_FEEDBACK">Customer Feedback</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        
                        <div className="space-y-2">
                            <Label>If Condition</Label>
                            <div className="flex space-x-2">
                                <Input className="w-1/3" placeholder="Field" value={newRule.conditionField} onChange={e => setNewRule({...newRule, conditionField: e.target.value})} />
                                <Select value={newRule.conditionOp} onValueChange={v => setNewRule({...newRule, conditionOp: v || ""})}>
                                    <SelectTrigger className="w-1/3"><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="lt">&lt;</SelectItem>
                                        <SelectItem value="gt">&gt;</SelectItem>
                                        <SelectItem value="eq">=</SelectItem>
                                        <SelectItem value="contains">Contains</SelectItem>
                                    </SelectContent>
                                </Select>
                                <Input className="w-1/3" placeholder="Value" value={newRule.conditionVal} onChange={e => setNewRule({...newRule, conditionVal: e.target.value})} />
                            </div>
                        </div>
                        
                        <div className="space-y-2">
                            <Label>Then Action</Label>
                            <Select value={newRule.actionType} onValueChange={v => setNewRule({...newRule, actionType: v || ""})}>
                                <SelectTrigger><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="CREATE_TICKET">Create Ticket</SelectItem>
                                    <SelectItem value="SEND_EMAIL">Send Email Alert</SelectItem>
                                    <SelectItem value="SEND_WEBHOOK">Fire Webhook</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardContent>
                <CardFooter className="justify-end border-t border-indigo-100 pt-4 bg-white/50 rounded-b-xl">
                    <Button onClick={handleCreateRule} disabled={!newRule.name || isCreating}>
                        {isCreating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : "Save Rule"}
                    </Button>
                </CardFooter>
            </Card>

            {/* Active Rules List */}
            <div className="space-y-4">
                <h3 className="font-semibold text-lg">Active Rules</h3>
                {loading ? (
                    <Skeleton className="h-24 w-full" />
                ) : rules.length === 0 ? (
                    <div className="text-center py-12 border border-dashed rounded-lg text-zinc-500">No automation rules configured yet.</div>
                ) : (
                    rules.map(rule => (
                        <div key={rule.id} className="flex items-center justify-between p-4 bg-white border rounded-lg shadow-sm">
                            <div className="flex-1 flex flex-col">
                                <div className="flex items-center mb-2">
                                    <span className="font-semibold">{rule.name}</span>
                                    <span className={`ml-3 px-2 py-0.5 text-[10px] font-bold tracking-wide uppercase rounded bg-emerald-100 text-emerald-700`}>{rule.status}</span>
                                </div>
                                <div className="flex items-center text-sm font-mono text-zinc-600 bg-zinc-50 p-2 rounded w-fit border border-zinc-100">
                                    <span className="text-indigo-600 font-bold mr-2">IF</span> {rule.trigger_event} 
                                    <span className="text-zinc-400 mx-2">AND</span>
                                    {rule.conditions?.[0]?.field} {rule.conditions?.[0]?.operator} {rule.conditions?.[0]?.value}
                                    <ArrowRight className="w-4 h-4 mx-3 text-zinc-400" />
                                    <span className="text-rose-600 font-bold mr-2">THEN</span> {rule.actions?.[0]?.type}
                                </div>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => handleDelete(rule.id)} className="text-rose-500 hover:text-rose-600 hover:bg-rose-50">
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        </div>
                    ))
                )}
            </div>
            
        </TabsContent>
        
        <TabsContent value="executions">
            <Card>
                <CardHeader>
                    <CardTitle>Recent Workflow Executions</CardTitle>
                    <CardDescription>Track exactly what happened when rules triggered.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {loading ? (
                            Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)
                        ) : executions.length === 0 ? (
                            <div className="text-center py-8 text-zinc-500">No recent executions.</div>
                        ) : (
                            executions.map(exec => (
                                <div key={exec.id} className="flex items-center justify-between p-3 border-b last:border-0">
                                    <div>
                                        <div className="flex items-center space-x-2">
                                            {exec.status === "SUCCESS" ? (
                                                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                            ) : (
                                                <div className="w-2 h-2 rounded-full bg-rose-500" />
                                            )}
                                            <span className="font-medium text-sm">Rule Execution</span>
                                        </div>
                                        <div className="text-xs text-zinc-500 mt-1 flex items-center">
                                            <PlayCircle className="w-3 h-3 mr-1" />
                                            {new Date(exec.executed_at).toLocaleString()}
                                            {exec.error_message && <span className="ml-2 text-rose-500">- {exec.error_message}</span>}
                                        </div>
                                    </div>
                                    <div className="text-xs text-zinc-400 font-mono">
                                        ID: {exec.id.substring(0,8)}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
