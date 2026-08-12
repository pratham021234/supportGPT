import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MessageSquareCode, Search, Menu } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Docs Header */}
      <header className="px-6 h-16 flex items-center justify-between border-b bg-background sticky top-0 z-50">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2 text-primary font-bold">
            <MessageSquareCode className="h-5 w-5" />
            <span>SupportGPT</span>
          </Link>
          <div className="h-4 w-px bg-border hidden sm:block"></div>
          <span className="font-semibold hidden sm:block">Documentation</span>
        </div>
        <div className="flex items-center gap-4 flex-1 justify-end max-w-sm">
          <div className="relative w-full hidden md:block">
             <Search className="absolute left-2.5 top-2 h-4 w-4 text-muted-foreground" />
             <Input type="search" placeholder="Search documentation... (Ctrl+K)" className="w-full bg-muted/50 pl-9 h-9 text-sm" />
          </div>
          <Link href="/login" className="hidden sm:block">
            <Button variant="outline" size="sm">Dashboard</Button>
          </Link>
        </div>
      </header>

      <div className="flex flex-1 container mx-auto">
        {/* Sidebar */}
        <aside className="w-64 shrink-0 border-r py-8 pr-6 hidden md:block overflow-y-auto sticky top-16 h-[calc(100vh-4rem)]">
          <nav className="space-y-8 text-sm">
             <div>
                <h4 className="font-semibold mb-3 px-2">Overview</h4>
                <ul className="space-y-1">
                   <li><Link href="/docs" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Introduction</Link></li>
                   <li><Link href="/docs/getting-started" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Getting Started</Link></li>
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Architecture</Link></li>
                </ul>
             </div>
             <div>
                <h4 className="font-semibold mb-3 px-2">Core Concepts</h4>
                <ul className="space-y-1">
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Knowledge Base</Link></li>
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">AI Agents</Link></li>
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Conversations & Tickets</Link></li>
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Prompt Studio</Link></li>
                </ul>
             </div>
             <div>
                <h4 className="font-semibold mb-3 px-2">Developers</h4>
                <ul className="space-y-1">
                   <li><Link href="/docs/api" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">API Reference</Link></li>
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Webhooks</Link></li>
                   <li><Link href="#" className="block px-2 py-1.5 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground">Widget SDK</Link></li>
                </ul>
             </div>
          </nav>
        </aside>

        {/* Content */}
        <main className="flex-1 min-w-0 py-8 px-4 md:px-10 overflow-y-auto">
          <div className="prose prose-zinc max-w-3xl dark:prose-invert">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
