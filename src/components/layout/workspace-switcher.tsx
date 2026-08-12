"use client";

import { useWorkspaces, useSwitchWorkspace } from "@/lib/api/workspaces";
import { useAuthStore } from "@/store/authStore";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Building2, PlusCircle, Check, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

export function WorkspaceSwitcher() {
  const { workspace: currentWorkspace } = useAuthStore();
  const { data: workspaces, isLoading } = useWorkspaces();
  const { mutate: switchWorkspace, isPending } = useSwitchWorkspace();
  const router = useRouter();

  const handleWorkspaceChange = (workspaceId: string) => {
    if (workspaceId === "create_new") {
      // For MVP, we will handle modal popups via state or query params.
      // Easiest is navigating to a create page, or opening a dialog if we had one.
      // Since we need to keep it contained, we can trigger a global state or dialog here.
      router.push("?createWorkspace=true");
      return;
    }
    
    if (workspaceId !== currentWorkspace?.id) {
      switchWorkspace(workspaceId);
    }
  };

  if (!currentWorkspace) return null;

  return (
    <div className="w-full px-4 mb-4 mt-2">
      <Select value={currentWorkspace.id} onValueChange={(val) => handleWorkspaceChange(val as string)} disabled={isPending}>
        <SelectTrigger className="w-full bg-muted/50 border-0 h-12">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-1.5 rounded-md">
              {isPending ? <Loader2 className="h-4 w-4 text-primary animate-spin" /> : <Building2 className="h-4 w-4 text-primary" />}
            </div>
            <div className="flex flex-col items-start truncate max-w-[120px]">
              <span className="text-sm font-semibold truncate">{currentWorkspace.name}</span>
              <span className="text-[10px] uppercase text-muted-foreground tracking-wider">
                {/* Fallback to plan if available on current workspace object */}
                {(currentWorkspace as any).plan || 'Free'} Plan
              </span>
            </div>
          </div>
        </SelectTrigger>
        <SelectContent>
          {isLoading ? (
            <div className="p-4 text-center text-sm text-muted-foreground">Loading...</div>
          ) : (
            workspaces?.map((ws) => (
              <SelectItem key={ws.id} value={ws.id} className="cursor-pointer">
                <div className="flex items-center justify-between w-full">
                  <span>{ws.name}</span>
                  {currentWorkspace.id === ws.id && <Check className="h-4 w-4 opacity-50 ml-2" />}
                </div>
              </SelectItem>
            ))
          )}
          <div className="h-px bg-muted my-1" />
          <SelectItem value="create_new" className="cursor-pointer text-primary">
            <div className="flex items-center gap-2">
              <PlusCircle className="h-4 w-4" />
              <span>Create Workspace</span>
            </div>
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
