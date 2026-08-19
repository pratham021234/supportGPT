"use client";

import { Bell, Menu, Search, Sun, Moon, CheckCheck } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useWebSocket } from "@/lib/websocket/use-websocket";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";

type PresenceStatus = "ONLINE" | "BUSY" | "AWAY" | "OFFLINE";

export function TopNav() {
  const { setTheme } = useTheme();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isConnected, messages } = useWebSocket('/notifications');
  const [presence, setPresence] = useState<PresenceStatus>("ONLINE");

  const updatePresenceMutation = useMutation({
    mutationFn: async (status: PresenceStatus) => {
      const res = await fetch("/api/v1/handoff/agents/status", {
        method: "POST",
        headers: { 
          "Authorization": `Bearer ${user?.token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ status })
      });
      if (!res.ok) throw new Error("Failed to update status");
      return status;
    },
    onSuccess: (status) => {
      setPresence(status);
    }
  });

  // Fetch unread notifications
  const { data: unreadData } = useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: async () => {
      if (!user) return [];
      const res = await fetch("/api/v1/notifications/unread", {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      return res.ok ? res.json() : [];
    },
    enabled: !!user,
  });

  const markReadMutation = useMutation({
    mutationFn: async (id: string) => {
      await fetch(`/api/v1/notifications/${id}/read`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${user?.token}` },
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] }),
  });

  const markAllReadMutation = useMutation({
    mutationFn: async () => {
      await fetch(`/api/v1/notifications/read-all`, {
        method: "POST",
        headers: { Authorization: `Bearer ${user?.token}` },
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] }),
  });

  useEffect(() => {
    if (messages.length > 0) {
      // Invalidate on new websocket event to fetch real notification from DB
      queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    }
  }, [messages, queryClient]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const notifications = Array.isArray(unreadData) ? unreadData : [];
  const unreadCount = notifications.length;

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="shrink-0 md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="flex flex-col">
          <nav className="grid gap-2 text-lg font-medium">
            <div className="flex items-center gap-2 text-lg font-semibold mb-4">
              <span>SupportGPT</span>
            </div>
          </nav>
        </SheetContent>
      </Sheet>
      <div className="w-full flex-1">
        <form>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search conversations, tickets, or documents..."
              className="w-full appearance-none bg-background pl-8 shadow-none md:w-2/3 lg:w-1/3"
            />
          </div>
        </form>
      </div>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="icon" className="rounded-full">
            <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setTheme("light")}>
            Light
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("dark")}>
            Dark
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("system")}>
            System
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="icon" className="rounded-full relative">
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <Badge variant="destructive" className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center text-[10px]">
                {unreadCount}
              </Badge>
            )}
            <span className="sr-only">Toggle notifications</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-80">
          <div className="flex items-center justify-between p-2">
            <DropdownMenuLabel className="p-0">Notifications {isConnected ? <span className="text-emerald-500 text-xs ml-1 font-normal">(Live)</span> : <span className="text-rose-500 text-xs ml-1 font-normal">(Offline)</span>}</DropdownMenuLabel>
            {unreadCount > 0 && (
                <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => markAllReadMutation.mutate()}>
                    <CheckCheck className="w-3 h-3 mr-1"/> Mark all
                </Button>
            )}
          </div>
          <DropdownMenuSeparator />
          {unreadCount === 0 ? (
            <div className="p-6 text-center text-sm text-muted-foreground">You're all caught up!</div>
          ) : (
            <div className="max-h-[300px] overflow-y-auto flex flex-col">
              {notifications.map((n: any) => (
                <div key={n.id} className="flex flex-col items-start gap-1 p-3 border-b hover:bg-muted/50 cursor-pointer" onClick={() => markReadMutation.mutate(n.id)}>
                  <div className="flex justify-between w-full items-center">
                      <span className={`font-semibold text-xs ${n.priority === 'CRITICAL' || n.priority === 'HIGH' ? 'text-rose-600' : ''}`}>{n.title}</span>
                      <span className="text-[10px] text-muted-foreground">{new Date(n.created_at).toLocaleTimeString()}</span>
                  </div>
                  <span className="text-xs text-muted-foreground line-clamp-2">{n.message}</span>
                </div>
              ))}
            </div>
          )}
          <DropdownMenuSeparator />
          <DropdownMenuItem className="justify-center text-xs" onClick={() => router.push("/dashboard/settings/notifications")}>
              View Preferences
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="secondary" size="icon" className="rounded-full">
            <Avatar className="h-9 w-9">
              <AvatarImage src="/avatars/01.png" alt="@avatar" />
              <AvatarFallback>{user?.name?.[0] || "U"}</AvatarFallback>
            </Avatar>
            <span className="sr-only">Toggle user menu</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>My Account</DropdownMenuLabel>
          <div className="px-2 py-1.5 flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">Status:</span>
            <select 
              className="text-xs border rounded p-1"
              value={presence}
              onChange={(e) => updatePresenceMutation.mutate(e.target.value as PresenceStatus)}
            >
              <option value="ONLINE">🟢 Online</option>
              <option value="BUSY">🔴 Busy</option>
              <option value="AWAY">🟡 Away</option>
              <option value="OFFLINE">⚫ Offline</option>
            </select>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => router.push("/dashboard/settings")}>Settings</DropdownMenuItem>
          <DropdownMenuItem>Support</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
