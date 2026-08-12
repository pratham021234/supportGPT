"use client";

import { useState } from "react";
import Link from "next/link";
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
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Search, Filter, MoreHorizontal, Plus, CheckSquare, Trash, CheckCircle2, UserPlus, Clock } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";

import { useTickets, TicketPriority, TicketStatus } from "@/lib/api/tickets";
import { CreateTicketDialog } from "@/components/tickets/create-ticket-dialog";

export const getPriorityBadge = (priority: TicketPriority) => {
  switch (priority) {
    case "URGENT":
      return <Badge variant="destructive" className="bg-red-600/10 text-red-600 hover:bg-red-600/20 border-red-600/20">Urgent</Badge>;
    case "HIGH":
      return <Badge variant="destructive" className="bg-orange-500/10 text-orange-500 hover:bg-orange-500/20 border-orange-500/20">High</Badge>;
    case "MEDIUM":
      return <Badge variant="default" className="bg-amber-500/10 text-amber-500 hover:bg-amber-500/20 border-amber-500/20">Medium</Badge>;
    case "LOW":
      return <Badge variant="secondary" className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border-blue-500/20">Low</Badge>;
    default:
      return <Badge variant="outline">{priority}</Badge>;
  }
};

export const getStatusBadge = (status: TicketStatus) => {
  switch (status) {
    case "OPEN":
      return <Badge variant="outline" className="border-destructive/30 text-destructive">Open</Badge>;
    case "IN_PROGRESS":
      return <Badge variant="outline" className="border-amber-500/30 text-amber-500">In Progress</Badge>;
    case "WAITING_CUSTOMER":
      return <Badge variant="outline" className="border-blue-500/30 text-blue-500">Waiting on Customer</Badge>;
    case "WAITING_INTERNAL":
      return <Badge variant="outline" className="border-purple-500/30 text-purple-500">Waiting Internal</Badge>;
    case "RESOLVED":
      return <Badge variant="outline" className="border-emerald-500/30 text-emerald-500">Resolved</Badge>;
    case "CLOSED":
      return <Badge variant="outline" className="border-slate-500/30 text-slate-500">Closed</Badge>;
    case "REOPENED":
      return <Badge variant="outline" className="border-rose-500/30 text-rose-500">Reopened</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

export default function TicketsPage() {
  const { data: tickets, isLoading } = useTickets();
  const [selectedTickets, setSelectedTickets] = useState<Set<string>>(new Set());
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const toggleSelectAll = () => {
    if (selectedTickets.size === tickets?.length) {
      setSelectedTickets(new Set());
    } else if (tickets) {
      setSelectedTickets(new Set(tickets.map(t => t.id)));
    }
  };

  const toggleSelect = (id: string) => {
    const newSet = new Set(selectedTickets);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedTickets(newSet);
  };

  const filteredTickets = tickets?.filter(t => 
    t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tickets</h1>
          <p className="text-muted-foreground">
            Manage, assign, and resolve customer support tickets.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/dashboard/tickets/operations">Operations Dashboard</Link>
          </Button>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Ticket
          </Button>
        </div>
      </div>

      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search tickets by subject or ID..." 
              className="pl-8 bg-background" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" className="bg-background">
            <Filter className="mr-2 h-4 w-4" /> Filter
          </Button>
        </div>
        
        {selectedTickets.size > 0 && (
          <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-4 duration-300">
            <Badge variant="secondary" className="px-3 py-1 text-sm font-medium">
              {selectedTickets.size} selected
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger render={<Button variant="outline" className="bg-background">Bulk Actions</Button>} />
              <DropdownMenuContent align="end">
                <DropdownMenuItem>
                  <UserPlus className="mr-2 h-4 w-4" /> Assign to me
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <CheckCircle className="mr-2 h-4 w-4 text-emerald-600" /> Mark Resolved
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-destructive">
                  <Trash className="mr-2 h-4 w-4" /> Delete selected
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>

      <div className="rounded-xl border bg-background shadow-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead className="w-[40px] px-4">
                <Checkbox 
                  checked={tickets && tickets.length > 0 && selectedTickets.size === tickets.length}
                  onCheckedChange={toggleSelectAll}
                  aria-label="Select all"
                />
              </TableHead>
              <TableHead className="w-[100px]">Ticket ID</TableHead>
              <TableHead className="w-[300px]">Subject</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>SLA</TableHead>
              <TableHead>Assigned To</TableHead>
              <TableHead>Updated</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array(5).fill(0).map((_, i) => (
                <TableRow key={i}>
                  <TableCell className="px-4"><Skeleton className="h-4 w-4 rounded" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-48 mb-1" /><Skeleton className="h-3 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20 rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-16 rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-24 rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-8 w-8 rounded-full ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : !filteredTickets || filteredTickets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <CheckSquare className="h-10 w-10 mb-4 opacity-20" />
                    <p className="font-medium text-foreground">No tickets found</p>
                    <p className="text-sm">We couldn't find any tickets matching your criteria.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filteredTickets.map((ticket) => (
                <TableRow key={ticket.id} className={selectedTickets.has(ticket.id) ? "bg-muted/30" : ""}>
                  <TableCell className="px-4">
                    <Checkbox 
                      checked={selectedTickets.has(ticket.id)}
                      onCheckedChange={() => toggleSelect(ticket.id)}
                      aria-label={`Select ticket ${ticket.id}`}
                    />
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    <Link href={`/dashboard/tickets/${ticket.id}`} className="hover:underline text-primary">
                      #{ticket.id.split('-')[0]}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Link href={`/dashboard/tickets/${ticket.id}`} className="block">
                      <div className="font-semibold text-sm hover:underline">{ticket.title}</div>
                      <div className="text-xs text-muted-foreground mt-1 truncate max-w-[250px]">
                        {ticket.customer_id ? `Customer ID: ${ticket.customer_id.split('-')[0]}` : 'System Generated'}
                      </div>
                    </Link>
                  </TableCell>
                  <TableCell>{getStatusBadge(ticket.status)}</TableCell>
                  <TableCell>{getPriorityBadge(ticket.priority)}</TableCell>
                  <TableCell>
                    {ticket.status !== "RESOLVED" && ticket.status !== "CLOSED" ? (
                      <div className="flex items-center gap-1.5 text-xs text-amber-600 font-medium">
                        <Clock className="h-3 w-3" /> 2h left
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Avatar className="h-6 w-6">
                        <AvatarFallback className="text-[10px] bg-primary/10 text-primary">
                          {ticket.assigned_to ? ticket.assigned_to[0].toUpperCase() : '?'}
                        </AvatarFallback>
                      </Avatar>
                      <span className={!ticket.assigned_to ? "text-muted-foreground text-sm italic" : "text-sm"}>
                        {ticket.assigned_to ? "Agent" : "Unassigned"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {new Date(ticket.updated_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger render={
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      } />
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem render={<Link href={`/dashboard/tickets/${ticket.id}`}>View Details</Link>} />
                        <DropdownMenuItem>Assign to me</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <CreateTicketDialog open={isCreateOpen} onOpenChange={setIsCreateOpen} />
    </div>
  );
}
