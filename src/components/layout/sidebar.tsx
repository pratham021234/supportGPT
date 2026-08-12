"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Library, 
  Files, 
  Bot, 
  MessageSquare, 
  Ticket, 
  BarChart3, 
  Sparkles, 
  Users, 
  Settings,
  MessageSquareCode
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Knowledge Base", href: "/dashboard/knowledge-base", icon: Library },
  { name: "Documents", href: "/dashboard/documents", icon: Files },
  { name: "Agents", href: "/dashboard/agents", icon: Bot },
  { name: "Conversations", href: "/dashboard/conversations", icon: MessageSquare },
  { name: "Tickets", href: "/dashboard/tickets", icon: Ticket },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { name: "Prompt Studio", href: "/dashboard/prompt-studio", icon: Sparkles },
];

const bottomNavItems = [
  { name: "Team", href: "/dashboard/team", icon: Users },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

import { WorkspaceSwitcher } from "./workspace-switcher";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden border-r bg-muted/40 md:flex md:w-64 md:flex-col">
      <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <MessageSquareCode className="h-6 w-6 text-primary" />
          <span>SupportGPT</span>
        </Link>
      </div>
      <div className="flex-1 overflow-auto py-2">
        <WorkspaceSwitcher />
        <nav className="grid items-start px-2 text-sm font-medium lg:px-4 gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
                  isActive ? "bg-muted text-primary" : ""
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="mt-auto p-4">
        <nav className="grid items-start gap-1 text-sm font-medium">
          {bottomNavItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
                  isActive ? "bg-muted text-primary" : ""
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
