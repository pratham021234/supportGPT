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
import { Search, Filter, MoreHorizontal, ArrowUpDown } from "lucide-react";

const tickets = [
  { id: "T-1024", subject: "Password reset not working", customer: "John Smith", status: "Open", priority: "High", assignedTo: "Sarah Agent", created: "10 mins ago" },
  { id: "T-1023", subject: "Billing issue with latest invoice", customer: "Sarah Lee", status: "In Progress", priority: "Medium", assignedTo: "Unassigned", created: "2 hours ago" },
  { id: "T-1022", subject: "API rate limits reached", customer: "DevCorp Inc.", status: "Resolved", priority: "Low", assignedTo: "Mike Technical", created: "1 day ago" },
  { id: "T-1021", subject: "How to invite team members", customer: "Alice Johnson", status: "Resolved", priority: "Low", assignedTo: "AI Agent", created: "2 days ago" },
];

const getPriorityBadge = (priority: string) => {
  switch (priority) {
    case "High":
      return <Badge variant="destructive" className="bg-destructive/10 text-destructive hover:bg-destructive/20">{priority}</Badge>;
    case "Medium":
      return <Badge variant="default" className="bg-amber-500/10 text-amber-500 hover:bg-amber-500/20">{priority}</Badge>;
    case "Low":
      return <Badge variant="secondary" className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20">{priority}</Badge>;
    default:
      return <Badge variant="outline">{priority}</Badge>;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "Open":
      return <Badge variant="outline" className="border-destructive/30 text-destructive">Open</Badge>;
    case "In Progress":
      return <Badge variant="outline" className="border-amber-500/30 text-amber-500">In Progress</Badge>;
    case "Resolved":
      return <Badge variant="outline" className="border-emerald-500/30 text-emerald-500">Resolved</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

export default function TicketsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tickets</h1>
          <p className="text-muted-foreground">
            Manage escalated support tickets that require human intervention.
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search tickets..." className="pl-8 bg-background" />
        </div>
        <Button variant="outline" className="bg-background">Filter</Button>
      </div>

      <div className="rounded-md border bg-background shadow-sm">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">ID</TableHead>
              <TableHead className="w-[300px]">Subject</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Assigned To</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tickets.map((ticket) => (
              <TableRow key={ticket.id}>
                <TableCell className="font-mono text-xs">{ticket.id}</TableCell>
                <TableCell className="font-medium">{ticket.subject}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="text-[10px]">{ticket.customer[0]}</AvatarFallback>
                    </Avatar>
                    <span className="text-sm">{ticket.customer}</span>
                  </div>
                </TableCell>
                <TableCell>{getStatusBadge(ticket.status)}</TableCell>
                <TableCell>{getPriorityBadge(ticket.priority)}</TableCell>
                <TableCell>
                  <span className={ticket.assignedTo === "Unassigned" ? "text-muted-foreground text-sm italic" : "text-sm"}>
                    {ticket.assignedTo}
                  </span>
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">{ticket.created}</TableCell>
                <TableCell>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
