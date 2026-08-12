import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MessageSquareCode } from "lucide-react";

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Navigation */}
      <header className="px-6 lg:px-14 h-20 flex items-center justify-between border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-2 text-primary font-bold text-xl">
          <MessageSquareCode className="h-6 w-6" />
          <span>SupportGPT</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link href="/features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="/use-cases" className="hover:text-primary transition-colors">Use Cases</Link>
          <Link href="/pricing" className="hover:text-primary transition-colors">Pricing</Link>
          <Link href="/customers" className="hover:text-primary transition-colors">Customers</Link>
          <Link href="/docs" className="hover:text-primary transition-colors">Docs</Link>
          <Link href="/blog" className="hover:text-primary transition-colors">Blog</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-primary transition-colors hidden sm:block">
            Sign in
          </Link>
          <Link href="/contact-sales" className="hidden lg:block">
            <Button variant="outline">Contact Sales</Button>
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t py-16 bg-zinc-950 text-zinc-400">
        <div className="container px-4 md:px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 mb-12">
            <div className="col-span-2 lg:col-span-2">
              <Link href="/" className="flex items-center gap-2 text-white font-bold text-xl mb-4">
                <MessageSquareCode className="h-6 w-6 text-primary" />
                <span>SupportGPT</span>
              </Link>
              <p className="max-w-xs mb-6 text-sm">
                The enterprise-grade AI customer support platform. Automate 80% of your tickets with knowledge-driven agents.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Product</h3>
              <ul className="space-y-3 text-sm">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/customers" className="hover:text-white transition-colors">Customers</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Resources</h3>
              <ul className="space-y-3 text-sm">
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="/docs/api" className="hover:text-white transition-colors">API Reference</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Company</h3>
              <ul className="space-y-3 text-sm">
                <li><Link href="/contact-sales" className="hover:text-white transition-colors">Contact Sales</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-zinc-800 flex flex-col md:flex-row justify-between items-center gap-4 text-sm">
            <p>© 2026 SupportGPT Inc. All rights reserved.</p>
            <div className="flex gap-6">
              <Link href="#" className="hover:text-white">Twitter</Link>
              <Link href="#" className="hover:text-white">GitHub</Link>
              <Link href="#" className="hover:text-white">LinkedIn</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
