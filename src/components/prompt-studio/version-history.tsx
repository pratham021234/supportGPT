"use client";

import { usePromptVersions, useRollbackVersion } from "@/lib/api/prompt-studio";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { History, RotateCcw, Eye, Loader2 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useState } from "react";

interface VersionHistoryProps {
  agentId: string;
}

export function VersionHistory({ agentId }: VersionHistoryProps) {
  const { data: versions, isLoading } = usePromptVersions(agentId);
  const { mutate: rollback, isPending } = useRollbackVersion(agentId);
  
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-4 pt-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h3 className="text-lg font-medium flex items-center gap-2">
          <History className="h-5 w-5" /> Version History
        </h3>
        <p className="text-sm text-muted-foreground mt-1">
          View past versions of this agent's configuration and roll back if necessary.
        </p>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Version</TableHead>
              <TableHead>Changes</TableHead>
              <TableHead>Author</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {versions?.map((version) => (
              <TableRow key={version.version_number}>
                <TableCell className="font-medium">v{version.version_number}</TableCell>
                <TableCell>{version.changes}</TableCell>
                <TableCell>{version.created_by}</TableCell>
                <TableCell>{new Date(version.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Badge variant={version.status === "ACTIVE" ? "default" : "secondary"}>
                    {version.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right space-x-2">
                  <Button variant="ghost" size="icon" title="View Diff">
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  </Button>
                  
                  {version.status !== "ACTIVE" && (
                    <Dialog open={selectedVersion === version.version_number} onOpenChange={(open) => setSelectedVersion(open ? version.version_number : null)}>
                      <DialogTrigger render={
                        <Button variant="ghost" size="icon" title="Rollback to this version">
                          <RotateCcw className="h-4 w-4 text-muted-foreground hover:text-amber-600" />
                        </Button>
                      } />
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Rollback to v{version.version_number}?</DialogTitle>
                          <DialogDescription>
                            This will overwrite the current active prompt and configuration with the settings from v{version.version_number}. This action will create a new version snapshot.
                          </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button variant="outline" onClick={() => setSelectedVersion(null)}>Cancel</Button>
                          <Button 
                            variant="destructive"
                            disabled={isPending}
                            onClick={() => {
                              rollback(version.version_number, {
                                onSuccess: () => setSelectedVersion(null)
                              });
                            }}
                          >
                            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Confirm Rollback
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
