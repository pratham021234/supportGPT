import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MessageSquareCode, ArrowRight, Bot, Zap, Shield, BarChart3 } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Navigation */}
      <header className="px-6 lg:px-14 h-20 flex items-center justify-between border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-2 text-primary font-bold text-xl">
          <MessageSquareCode className="h-6 w-6" />
          <span>SupportGPT</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link href="#features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-primary transition-colors">How it works</Link>
          <Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link>
          <Link href="/docs" className="hover:text-primary transition-colors">Docs</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-primary transition-colors">
            Sign in
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative pt-32 pb-24 lg:pt-48 lg:pb-32 overflow-hidden">
          <div className="absolute inset-0 bg-primary/5 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />
          <div className="container px-4 md:px-6 relative z-10 flex flex-col items-center text-center">
            <div className="inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium mb-8 bg-background shadow-sm">
              <span className="flex h-2 w-2 rounded-full bg-primary mr-2"></span>
              SupportGPT 2.0 is now live
            </div>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl mb-8">
              Deploy AI customer support agents trained on <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-500">company knowledge</span>.
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mb-10">
              Instantly resolve customer queries with intelligent agents. Upload your documentation, FAQs, and past tickets, and let SupportGPT handle the rest.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
              <Link href="/register">
                <Button size="lg" className="h-14 px-8 text-lg">
                  Start for free <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="#demo">
                <Button size="lg" variant="outline" className="h-14 px-8 text-lg">
                  Book a demo
                </Button>
              </Link>
            </div>
            
            {/* Dashboard Preview Image */}
            <div className="mt-20 relative w-full max-w-5xl mx-auto">
              <div className="rounded-xl border bg-background/50 backdrop-blur-sm shadow-2xl overflow-hidden ring-1 ring-white/10">
                <div className="h-10 border-b flex items-center px-4 bg-muted/50 gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <div className="aspect-[16/9] bg-zinc-950 p-8 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center opacity-20">
                     <BarChart3 className="w-64 h-64 text-primary" />
                  </div>
                  <p className="text-zinc-500 font-mono relative z-10">Dashboard Preview (Mockup)</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-muted/50">
          <div className="container px-4 md:px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Enterprise-grade support, simplified.</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Everything you need to scale your customer success team without scaling your headcount.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4 transition-all hover:shadow-md">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-2">
                  <Bot className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold">Instant Resolution</h3>
                <p className="text-muted-foreground">
                  Our AI agents understand context and provide accurate answers with source citations in seconds.
                </p>
              </div>
              <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4 transition-all hover:shadow-md">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-2">
                  <Zap className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold">Smart Handoff</h3>
                <p className="text-muted-foreground">
                  When confidence is low, the AI automatically creates a ticket and seamlessly routes it to a human agent.
                </p>
              </div>
              <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4 transition-all hover:shadow-md">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-2">
                  <Shield className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold">Knowledge Security</h3>
                <p className="text-muted-foreground">
                  Your data stays yours. Enterprise-grade encryption and secure vector databases ensure complete privacy.
                </p>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t py-12 bg-background">
        <div className="container px-4 md:px-6 flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-muted-foreground">
          <div className="flex items-center gap-2 text-primary font-bold text-lg">
            <MessageSquareCode className="h-5 w-5" />
            <span>SupportGPT</span>
          </div>
          <p>© 2026 SupportGPT Inc. All rights reserved.</p>
          <div className="flex gap-6">
            <Link href="#" className="hover:text-foreground">Twitter</Link>
            <Link href="#" className="hover:text-foreground">GitHub</Link>
            <Link href="#" className="hover:text-foreground">LinkedIn</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
