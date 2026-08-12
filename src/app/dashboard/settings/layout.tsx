"use client";

import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { 
  Settings, 
  Blocks, 
  Bell, 
  Key, 
  Webhook, 
  BrainCircuit, 
  Activity, 
  BarChart3 
} from "lucide-react";
import { cn } from "@/lib/utils";

const sidebarItems = [
  { name: "General & Branding", href: "/dashboard/settings", icon: Settings },
  { name: "Integrations", href: "/dashboard/settings/integrations", icon: Blocks },
  { name: "Notifications", href: "/dashboard/settings/notifications", icon: Bell },
  { name: "API Keys", href: "/dashboard/settings/api-keys", icon: Key },
  { name: "Webhooks", href: "/dashboard/settings/webhooks", icon: Webhook },
  { name: "AI Providers", href: "/dashboard/settings/ai-providers", icon: BrainCircuit },
  { name: "System Status", href: "/dashboard/settings/system-status", icon: Activity },
  { name: "Usage Analytics", href: "/dashboard/settings/usage", icon: BarChart3 },
];

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="flex flex-col md:flex-row gap-8 h-full min-h-[calc(100vh-8rem)]">
      <aside className="w-full md:w-64 shrink-0 flex flex-col gap-1">
        <h2 className="text-xl font-bold tracking-tight mb-4 px-2">Settings</h2>
        <nav className="flex flex-col gap-1">
          {sidebarItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Button
                key={item.href}
                variant={isActive ? "secondary" : "ghost"}
                className={cn("justify-start", isActive ? "font-medium" : "font-normal text-muted-foreground")}
                onClick={() => router.push(item.href)}
              >
                <item.icon className="w-4 h-4 mr-3" />
                {item.name}
              </Button>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 overflow-y-auto pb-10 min-w-0">
        {children}
      </main>
    </div>
  );
}
