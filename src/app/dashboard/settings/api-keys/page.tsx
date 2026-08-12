"use client";

import { useApiKeys, useCreateApiKey, useRevokeApiKey } from "@/lib/api/settings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, Plus, Copy, Trash2, Key } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function ApiKeysPage() {
  const { data: keys, isLoading } = useApiKeys();
  const { mutate: createKey, isPending: creating } = useCreateApiKey();
  const { mutate: revokeKey, isPending: revoking } = useRevokeApiKey();

  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState("");
  const [scopes, setScopes] = useState<string[]>(["read:tickets", "write:tickets"]);
  const [newKeyData, setNewKeyData] = useState<{ raw_key: string; name: string } | null>(null);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createKey({ name, scopes }, {
      onSuccess: (data) => {
        setNewKeyData(data);
        setName("");
        // Keep dialog open to show the key
      }
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">API Keys</h2>
          <p className="text-muted-foreground mt-1">
            Manage authentication keys for accessing the SupportGPT REST API.
          </p>
        </div>
        
        <Dialog open={isOpen} onOpenChange={(open) => {
          setIsOpen(open);
          if (!open) setNewKeyData(null);
        }}>
          <DialogTrigger render={<Button className="gap-2" />}>
            <Plus className="w-4 h-4" /> Generate Key
          </DialogTrigger>
          <DialogContent>
            {newKeyData ? (
              <div className="space-y-6">
                <DialogHeader>
                  <DialogTitle>API Key Generated</DialogTitle>
                  <DialogDescription>
                    Please copy this key now. For security reasons, you will not be able to see it again.
                  </DialogDescription>
                </DialogHeader>
                <div className="p-4 border rounded-md bg-muted/50 flex items-center justify-between">
                  <code className="font-mono text-sm">{newKeyData.raw_key}</code>
                  <Button variant="ghost" size="icon" onClick={() => copyToClipboard(newKeyData.raw_key)}>
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
                <DialogFooter>
                  <Button onClick={() => setIsOpen(false)}>Done</Button>
                </DialogFooter>
              </div>
            ) : (
              <form onSubmit={handleCreate}>
                <DialogHeader>
                  <DialogTitle>Generate New API Key</DialogTitle>
                  <DialogDescription>Create a new key to authenticate programmatic requests.</DialogDescription>
                </DialogHeader>
                <div className="py-6 space-y-6">
                  <div className="space-y-2">
                    <Label>Key Name</Label>
                    <Input placeholder="e.g. Production Backend" value={name} onChange={e => setName(e.target.value)} required />
                  </div>
                  <div className="space-y-3">
                    <Label>Scopes</Label>
                    <div className="grid grid-cols-2 gap-4 border p-4 rounded-md bg-muted/20">
                      <div className="flex items-center gap-2">
                        <Checkbox id="read-tick" checked={scopes.includes("read:tickets")} onCheckedChange={() => {}} />
                        <Label htmlFor="read-tick" className="font-normal cursor-pointer text-sm">Read Tickets</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <Checkbox id="write-tick" checked={scopes.includes("write:tickets")} onCheckedChange={() => {}} />
                        <Label htmlFor="write-tick" className="font-normal cursor-pointer text-sm">Write Tickets</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <Checkbox id="read-kb" checked={scopes.includes("read:knowledge")} onCheckedChange={() => {}} />
                        <Label htmlFor="read-kb" className="font-normal cursor-pointer text-sm">Read Knowledge</Label>
                      </div>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" type="button" onClick={() => setIsOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={creating || !name}>
                    {creating && <Loader2 className="w-4 h-4 mr-2 animate-spin" />} Generate
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Keys</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
          ) : !keys || keys.length === 0 ? (
            <div className="text-center p-12 text-muted-foreground border border-dashed rounded-md bg-muted/10">
              <Key className="w-8 h-8 mx-auto mb-3 opacity-20" />
              <p>No API keys generated yet.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Token</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Last Used</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {keys.map((key) => (
                  <TableRow key={key.id}>
                    <TableCell className="font-medium">{key.name}</TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {key.key_preview || "sk_live_...xxxx"}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{new Date(key.created_at).toLocaleDateString()}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {key.last_used ? new Date(key.last_used).toLocaleString() : 'Never'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" className="text-destructive" onClick={() => revokeKey(key.id)} disabled={revoking}>
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
