import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, FileText, Globe, File, MoreHorizontal, ArrowUpDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const documents = [
  { id: "doc_1", name: "Q3 Financial Report.pdf", type: "PDF", status: "Processed", chunks: 142, date: "2026-08-01" },
  { id: "doc_2", name: "API Documentation", type: "URL", status: "Processed", chunks: 856, date: "2026-08-02" },
  { id: "doc_3", name: "Employee Handbook.docx", type: "DOCX", status: "Processing", chunks: 0, date: "2026-08-06" },
  { id: "doc_4", name: "Pricing FAQs.md", type: "Markdown", status: "Error", chunks: 0, date: "2026-08-05" },
  { id: "doc_5", name: "Terms of Service.pdf", type: "PDF", status: "Processed", chunks: 45, date: "2026-07-28" },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case "Processed":
      return <Badge variant="default" className="bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20">Processed</Badge>;
    case "Processing":
      return <Badge variant="default" className="bg-amber-500/10 text-amber-500 hover:bg-amber-500/20">Processing...</Badge>;
    case "Error":
      return <Badge variant="destructive" className="bg-destructive/10 text-destructive hover:bg-destructive/20">Failed</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case "PDF":
      return <FileText className="h-4 w-4 text-red-500" />;
    case "URL":
      return <Globe className="h-4 w-4 text-blue-500" />;
    case "DOCX":
      return <File className="h-4 w-4 text-blue-600" />;
    case "Markdown":
      return <FileText className="h-4 w-4 text-zinc-500" />;
    default:
      return <File className="h-4 w-4" />;
  }
}

export default function KnowledgeBasePage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-muted-foreground">
            Manage the documents and URLs that your AI agents use to answer questions.
          </p>
        </div>
        <Button className="shrink-0 gap-2">
          <Plus className="h-4 w-4" />
          Add Knowledge
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search documents..." className="pl-8" />
        </div>
        <Button variant="outline">Filter</Button>
      </div>

      <div className="rounded-md border bg-background shadow-sm">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[300px]">
                <div className="flex items-center gap-1 cursor-pointer hover:text-foreground">
                  Name <ArrowUpDown className="h-3 w-3" />
                </div>
              </TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Knowledge Chunks</TableHead>
              <TableHead>Date Added</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(doc.type)}
                    {doc.name}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className="font-normal text-xs">{doc.type}</Badge>
                </TableCell>
                <TableCell>{getStatusBadge(doc.status)}</TableCell>
                <TableCell className="text-right">{doc.chunks}</TableCell>
                <TableCell className="text-muted-foreground">{doc.date}</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem>View details</DropdownMenuItem>
                      <DropdownMenuItem>Re-process</DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
