"use client";

import { useTeamMembers, useUpdateMemberStatus } from "@/lib/api/team";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MoreHorizontal, Loader2, ShieldBan, ShieldCheck } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useRouter } from "next/navigation";

export default function TeamPage() {
  const { data: members, isLoading } = useTeamMembers();
  const { mutate: updateStatus } = useUpdateMemberStatus();
  const router = useRouter();
  const currentUser = useAuthStore(state => state.user);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12 text-muted-foreground">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (!members || members.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 border rounded-md border-dashed bg-muted/10">
        <h3 className="text-lg font-medium">No team members found</h3>
        <p className="text-sm text-muted-foreground mt-1">This workspace doesn't have any members yet.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border bg-background shadow-sm">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Member</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Joined</TableHead>
            <TableHead className="text-right w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {members.map((member) => (
            <TableRow key={member.id} className={member.status === "suspended" ? "opacity-60" : ""}>
              <TableCell className="font-medium cursor-pointer" onClick={() => router.push(`/dashboard/team/${member.id}`)}>
                <div className="flex items-center gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{(member.user_full_name || member.user_email || "U")[0].toUpperCase()}</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span>{member.user_full_name || member.user_email.split('@')[0]}</span>
                    {currentUser?.id === member.user_id && <span className="text-[10px] text-muted-foreground">(You)</span>}
                  </div>
                </div>
              </TableCell>
              <TableCell className="text-muted-foreground">{member.user_email}</TableCell>
              <TableCell>
                <Badge variant={member.role === "Owner" || member.role === "admin" ? "default" : "secondary"}>
                  {member.role || "Member"}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={member.status === "active" ? "outline" : "destructive"} className="capitalize">
                  {member.status || "active"}
                </Badge>
              </TableCell>
              <TableCell className="text-muted-foreground text-sm">
                {new Date(member.joined_at).toLocaleDateString()}
              </TableCell>
              <TableCell className="text-right">
                <DropdownMenu>
                  <DropdownMenuTrigger>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Manage User</DropdownMenuLabel>
                    <DropdownMenuItem onClick={() => router.push(`/dashboard/team/${member.id}`)}>View Profile</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    {member.status === 'active' ? (
                      <DropdownMenuItem 
                        onClick={() => updateStatus({ id: member.id, status: 'suspended' })}
                        className="text-amber-600 gap-2"
                      >
                        <ShieldBan className="h-4 w-4" /> Suspend Member
                      </DropdownMenuItem>
                    ) : (
                      <DropdownMenuItem 
                        onClick={() => updateStatus({ id: member.id, status: 'active' })}
                        className="text-emerald-600 gap-2"
                      >
                        <ShieldCheck className="h-4 w-4" /> Reactivate Member
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem className="text-destructive">Remove from Workspace</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
