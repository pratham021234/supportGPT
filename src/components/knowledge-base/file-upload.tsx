"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { UploadCloud, File, X, AlertCircle, CheckCircle2 } from "lucide-react";
import { useUploadDocument } from "@/lib/api/knowledge";

export function FileUpload({ onSuccess }: { onSuccess: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { mutate: uploadDoc, isPending, isError, error, isSuccess } = useUploadDocument();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (!file) return;
    uploadDoc({ file }, {
      onSuccess: () => {
        setTimeout(() => onSuccess(), 1000);
      }
    });
  };

  return (
    <div className="space-y-4">
      {!file ? (
        <div
          className={`border-2 border-dashed rounded-lg p-10 text-center flex flex-col items-center justify-center transition-colors cursor-pointer ${
            dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleChange}
          />
          <UploadCloud className="h-10 w-10 text-muted-foreground mb-4" />
          <h3 className="font-medium mb-1">Click or drag file to this area to upload</h3>
          <p className="text-sm text-muted-foreground">
            Support for a single PDF, DOCX, TXT, or MD upload.
          </p>
        </div>
      ) : (
        <div className="border rounded-lg p-4 flex items-center justify-between bg-muted/30">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="bg-primary/10 p-2 rounded shrink-0">
              <File className="h-6 w-6 text-primary" />
            </div>
            <div className="truncate">
              <p className="font-medium text-sm truncate">{file.name}</p>
              <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setFile(null)} disabled={isPending}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      {isError && (
        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          Failed to upload: {(error as any)?.message || "Unknown error"}
        </div>
      )}

      {isSuccess && (
        <div className="bg-emerald-500/10 text-emerald-600 text-sm p-3 rounded flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" />
          Upload successful! Processing has started.
        </div>
      )}

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onSuccess} disabled={isPending}>Cancel</Button>
        <Button onClick={handleUpload} disabled={!file || isPending}>
          {isPending ? "Uploading..." : "Upload File"}
        </Button>
      </div>
    </div>
  );
}
