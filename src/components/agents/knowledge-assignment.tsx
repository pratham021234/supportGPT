"use client";

import { useState } from "react";
import { useAgent, useAssignKnowledge } from "@/lib/api/agents";
import { useDocuments } from "@/lib/api/knowledge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { AlertCircle, CheckCircle2, FileText, Globe, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

export function KnowledgeAssignment({ agentId }: { agentId: string }) {
  const { data: agent } = useAgent(agentId);
  const { data: documents, isLoading: isLoadingDocs } = useDocuments();
  const { mutate: assignKnowledge, isPending, isSuccess, isError, error } = useAssignKnowledge(agentId);
  
  const [search, setSearch] = useState("");
  // Mocking assigned documents state (normally fetched from agent.knowledge_scopes)
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());

  const handleToggleDoc = (docId: string) => {
    const newSet = new Set(selectedDocs);
    if (newSet.has(docId)) {
      newSet.delete(docId);
    } else {
      newSet.add(docId);
    }
    setSelectedDocs(newSet);
  };

  const handleSave = () => {
    // In a real implementation, you would pass the full list or diffs.
    // Assuming backend takes document_ids array
    assignKnowledge({
      document_ids: Array.from(selectedDocs)
    });
  };

  const filteredDocs = documents?.filter(d => 
    d.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Knowledge Sources</CardTitle>
        <CardDescription>Select the documents and websites this agent can use to answer questions.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search available knowledge..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="border rounded-md divide-y max-h-[400px] overflow-auto">
          {isLoadingDocs ? (
            <div className="p-4 space-y-4">
              <Skeleton className="h-6 w-full" />
              <Skeleton className="h-6 w-full" />
              <Skeleton className="h-6 w-full" />
            </div>
          ) : !filteredDocs || filteredDocs.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No knowledge sources found. Add some in the Knowledge Base first.
            </div>
          ) : (
            filteredDocs.map((doc) => (
              <div key={doc.id} className="flex items-center space-x-3 p-4 hover:bg-muted/50 transition-colors">
                <Checkbox 
                  id={`doc-${doc.id}`} 
                  checked={selectedDocs.has(doc.id)}
                  onCheckedChange={() => handleToggleDoc(doc.id)}
                />
                <label 
                  htmlFor={`doc-${doc.id}`}
                  className="flex flex-1 items-center justify-between cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  <div className="flex items-center gap-2">
                    {doc.file_type || doc.source_id ? (
                      <Globe className="h-4 w-4 text-blue-500" />
                    ) : (
                      <FileText className="h-4 w-4 text-red-500" />
                    )}
                    <span>{doc.title}</span>
                  </div>
                  <Badge variant="outline" className="capitalize text-[10px] font-normal">
                    {doc.file_type || (doc.source_id ? "URL" : "FAQ")}
                  </Badge>
                </label>
              </div>
            ))
          )}
        </div>

        {isError && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Failed to assign knowledge: {(error as any)?.message || "Unknown error"}
          </div>
        )}

        {isSuccess && (
          <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Knowledge sources assigned successfully.
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <p className="text-sm text-muted-foreground">
            {selectedDocs.size} source(s) selected
          </p>
          <Button onClick={handleSave} disabled={isPending}>
            {isPending ? "Saving..." : "Save Assignments"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
