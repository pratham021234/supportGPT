"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { TimeRange } from "@/lib/api/analytics";

const tabs = [
  { name: "Overview", path: "/dashboard/analytics" },
  { name: "AI Performance", path: "/dashboard/analytics/ai-performance" },
  { name: "Knowledge", path: "/dashboard/analytics/knowledge" },
  { name: "Agents", path: "/dashboard/analytics/agents" },
  { name: "Tickets", path: "/dashboard/analytics/tickets" },
  { name: "Widget", path: "/dashboard/analytics/widget" },
  { name: "Reports", path: "/dashboard/analytics/reports" }
];

export default function AnalyticsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const currentRange = (searchParams.get("range") as TimeRange) || "7d";

  const handleRangeChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("range", value);
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="flex flex-col gap-6 max-w-[1400px] mx-auto w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics & Business Intelligence</h1>
          <p className="text-muted-foreground mt-1">
            Data-driven insights to monitor and optimize your support operations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground font-medium">Date Range:</span>
          <Select value={currentRange} onValueChange={handleRangeChange}>
            <SelectTrigger className="w-[140px] h-9">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <nav className="flex items-center gap-1 border-b pb-0 overflow-x-auto no-scrollbar">
        {tabs.map((tab) => {
          const isActive = pathname === tab.path;
          return (
            <Link
              key={tab.path}
              href={`${tab.path}?range=${currentRange}`}
              className={cn(
                "px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
                isActive 
                  ? "border-primary text-primary" 
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/30"
              )}
            >
              {tab.name}
            </Link>
          );
        })}
      </nav>

      <div className="pt-2">
        {children}
      </div>
    </div>
  );
}
