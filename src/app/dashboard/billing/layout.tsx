"use client";

import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { 
  CreditCard, 
  Wallet, 
  Receipt, 
  Activity, 
  Users, 
  History, 
  BarChart, 
  Building2 
} from "lucide-react";
import { cn } from "@/lib/utils";

const sidebarItems = [
  { name: "Overview", href: "/dashboard/billing", icon: Wallet },
  { name: "Plans & Upgrades", href: "/dashboard/billing/plans", icon: CreditCard },
  { name: "Payment Methods", href: "/dashboard/billing/payment-methods", icon: Wallet },
  { name: "Invoices", href: "/dashboard/billing/invoices", icon: Receipt },
  { name: "Usage & Limits", href: "/dashboard/billing/usage", icon: Activity },
  { name: "Seat Management", href: "/dashboard/billing/seats", icon: Users },
  { name: "Billing History", href: "/dashboard/billing/history", icon: History },
  { name: "Analytics", href: "/dashboard/billing/analytics", icon: BarChart },
  { name: "Tax Info", href: "/dashboard/billing/tax", icon: Building2 },
];

export default function BillingLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="flex flex-col md:flex-row gap-8 h-full min-h-[calc(100vh-8rem)]">
      <aside className="w-full md:w-64 shrink-0 flex flex-col gap-1">
        <h2 className="text-xl font-bold tracking-tight mb-4 px-2">Billing</h2>
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
