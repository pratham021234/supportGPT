"use client";

import { useWebhooks, useCreateWebhook } from "@/lib/api/settings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, Plus, Trash2, Webhook as WebhookIcon, ExternalLink } from "lucide-react";
import { useState } from "react";

export default function WebhooksPage() {
  const { data: webhooks, isLoading } = useWebhooks();
  const { mutate: createWebhook, isPending } = useCreateWebhook();

  const [isOpen, setIsOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [events, setEvents] = useState<string[]>([]);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createWebhook({ url, events }, {
      onSuccess: () => {
        setIsOpen(false);
        setUrl("");
        setEvents([]);
      }
    });
  };

  const toggleEvent = (evt: string) => {
    setEvents(prev => prev.includes(evt) ? prev.filter(e => e !== evt) : [...prev, evt]);
  };

  const availableEvents = [
    "ticket.created", "ticket.resolved", "conversation.started", "agent.failed", "document.processed"
  ];

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Webhooks</h2>
          <p className="text-muted-foreground mt-1">
            Configure endpoints to receive real-time HTTP POST payloads when events happen.
          </p>
        </div>
        
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger render={<Button className="gap-2" />}>
            <Plus className="w-4 h-4" /> Add Endpoint
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle>Add Webhook Endpoint</DialogTitle>
                <DialogDescription>Enter the URL where you want to receive payloads.</DialogDescription>
              </DialogHeader>
              <div className="py-6 space-y-6">
                <div className="space-y-2">
                  <Label>Payload URL</Label>
                  <Input placeholder="https://api.yourdomain.com/webhooks" value={url} onChange={e => setUrl(e.target.value)} required type="url" />
                </div>
                <div className="space-y-3">
                  <Label>Events to send</Label>
                  <div className="space-y-3 border p-4 rounded-md bg-muted/20">
                    {availableEvents.map(evt => (
                      <div key={evt} className="flex items-center gap-2">
                        <Checkbox id={evt} checked={events.includes(evt)} onCheckedChange={() => toggleEvent(evt)} />
                        <Label htmlFor={evt} className="font-normal cursor-pointer text-sm font-mono">{evt}</Label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" type="button" onClick={() => setIsOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={isPending || !url || events.length === 0}>
                  {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />} Create Endpoint
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
          ) : !webhooks || webhooks.length === 0 ? (
            <div className="text-center p-12 text-muted-foreground border border-dashed rounded-md bg-muted/10">
              <WebhookIcon className="w-8 h-8 mx-auto mb-3 opacity-20" />
              <p>No webhooks configured.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>URL</TableHead>
                  <TableHead>Events</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {webhooks.map((wh) => (
                  <TableRow key={wh.id}>
                    <TableCell className="font-medium flex items-center gap-2">
                      {wh.url} <ExternalLink className="w-3 h-3 text-muted-foreground" />
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap max-w-[200px]">
                        {wh.events.map(e => <Badge key={e} variant="secondary" className="font-mono text-[10px]">{e}</Badge>)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={wh.status === 'active' ? 'outline' : 'destructive'} className={wh.status === 'active' ? 'text-emerald-600 border-emerald-200 bg-emerald-50' : ''}>
                        {wh.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button variant="ghost" size="sm">Test</Button>
                      <Button variant="ghost" size="icon" className="text-destructive">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
