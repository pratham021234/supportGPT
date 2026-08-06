import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Filter, MoreVertical, Send, Bot, User, Phone, Mail, Clock, Library } from "lucide-react";

export default function ConversationsPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Conversations</h1>
          <p className="text-muted-foreground">
            Monitor and intervene in active AI support conversations.
          </p>
        </div>
      </div>

      <Card className="flex flex-1 overflow-hidden min-h-0 border">
        {/* Sidebar List */}
        <div className="w-1/3 border-r flex flex-col bg-muted/20">
          <div className="p-4 border-b space-y-4 shrink-0">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search messages..." className="pl-8 bg-background" />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-2 text-sm">
              <Badge variant="secondary" className="bg-primary/10 text-primary hover:bg-primary/20">Active (12)</Badge>
              <Badge variant="outline">Escalated (3)</Badge>
              <Badge variant="outline">Resolved (342)</Badge>
            </div>
          </div>
          
          <ScrollArea className="flex-1">
            <div className="flex flex-col">
              {[
                { name: "John Smith", id: "#1024", query: "How do I reset my password?", status: "Active", ai: true, time: "2m" },
                { name: "Sarah Lee", id: "#1023", query: "Billing issue with latest invoice", status: "Escalated", ai: false, time: "15m" },
                { name: "Unknown User", id: "#1022", query: "API rate limits", status: "Active", ai: true, time: "1h" },
              ].map((conv, i) => (
                <div key={i} className={`p-4 border-b cursor-pointer transition-colors hover:bg-muted/50 ${i === 0 ? "bg-muted" : ""}`}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">{conv.name}</span>
                      <span className="text-xs text-muted-foreground">{conv.id}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">{conv.time}</span>
                  </div>
                  <p className="text-sm text-muted-foreground truncate mb-2">{conv.query}</p>
                  <div className="flex items-center gap-2">
                    {conv.status === "Escalated" ? (
                      <Badge variant="destructive" className="h-5 text-[10px]">Escalated</Badge>
                    ) : (
                      <Badge variant="outline" className="h-5 text-[10px] text-emerald-500 border-emerald-500/30">Active</Badge>
                    )}
                    {conv.ai && (
                      <div className="flex items-center gap-1 text-[10px] text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">
                        <Bot className="h-3 w-3" /> AI Handling
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="h-16 border-b flex items-center justify-between px-6 bg-background shrink-0">
            <div className="flex items-center gap-4">
              <Avatar className="h-10 w-10">
                <AvatarFallback>JS</AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold text-sm">John Smith <span className="text-muted-foreground font-normal">#1024</span></h3>
                <div className="flex items-center gap-2 text-xs text-emerald-500">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  AI is typing...
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="text-destructive border-destructive/30 hover:bg-destructive/10 hover:text-destructive">
                Take Over
              </Button>
              <Button variant="ghost" size="icon">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <ScrollArea className="flex-1 p-6">
            <div className="space-y-6">
              <div className="flex justify-center">
                <Badge variant="outline" className="text-xs font-normal text-muted-foreground">Today at 10:42 AM</Badge>
              </div>
              
              <div className="flex items-start gap-3">
                <Avatar className="h-8 w-8 mt-1">
                  <AvatarFallback>JS</AvatarFallback>
                </Avatar>
                <div className="grid gap-1">
                  <div className="font-semibold text-sm flex items-center gap-2">
                    John Smith <span className="text-xs text-muted-foreground font-normal">10:42 AM</span>
                  </div>
                  <div className="bg-muted px-4 py-3 rounded-2xl rounded-tl-sm text-sm">
                    Hi, I'm trying to log in but I forgot my password. The reset link isn't arriving in my email.
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 flex-row-reverse">
                <Avatar className="h-8 w-8 mt-1 bg-primary/10">
                  <AvatarFallback className="bg-transparent text-primary"><Bot className="h-5 w-5" /></AvatarFallback>
                </Avatar>
                <div className="grid gap-1 text-right">
                  <div className="font-semibold text-sm flex items-center gap-2 justify-end">
                    <span className="text-xs text-muted-foreground font-normal">10:43 AM</span> Support Agent
                  </div>
                  <div className="bg-primary text-primary-foreground px-4 py-3 rounded-2xl rounded-tr-sm text-sm text-left">
                    I can help with that! Sometimes password reset emails can take a few minutes or end up in your spam folder. 
                    <br/><br/>
                    Have you checked your spam or promotions folder? If it's not there, I can check if there are any issues with email delivery for your account.
                  </div>
                  <div className="text-xs text-muted-foreground mt-1 flex justify-end gap-2">
                    <span>Confidence: 95%</span>
                    <span>•</span>
                    <a href="#" className="hover:underline flex items-center gap-1"><Library className="h-3 w-3" /> Login Troubleshooting FAQ</a>
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <Avatar className="h-8 w-8 mt-1">
                  <AvatarFallback>JS</AvatarFallback>
                </Avatar>
                <div className="grid gap-1">
                  <div className="font-semibold text-sm flex items-center gap-2">
                    John Smith <span className="text-xs text-muted-foreground font-normal">10:45 AM</span>
                  </div>
                  <div className="bg-muted px-4 py-3 rounded-2xl rounded-tl-sm text-sm">
                    Yes I checked spam. Still nothing.
                  </div>
                </div>
              </div>
            </div>
          </ScrollArea>

          <div className="p-4 border-t bg-background shrink-0">
            <div className="flex gap-2 items-center text-sm text-muted-foreground mb-2 px-2">
              <Bot className="h-4 w-4" /> AI is currently handling this conversation. You can take over at any time.
            </div>
            <div className="relative">
              <Input placeholder="Type an internal note or take over the chat..." className="pr-20 py-6" disabled />
              <Button size="sm" className="absolute right-2 top-2 h-8" disabled>
                Send <Send className="ml-2 h-3 w-3" />
              </Button>
            </div>
          </div>
        </div>

        {/* Customer Profile Panel */}
        <div className="w-1/4 border-l bg-background hidden lg:flex flex-col">
          <div className="p-6 border-b text-center">
            <Avatar className="h-20 w-20 mx-auto mb-4">
              <AvatarFallback className="text-2xl">JS</AvatarFallback>
            </Avatar>
            <h3 className="font-bold text-lg">John Smith</h3>
            <p className="text-muted-foreground text-sm">Premium User</p>
          </div>
          <ScrollArea className="flex-1 p-6">
            <div className="space-y-6">
              <div>
                <h4 className="font-semibold text-sm mb-3">Contact Details</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3 text-muted-foreground">
                    <Mail className="h-4 w-4" /> john@example.com
                  </div>
                  <div className="flex items-center gap-3 text-muted-foreground">
                    <Phone className="h-4 w-4" /> +1 (555) 123-4567
                  </div>
                  <div className="flex items-center gap-3 text-muted-foreground">
                    <Clock className="h-4 w-4" /> 10:45 AM (Local time)
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-sm mb-3">Recent Activity</h4>
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                    <div>
                      <p className="text-sm font-medium">Viewed Pricing Page</p>
                      <p className="text-xs text-muted-foreground">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="mt-1 h-2 w-2 rounded-full bg-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Ticket #0984 Resolved</p>
                      <p className="text-xs text-muted-foreground">3 days ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </ScrollArea>
        </div>
      </Card>
    </div>
  );
}
