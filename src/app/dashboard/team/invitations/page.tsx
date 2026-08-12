"use client";

import { useState } from "react";
import { usePendingInvitations } from "@/lib/api/workspaces";
import { useInviteMember, useRoles } from "@/lib/api/team";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Mail, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function InvitationsPage() {
  const { data: invitations, isLoading } = usePendingInvitations();
  const { data: roles } = useRoles();
  const { mutate: inviteMember, isPending } = useInviteMember();

  const [email, setEmail] = useState("");
  const [roleId, setRoleId] = useState("");

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !roleId) return;
    
    inviteMember({ email, role_id: roleId }, {
      onSuccess: () => {
        setEmail("");
        setRoleId("");
      }
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Invite New Member</CardTitle>
          <CardDescription>Send an email invitation to join this workspace.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleInvite} className="flex flex-col sm:flex-row gap-4 items-start">
            <div className="flex-1 space-y-2">
              <Input 
                type="email" 
                placeholder="user@example.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="w-full sm:w-48 space-y-2">
              <Select value={roleId} onValueChange={(val) => setRoleId(val as string)} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select Role" />
                </SelectTrigger>
                <SelectContent>
                  {roles?.map(r => (
                    <SelectItem key={r.id} value={r.id}>{r.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" disabled={isPending || !email || !roleId}>
              {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              <Mail className="w-4 h-4 mr-2" />
              Send Invite
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pending Invitations</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
          ) : !invitations || invitations.length === 0 ? (
            <div className="text-center p-8 text-muted-foreground border border-dashed rounded-md">
              No pending invitations.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Sent At</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invitations.map((inv) => (
                  <TableRow key={inv.id}>
                    <TableCell className="font-medium">{inv.email}</TableCell>
                    <TableCell>{inv.role || "Member"}</TableCell>
                    <TableCell className="text-muted-foreground">{new Date(inv.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50">
                        {inv.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button variant="ghost" size="sm" className="text-muted-foreground">Resend</Button>
                      <Button variant="ghost" size="icon" className="text-destructive"><Trash2 className="w-4 h-4" /></Button>
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
