"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCrawlWebsite } from "@/lib/api/knowledge";
import { AlertCircle, CheckCircle2 } from "lucide-react";

export function WebsiteForm({ onSuccess }: { onSuccess: () => void }) {
  const [url, setUrl] = useState("");
  const { mutate: crawlWebsite, isPending, isError, error, isSuccess } = useCrawlWebsite();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    
    crawlWebsite({ url }, {
      onSuccess: () => {
        setTimeout(() => onSuccess(), 1000);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="url">Website URL</Label>
        <Input 
          id="url" 
          placeholder="https://example.com/docs" 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          type="url"
        />
        <p className="text-xs text-muted-foreground">
          Our crawler will extract text content from this page and its sub-pages up to 2 levels deep.
        </p>
      </div>

      {isError && (
        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          Failed to start crawl: {(error as any)?.message || "Unknown error"}
        </div>
      )}

      {isSuccess && (
        <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" />
          Website crawling started successfully.
        </div>
      )}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onSuccess} disabled={isPending}>Cancel</Button>
        <Button type="submit" disabled={!url || isPending}>
          {isPending ? "Starting..." : "Start Crawling"}
        </Button>
      </div>
    </form>
  );
}
