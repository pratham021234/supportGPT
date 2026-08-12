"use client";

import { useTeamMember, useUpdateMemberRole, useRoles } from "@/lib/api/team";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Loader2, ArrowLeft, ShieldBan, MessageSquare, Ticket } from "lucide-react";
import { useRouter } from "next/navigation";
import { Label } from "@/components/ui/label";

export default function MemberProfilePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { data: member, isLoading } = useTeamMember(params.id);
  const { data: roles } = useRoles();
  const { mutate: updateRole, isPending: isUpdatingRole } = useUpdateMemberRole();

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  if (!member) {
    return <div>Member not found.</div>;
  }

  return (
    <div className="max-w-4xl space-y-6">
      <Button variant="ghost" size="sm" className="mb-2 -ml-3 text-muted-foreground" onClick={() => router.back()}>
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Directory
      </Button>
      
      <div className="flex flex-col md:flex-row gap-6">
        <Card className="flex-1">
          <CardHeader className="pb-4">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-4">
                <Avatar className="w-16 h-16">
                  <AvatarFallback className="text-xl">{(member.user_full_name || member.user_email)[0].toUpperCase()}</AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-2xl">{member.user_full_name || member.user_email.split('@')[0]}</CardTitle>
                  <CardDescription className="mt-1">{member.user_email}</CardDescription>
                  <div className="mt-2 flex gap-2">
                    <Badge variant={member.status === "active" ? "default" : "destructive"}>{member.status}</Badge>
                    <Badge variant="secondary">{member.role}</Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6 pt-4 border-t">
            <div className="space-y-2">
              <Label>Assigned Role</Label>
              <div className="flex gap-4">
                <Select 
                  defaultValue={member.role} // Using name here for MVP mapping
                  onValueChange={(val) => updateRole({ id: member.id, role_id: val })}
                  disabled={isUpdatingRole}
                >
                  <SelectTrigger className="w-64">
                    <SelectValue placeholder="Select Role" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles?.map(r => (
                      <SelectItem key={r.id} value={r.id}>{r.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {isUpdatingRole && <Loader2 className="w-4 h-4 animate-spin text-muted-foreground mt-3" />}
              </div>
              <p className="text-xs text-muted-foreground">Changing a role instantly updates permissions across the workspace.</p>
            </div>
          </CardContent>
        </Card>

        <div className="w-full md:w-80 space-y-6 flex-shrink-0">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Activity Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Ticket className="w-4 h-4" /> Assigned Tickets
                </div>
                <span className="font-semibold">12</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MessageSquare className="w-4 h-4" /> Active Chats
                </div>
                <span className="font-semibold">4</span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-destructive/20 bg-destructive/5">
            <CardHeader>
              <CardTitle className="text-sm font-semibold text-destructive flex items-center gap-2">
                <ShieldBan className="w-4 h-4" /> Danger Zone
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button variant="destructive" className="w-full">Deactivate User</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
