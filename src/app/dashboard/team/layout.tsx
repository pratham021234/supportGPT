"use client";

import { usePathname, useRouter } from "next/navigation";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Users, Mail, ShieldAlert, KeyRound } from "lucide-react";

export default function TeamLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const getActiveTab = () => {
    if (pathname.includes("/team/invitations")) return "invitations";
    if (pathname.includes("/team/roles")) return "roles";
    if (pathname.includes("/team/security")) return "security";
    return "directory";
  };

  const handleTabChange = (value: string) => {
    switch (value) {
      case "directory":
        router.push("/dashboard/team");
        break;
      case "invitations":
        router.push("/dashboard/team/invitations");
        break;
      case "roles":
        router.push("/dashboard/team/roles");
        break;
      case "security":
        router.push("/dashboard/team/security");
        break;
    }
  };

  // Do not show tabs if we are on a specific member's profile page 
  // (assuming profile page URL is /dashboard/team/[id] where [id] is not 'invitations', 'roles', 'security')
  const isProfilePage = pathname.split('/').length > 3 && !['invitations', 'roles', 'security'].includes(pathname.split('/').pop() || '');

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team & Access Management</h1>
          <p className="text-muted-foreground">
            Manage workspace members, assign roles, enforce permissions, and monitor security events.
          </p>
        </div>

        {!isProfilePage && (
          <Tabs value={getActiveTab()} onValueChange={handleTabChange} className="w-full">
            <TabsList className="grid grid-cols-4 w-[600px]">
              <TabsTrigger value="directory" className="gap-2">
                <Users className="h-4 w-4" /> Directory
              </TabsTrigger>
              <TabsTrigger value="invitations" className="gap-2">
                <Mail className="h-4 w-4" /> Invitations
              </TabsTrigger>
              <TabsTrigger value="roles" className="gap-2">
                <KeyRound className="h-4 w-4" /> Roles & Permissions
              </TabsTrigger>
              <TabsTrigger value="security" className="gap-2">
                <ShieldAlert className="h-4 w-4" /> Security & Audit
              </TabsTrigger>
            </TabsList>
          </Tabs>
        )}
      </div>

      <div className="mt-4">
        {children}
      </div>
    </div>
  );
}
