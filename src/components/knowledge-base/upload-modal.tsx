"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, FileText, Globe, MessageCircleQuestion } from "lucide-react";
import { FileUpload } from "./file-upload";
import { WebsiteForm } from "./website-form";
import { FAQForm } from "./faq-form";

export function UploadModal() {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button className="shrink-0 gap-2" />}>
        <Plus className="h-4 w-4" />
        Add Knowledge
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Add Knowledge Source</DialogTitle>
          <DialogDescription>
            Upload files, crawl websites, or manually add FAQs to train your AI agents.
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="file" className="w-full mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="file" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              File Upload
            </TabsTrigger>
            <TabsTrigger value="website" className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Website
            </TabsTrigger>
            <TabsTrigger value="faq" className="flex items-center gap-2">
              <MessageCircleQuestion className="h-4 w-4" />
              FAQ
            </TabsTrigger>
          </TabsList>
          <TabsContent value="file" className="mt-4">
            <FileUpload onSuccess={() => setOpen(false)} />
          </TabsContent>
          <TabsContent value="website" className="mt-4">
            <WebsiteForm onSuccess={() => setOpen(false)} />
          </TabsContent>
          <TabsContent value="faq" className="mt-4">
            <FAQForm onSuccess={() => setOpen(false)} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
