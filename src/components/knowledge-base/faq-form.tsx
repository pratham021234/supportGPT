"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateFaq } from "@/lib/api/knowledge";
import { AlertCircle, CheckCircle2 } from "lucide-react";

export function FAQForm({ onSuccess }: { onSuccess: () => void }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [category, setCategory] = useState("");
  const { mutate: createFaq, isPending, isError, error, isSuccess } = useCreateFaq();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question || !answer) return;
    
    createFaq({ question, answer, category }, {
      onSuccess: () => {
        setTimeout(() => onSuccess(), 1000);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="question">Question</Label>
        <Input 
          id="question" 
          placeholder="e.g., How do I reset my password?" 
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="answer">Answer</Label>
        <Textarea 
          id="answer" 
          placeholder="Provide the complete answer here..." 
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          required
          rows={4}
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="category">Category (Optional)</Label>
        <Input 
          id="category" 
          placeholder="e.g., Billing, Technical Support" 
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
      </div>

      {isError && (
        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          Failed to save FAQ: {(error as any)?.message || "Unknown error"}
        </div>
      )}

      {isSuccess && (
        <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" />
          FAQ saved and processed successfully.
        </div>
      )}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onSuccess} disabled={isPending}>Cancel</Button>
        <Button type="submit" disabled={!question || !answer || isPending}>
          {isPending ? "Saving..." : "Save FAQ"}
        </Button>
      </div>
    </form>
  );
}
