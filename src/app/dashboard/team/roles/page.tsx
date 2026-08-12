"use client";

import { useState } from "react";
import { useRoles, usePermissions, useCreateRole } from "@/lib/api/team";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Check, X, Plus, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function RolesPage() {
  const { data: roles, isLoading: isLoadingRoles } = useRoles();
  const { data: permissions, isLoading: isLoadingPerms } = usePermissions();
  const { mutate: createRole, isPending } = useCreateRole();

  const [isOpen, setIsOpen] = useState(false);
  const [newRoleName, setNewRoleName] = useState("");
  const [selectedPerms, setSelectedPerms] = useState<string[]>([]);

  if (isLoadingRoles || isLoadingPerms) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createRole({ name: newRoleName, permissions: selectedPerms }, {
      onSuccess: () => {
        setIsOpen(false);
        setNewRoleName("");
        setSelectedPerms([]);
      }
    });
  };

  const togglePerm = (permId: string) => {
    setSelectedPerms(prev => prev.includes(permId) ? prev.filter(p => p !== permId) : [...prev, permId]);
  };

  // Group permissions for matrix view
  const resources = Array.from(new Set(permissions?.map(p => p.resource) || []));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-medium">Permission Matrix</h2>
          <p className="text-sm text-muted-foreground">View and manage granular access controls across the workspace.</p>
        </div>
        
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger render={<Button className="gap-2" />}>
            <Plus className="w-4 h-4" /> Create Custom Role
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle>Create Custom Role</DialogTitle>
                <DialogDescription>Define a new role and configure its specific permissions.</DialogDescription>
              </DialogHeader>
              
              <div className="space-y-6 py-4">
                <div className="space-y-2">
                  <Label>Role Name</Label>
                  <Input value={newRoleName} onChange={(e) => setNewRoleName(e.target.value)} placeholder="e.g. Content Reviewer" required />
                </div>
                
                <div className="space-y-3">
                  <Label>Permissions</Label>
                  <ScrollArea className="h-[300px] border rounded-md p-4 bg-muted/20">
                    <div className="space-y-6">
                      {resources.map(resource => (
                        <div key={resource}>
                          <h4 className="font-semibold text-sm capitalize mb-3 border-b pb-1">{resource}</h4>
                          <div className="grid grid-cols-2 gap-3">
                            {permissions?.filter(p => p.resource === resource).map(p => (
                              <div key={p.id} className="flex items-start gap-2">
                                <Checkbox 
                                  id={`chk-${p.id}`} 
                                  checked={selectedPerms.includes(p.id)}
                                  onCheckedChange={() => togglePerm(p.id)}
                                />
                                <Label htmlFor={`chk-${p.id}`} className="font-normal text-sm cursor-pointer leading-tight">
                                  {p.name}
                                </Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" type="button" onClick={() => setIsOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={isPending || !newRoleName}>
                  {isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />} Save Role
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="border rounded-md overflow-x-auto bg-background">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[250px] sticky left-0 bg-muted/50 font-semibold border-r">Permission</TableHead>
              {roles?.map(role => (
                <TableHead key={role.id} className="text-center min-w-[120px] bg-muted/10 font-semibold">
                  {role.name}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {permissions?.map(perm => (
              <TableRow key={perm.id}>
                <TableCell className="sticky left-0 bg-background border-r flex flex-col gap-1">
                  <span className="font-medium text-sm">{perm.name}</span>
                  <span className="text-[10px] text-muted-foreground uppercase">{perm.resource}</span>
                </TableCell>
                {roles?.map(role => (
                  <TableCell key={`${role.id}-${perm.id}`} className="text-center">
                    {/* For MVP, visually check owner/admin, or check role.permissions array if it exists */}
                    {(role.name === 'Owner' || (role.permissions && role.permissions.includes(perm.id))) ? (
                      <Check className="w-4 h-4 mx-auto text-emerald-500" />
                    ) : (
                      <X className="w-4 h-4 mx-auto text-muted-foreground/30" />
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
