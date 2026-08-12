"use client";

import { ColumnDef } from "@tanstack/react-table";
import { KnowledgeDocument } from "@/lib/api/knowledge";
import { Badge } from "@/components/ui/badge";
import { FileText, Globe, File, MoreHorizontal, ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const getTypeIcon = (type?: string) => {
  switch (type?.toLowerCase()) {
    case "pdf":
      return <FileText className="h-4 w-4 text-red-500" />;
    case "website":
    case "url":
      return <Globe className="h-4 w-4 text-blue-500" />;
    case "docx":
      return <File className="h-4 w-4 text-blue-600" />;
    case "markdown":
    case "md":
      return <FileText className="h-4 w-4 text-zinc-500" />;
    case "faq":
      return <FileText className="h-4 w-4 text-emerald-500" />;
    default:
      return <File className="h-4 w-4 text-muted-foreground" />;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "READY":
    case "COMPLETED":
      return <Badge variant="default" className="bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20">Ready</Badge>;
    case "PROCESSING":
    case "QUEUED":
      return <Badge variant="default" className="bg-amber-500/10 text-amber-500 hover:bg-amber-500/20 capitalize">{status.toLowerCase()}...</Badge>;
    case "FAILED":
    case "ERROR":
      return <Badge variant="destructive" className="bg-destructive/10 text-destructive hover:bg-destructive/20">Failed</Badge>;
    default:
      return <Badge variant="outline" className="capitalize">{status.toLowerCase()}</Badge>;
  }
};

export const documentColumns: ColumnDef<KnowledgeDocument>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
        className="translate-y-[2px]"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
        className="translate-y-[2px]"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "title",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4 h-8 data-[state=open]:bg-accent"
        >
          <span>Name</span>
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => {
      const type = row.original.file_type || (row.original.source_id ? "URL" : "FAQ");
      return (
        <div className="flex items-center gap-2 font-medium">
          {getTypeIcon(type)}
          <span className="truncate max-w-[300px]">{row.getValue("title")}</span>
        </div>
      )
    },
  },
  {
    accessorKey: "file_type",
    header: "Type",
    cell: ({ row }) => {
      const type = (row.getValue("file_type") as string) || (row.original.source_id ? "Website" : "FAQ");
      return <Badge variant="outline" className="font-normal text-xs">{type}</Badge>
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      return getStatusBadge(row.getValue("status"))
    },
  },
  {
    accessorKey: "created_at",
    header: () => <div className="text-right">Date Added</div>,
    cell: ({ row }) => {
      const date = new Date(row.getValue("created_at"));
      return <div className="text-right text-muted-foreground">{date.toLocaleDateString()}</div>
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const doc = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger render={
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          } />
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => window.location.href = `/dashboard/knowledge-base/${doc.id}`}>
              View details
            </DropdownMenuItem>
            <DropdownMenuItem>Reprocess</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive">Delete document</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
];
