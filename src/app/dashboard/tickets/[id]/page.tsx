"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useTicket, useTicketComments, useAddTicketComment, useUpdateTicketStatus, TicketStatus, TicketPriority } from "@/lib/api/tickets";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Clock, MessageSquare, Lock, Send, User, AlertCircle, FileText, Activity, CheckCircle } from "lucide-react";
import { getPriorityBadge, getStatusBadge } from "../page";

export default function TicketDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const ticketId = params.id as string;
  
  const [commentText, setCommentText] = useState("");
  const [isInternal, setIsInternal] = useState(false);

  const { data: ticketData, isLoading: isLoadingTicket } = useTicket(ticketId);
  const { data: comments, isLoading: isLoadingComments } = useTicketComments(ticketId);
  
  const { mutate: addComment, isPending: isAddingComment } = useAddTicketComment(ticketId);
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateTicketStatus(ticketId);

  if (isLoadingTicket) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full h-full">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <div className="flex flex-1 gap-6 min-h-0">
          <Skeleton className="w-[300px] h-full rounded-xl" />
          <Skeleton className="flex-1 h-full rounded-xl" />
          <Skeleton className="w-[300px] h-full rounded-xl hidden xl:block" />
        </div>
      </div>
    );
  }

  if (!ticketData || !ticketData.ticket) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] text-center">
        <AlertCircle className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
        <h2 className="text-xl font-semibold mb-2">Ticket Not Found</h2>
        <p className="text-muted-foreground mb-6">The ticket you are looking for does not exist or has been deleted.</p>
        <Button onClick={() => router.push("/dashboard/tickets")}>Back to Tickets</Button>
      </div>
    );
  }

  const { ticket, sla } = ticketData;

  const handleSendComment = () => {
    if (!commentText.trim()) return;
    addComment({ content: commentText, is_internal: isInternal }, {
      onSuccess: () => setCommentText("")
    });
  };

  return (
    <div className="flex flex-col gap-4 h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard/tickets")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight">{ticket.title}</h1>
              {getStatusBadge(ticket.status)}
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              #{ticket.id.split('-')[0]} • Created {new Date(ticket.created_at).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {ticket.status !== "RESOLVED" && ticket.status !== "CLOSED" && (
            <Button variant="outline" onClick={() => updateStatus("RESOLVED")} disabled={isUpdatingStatus} className="text-emerald-600 border-emerald-200 bg-emerald-50 hover:bg-emerald-100">
              Mark as Resolved
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-1 gap-4 overflow-hidden min-h-0">
        {/* Left Panel: Details & Customer */}
        <div className="w-[300px] border rounded-xl bg-background flex flex-col overflow-y-auto shrink-0 shadow-sm">
          <div className="p-5 border-b">
            <h3 className="font-semibold text-sm mb-4 text-muted-foreground uppercase tracking-wider">Ticket Details</h3>
            
            <div className="space-y-4">
              <div className="grid gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">Status</label>
                <Select value={ticket.status} onValueChange={(v) => updateStatus(v as TicketStatus)} disabled={isUpdatingStatus}>
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="OPEN">Open</SelectItem>
                    <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                    <SelectItem value="WAITING_CUSTOMER">Waiting on Customer</SelectItem>
                    <SelectItem value="WAITING_INTERNAL">Waiting Internal</SelectItem>
                    <SelectItem value="RESOLVED">Resolved</SelectItem>
                    <SelectItem value="CLOSED">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">Priority</label>
                <div className="h-8 flex items-center">{getPriorityBadge(ticket.priority)}</div>
              </div>
              
              <div className="grid gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">Category</label>
                <div className="text-sm capitalize">{ticket.category || "General"}</div>
              </div>

              <div className="grid gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">Assignee</label>
                <div className="flex items-center gap-2 text-sm">
                  <Avatar className="h-5 w-5">
                    <AvatarFallback className="text-[9px]">{ticket.assigned_to ? "A" : "?"}</AvatarFallback>
                  </Avatar>
                  {ticket.assigned_to ? "Agent" : "Unassigned"}
                </div>
              </div>
            </div>
          </div>

          <div className="p-5 border-b">
            <h3 className="font-semibold text-sm mb-4 text-muted-foreground uppercase tracking-wider">SLA Status</h3>
            {sla ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Resolution</span>
                  <Badge variant={sla.is_breached ? "destructive" : "outline"} className={!sla.is_breached ? "text-emerald-600 border-emerald-300" : ""}>
                    {sla.time_remaining_minutes} min left
                  </Badge>
                </div>
                <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${sla.is_breached ? 'bg-destructive' : 'bg-emerald-500'}`} style={{ width: '60%' }}></div>
                </div>
              </div>
            ) : (
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <Clock className="h-4 w-4" /> No SLA configured
              </div>
            )}
          </div>

          <div className="p-5">
            <h3 className="font-semibold text-sm mb-4 text-muted-foreground uppercase tracking-wider">Customer Info</h3>
            <div className="flex items-center gap-3 mb-4">
              <Avatar className="h-10 w-10">
                <AvatarFallback><User className="h-5 w-5 text-muted-foreground" /></AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium text-sm">{ticket.customer_id ? `Customer ${ticket.customer_id.split('-')[0]}` : "Unknown"}</p>
                <p className="text-xs text-muted-foreground">Via {ticket.source}</p>
              </div>
            </div>
            
            {ticket.conversation_id && (
              <Button variant="outline" className="w-full text-xs h-8" onClick={() => router.push(`/dashboard/conversations?id=${ticket.conversation_id}`)}>
                View Linked Chat
              </Button>
            )}
          </div>
        </div>

        {/* Center Panel: Conversation & Activity */}
        <div className="flex-1 border rounded-xl bg-background flex flex-col overflow-hidden shadow-sm">
          <div className="p-5 border-b bg-muted/10 shrink-0">
            <h2 className="font-semibold">{ticket.title}</h2>
            {ticket.description && (
              <p className="text-sm text-muted-foreground mt-2 whitespace-pre-wrap">{ticket.description}</p>
            )}
          </div>
          
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {isLoadingComments ? (
              <div className="space-y-4">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
            ) : comments?.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <MessageSquare className="h-10 w-10 mb-2 opacity-20" />
                <p>No comments yet.</p>
              </div>
            ) : (
              comments?.map((comment) => (
                <div key={comment.id} className={`flex gap-4 ${comment.is_internal ? 'opacity-90' : ''}`}>
                  <Avatar className="h-8 w-8 mt-1 shrink-0">
                    <AvatarFallback className={comment.is_internal ? 'bg-amber-100 text-amber-700' : ''}>
                      {comment.is_internal ? <Lock className="h-4 w-4" /> : 'A'}
                    </AvatarFallback>
                  </Avatar>
                  <div className={`flex-1 rounded-xl p-4 text-sm ${comment.is_internal ? 'bg-amber-50/50 border border-amber-200' : 'bg-muted/50 border border-transparent'}`}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold">{comment.author_id ? "Agent" : "Customer"}</span>
                      <span className="text-xs text-muted-foreground">{new Date(comment.created_at).toLocaleString()}</span>
                    </div>
                    {comment.is_internal && (
                      <Badge variant="outline" className="mb-2 bg-amber-100/50 text-amber-800 border-amber-200 text-[10px]">Internal Note</Badge>
                    )}
                    <p className="whitespace-pre-wrap leading-relaxed">{comment.content}</p>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div className="p-4 border-t bg-muted/10 shrink-0">
            <Tabs defaultValue="reply" className="w-full" onValueChange={(v) => setIsInternal(v === 'internal')}>
              <TabsList className="mb-2 w-full justify-start h-9 bg-background border">
                <TabsTrigger value="reply" className="text-xs">Public Reply</TabsTrigger>
                <TabsTrigger value="internal" className="text-xs data-[state=active]:bg-amber-100 data-[state=active]:text-amber-800">Internal Note</TabsTrigger>
              </TabsList>
              
              <TabsContent value="reply" className="mt-0">
                <div className="relative">
                  <Textarea 
                    placeholder="Type your reply to the customer..."
                    className="min-h-[100px] resize-none pr-12 focus-visible:ring-primary"
                    value={isInternal ? "" : commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                  />
                  <Button 
                    size="icon" 
                    className="absolute bottom-3 right-3 h-8 w-8"
                    onClick={handleSendComment}
                    disabled={isAddingComment || !commentText.trim() || isInternal}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="internal" className="mt-0">
                <div className="relative">
                  <Textarea 
                    placeholder="Type an internal note (visible only to agents)..."
                    className="min-h-[100px] resize-none pr-12 bg-amber-50/30 border-amber-200 focus-visible:ring-amber-500"
                    value={!isInternal ? "" : commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                  />
                  <Button 
                    size="icon" 
                    className="absolute bottom-3 right-3 h-8 w-8 bg-amber-600 hover:bg-amber-700"
                    onClick={handleSendComment}
                    disabled={isAddingComment || !commentText.trim() || !isInternal}
                  >
                    <Lock className="h-4 w-4" />
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Right Panel: Context & Timeline */}
        <div className="w-[280px] border rounded-xl bg-background hidden xl:flex flex-col overflow-y-auto shrink-0 shadow-sm">
          <div className="p-5 border-b">
            <h3 className="font-semibold text-sm mb-4 text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Activity className="h-4 w-4" /> Timeline
            </h3>
            
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-muted before:to-transparent">
              <div className="relative flex items-center group">
                <div className="flex items-center justify-center w-6 h-6 rounded-full border border-background bg-primary text-primary-foreground shrink-0 shadow z-10">
                  <FileText className="h-3 w-3" />
                </div>
                <div className="ml-3 p-3 rounded border bg-background shadow-sm w-full">
                  <div className="font-medium text-xs mb-1">Ticket Created</div>
                  <div className="text-[10px] text-muted-foreground">{new Date(ticket.created_at).toLocaleString()}</div>
                </div>
              </div>
              
              {ticket.resolved_at && (
                <div className="relative flex items-center group">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full border border-background bg-emerald-500 text-emerald-50 shrink-0 shadow z-10">
                    <CheckCircle className="h-3 w-3" />
                  </div>
                  <div className="ml-3 p-3 rounded border bg-background shadow-sm w-full">
                    <div className="font-medium text-xs mb-1">Ticket Resolved</div>
                    <div className="text-[10px] text-muted-foreground">{new Date(ticket.resolved_at).toLocaleString()}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
