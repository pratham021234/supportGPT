"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { useKnowledgeSearch } from "@/lib/api/knowledge";
import { Search, Loader2, FileText, AlertCircle } from "lucide-react";
import { useDebounce } from "@/hooks/use-debounce";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";

export function KnowledgeSearch() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  
  // Custom debounce hook is used if it exists, otherwise inline timeout.
  // Using simple timeout for standalone stability.
  const [debouncedQuery, setDebouncedQuery] = useState(query);
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
    }, 500);
    return () => clearTimeout(handler);
  }, [query]);

  const { data: results, isLoading, isError } = useKnowledgeSearch(debouncedQuery);

  useEffect(() => {
    if (query.length > 2) {
      setOpen(true);
    } else {
      setOpen(false);
    }
  }, [query]);

  return (
    <div className="relative flex-1 w-full max-w-lg">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Semantic search across knowledge base..."
              className="pl-8 w-full bg-muted/50 border-primary/20 focus-visible:ring-primary/30"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => {
                if (query.length > 2) setOpen(true);
              }}
            />
            {isLoading && (
              <Loader2 className="absolute right-2.5 top-2.5 h-4 w-4 animate-spin text-muted-foreground" />
            )}
          </div>
        </PopoverTrigger>
        <PopoverContent 
          className="w-[500px] p-0" 
          align="start"
          onOpenAutoFocus={(e) => e.preventDefault()}
        >
          <div className="border-b px-4 py-2 bg-muted/30">
            <p className="text-xs font-semibold text-muted-foreground">Search Results</p>
          </div>
          <ScrollArea className="max-h-[400px]">
            {isError ? (
              <div className="p-4 text-sm text-destructive flex items-center gap-2 justify-center">
                <AlertCircle className="h-4 w-4" />
                Error performing search
              </div>
            ) : !results || results.length === 0 ? (
              <div className="p-8 text-center text-sm text-muted-foreground">
                {isLoading ? "Searching..." : "No semantic matches found."}
              </div>
            ) : (
              <div className="flex flex-col">
                {results.map((result) => (
                  <div key={result.id} className="p-4 border-b last:border-0 hover:bg-muted/50 transition-colors cursor-pointer">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-primary" />
                        <span className="font-medium text-sm">
                          {result.metadata?.document_name || "Unknown Document"}
                        </span>
                      </div>
                      <Badge variant="outline" className="text-[10px]">
                        {(result.score * 100).toFixed(0)}% match
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 mt-1 leading-relaxed">
                      {result.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </PopoverContent>
      </Popover>
    </div>
  );
}
