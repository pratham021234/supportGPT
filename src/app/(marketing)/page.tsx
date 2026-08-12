import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Bot, Zap, Shield, Sparkles, CheckCircle2, ChevronRight, BarChart3, Users, MessageSquare } from "lucide-react";
import Image from "next/image";

export default function LandingPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative pt-32 pb-24 lg:pt-40 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-primary/5 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
        
        {/* Decorative elements */}
        <div className="absolute top-1/4 left-0 w-64 h-64 bg-primary/20 rounded-full blur-3xl opacity-50 mix-blend-multiply pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-50 mix-blend-multiply pointer-events-none" />
        
        <div className="container px-4 md:px-6 relative z-10 flex flex-col items-center text-center">
          <Link href="/blog/introducing-supportgpt-2">
            <div className="inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium mb-8 bg-background shadow-sm hover:shadow transition-all hover:-translate-y-0.5 cursor-pointer">
              <Sparkles className="w-4 h-4 text-primary mr-2" />
              SupportGPT 2.0 is now live <ChevronRight className="w-4 h-4 ml-1 opacity-50" />
            </div>
          </Link>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl mb-6">
            Deploy AI support agents trained on <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-600">your knowledge</span>.
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed">
            Reduce support workload by 80%. Deliver instant, accurate answers with citations, and seamlessly escalate complex issues to human agents.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link href="/register">
              <Button size="lg" className="h-14 px-8 text-lg w-full sm:w-auto group">
                Start Free Trial <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/contact-sales">
              <Button size="lg" variant="outline" className="h-14 px-8 text-lg w-full sm:w-auto">
                Book a Demo
              </Button>
            </Link>
          </div>
          
          {/* Dashboard Preview Mockup */}
          <div className="mt-20 relative w-full max-w-5xl mx-auto perspective-[2000px]">
            <div className="rounded-xl border bg-background/50 backdrop-blur-sm shadow-2xl overflow-hidden ring-1 ring-white/10 transform-gpu rotate-x-12 scale-95 hover:rotate-x-0 hover:scale-100 transition-all duration-700 ease-out origin-bottom">
              <div className="h-10 border-b flex items-center px-4 bg-muted/50 gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
              </div>
              <div className="aspect-[16/9] bg-zinc-950 p-8 flex items-center justify-center relative overflow-hidden">
                {/* Abstract UI representation */}
                <div className="absolute inset-0 bg-gradient-to-br from-zinc-900 to-zinc-950 flex flex-col p-6 gap-6">
                  <div className="flex gap-4">
                    <div className="w-64 h-24 rounded-lg bg-zinc-800/50 border border-zinc-700/50 flex flex-col justify-center px-4 gap-2">
                       <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center"><MessageSquare className="w-4 h-4 text-primary" /></div>
                       <div className="w-24 h-2 bg-zinc-700 rounded"></div>
                       <div className="w-32 h-2 bg-zinc-600 rounded"></div>
                    </div>
                    <div className="w-64 h-24 rounded-lg bg-zinc-800/50 border border-zinc-700/50 flex flex-col justify-center px-4 gap-2">
                       <div className="w-8 h-8 rounded bg-blue-500/20 flex items-center justify-center"><Bot className="w-4 h-4 text-blue-500" /></div>
                       <div className="w-24 h-2 bg-zinc-700 rounded"></div>
                       <div className="w-32 h-2 bg-zinc-600 rounded"></div>
                    </div>
                  </div>
                  <div className="flex-1 rounded-lg bg-zinc-800/50 border border-zinc-700/50 p-4">
                     <div className="w-48 h-4 bg-zinc-700 rounded mb-6"></div>
                     <div className="space-y-4">
                       <div className="flex justify-between items-center"><div className="w-32 h-3 bg-zinc-700 rounded"></div><div className="w-16 h-3 bg-zinc-600 rounded"></div></div>
                       <div className="flex justify-between items-center"><div className="w-40 h-3 bg-zinc-700 rounded"></div><div className="w-16 h-3 bg-zinc-600 rounded"></div></div>
                       <div className="flex justify-between items-center"><div className="w-24 h-3 bg-zinc-700 rounded"></div><div className="w-16 h-3 bg-zinc-600 rounded"></div></div>
                     </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Bar */}
      <section className="py-10 border-y bg-muted/30">
        <div className="container px-4 md:px-6">
          <p className="text-center text-sm font-medium text-muted-foreground mb-6 uppercase tracking-wider">Trusted by innovative teams worldwide</p>
          <div className="flex flex-wrap justify-center gap-10 md:gap-20 opacity-50 grayscale">
            {/* Using text logos for simulation */}
            <h3 className="text-2xl font-bold font-sans">Acme Corp</h3>
            <h3 className="text-2xl font-bold font-serif">Globex</h3>
            <h3 className="text-2xl font-black font-mono">SOYUZ</h3>
            <h3 className="text-2xl font-bold font-sans tracking-tighter">Initech</h3>
            <h3 className="text-2xl font-semibold italic">Stark Ind.</h3>
          </div>
        </div>
      </section>

      {/* How it Works / Workflow */}
      <section id="how-it-works" className="py-24">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">How SupportGPT works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From raw documentation to a fully autonomous support engine in under 10 minutes.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto relative">
             {/* Connection Line */}
             <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-primary/10 via-primary/40 to-primary/10 -z-10 -translate-y-1/2"></div>
             
             {[
               { step: "01", title: "Upload Knowledge", desc: "Sync your Help Center, Notion docs, PDFs, or raw text. Our engine embeds it instantly." },
               { step: "02", title: "Deploy AI Agent", desc: "Customize your agent's persona and logic, then embed the widget on your site with one line of code." },
               { step: "03", title: "Resolve & Route", desc: "The AI resolves 80% of queries instantly. Complex issues are automatically routed to your human team as tickets." }
             ].map((item, i) => (
               <div key={i} className="bg-background border rounded-2xl p-8 relative shadow-sm hover:shadow-md transition-all group">
                 <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-xl mb-6 shadow-lg shadow-primary/20 group-hover:scale-110 transition-transform">
                   {item.step}
                 </div>
                 <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                 <p className="text-muted-foreground">{item.desc}</p>
               </div>
             ))}
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="py-24 bg-muted/50">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Enterprise-grade capabilities</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to run a world-class customer success operation.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-2">
                <Bot className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">RAG Engine</h3>
              <p className="text-muted-foreground">
                Advanced Retrieval-Augmented Generation ensures your AI only answers based on your actual company data, preventing hallucinations.
              </p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500 mb-2">
                <MessageSquare className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Omnichannel Widget</h3>
              <p className="text-muted-foreground">
                A beautiful, embeddable chat widget that supports markdown, streaming responses, and seamless human handoff.
              </p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500 mb-2">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Prompt Studio</h3>
              <p className="text-muted-foreground">
                Fine-tune the exact tone, behavior, and escalation rules of your AI agents with a visual playground.
              </p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-500 mb-2">
                <Users className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Team Inbox</h3>
              <p className="text-muted-foreground">
                When the AI escalates a query, it lands in a powerful collaborative inbox for your human agents to resolve as a ticket.
              </p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 mb-2">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Advanced Analytics</h3>
              <p className="text-muted-foreground">
                Track resolution rates, AI deflection metrics, and human agent performance with beautiful BI dashboards.
              </p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center text-red-500 mb-2">
                <Shield className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Enterprise Security</h3>
              <p className="text-muted-foreground">
                SOC2 compliant architecture, strict RBAC, data encryption at rest, and granular workspace management.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial */}
      <section className="py-24 bg-zinc-950 text-white">
        <div className="container px-4 md:px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-8">"SupportGPT reduced our support ticket volume by 74% in the first month."</h2>
            <div className="flex flex-col items-center justify-center">
              <div className="w-16 h-16 bg-zinc-800 rounded-full mb-4"></div>
              <h4 className="font-bold text-lg">Sarah Jenkins</h4>
              <p className="text-zinc-400">VP of Customer Success, Vercel</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="py-24">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Simple, transparent pricing</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Start for free, then scale as your business grows.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 max-w-4xl mx-auto gap-8">
             <div className="border rounded-2xl p-8 bg-background">
                <h3 className="text-2xl font-bold">Starter</h3>
                <div className="mt-4 flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-bold tracking-tight">$49</span>
                  <span className="text-muted-foreground text-sm font-medium">/mo</span>
                </div>
                <ul className="space-y-4 mb-8">
                  <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-emerald-500" /> <span>Up to 1,000 conversations</span></li>
                  <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-emerald-500" /> <span>2 AI Agents</span></li>
                  <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-emerald-500" /> <span>50 Knowledge Documents</span></li>
                </ul>
                <Link href="/register">
                  <Button className="w-full" variant="outline">Start Free Trial</Button>
                </Link>
             </div>
             
             <div className="border-2 border-primary rounded-2xl p-8 bg-background relative shadow-xl">
                <div className="absolute top-0 right-8 -translate-y-1/2">
                   <div className="bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Most Popular</div>
                </div>
                <h3 className="text-2xl font-bold">Professional</h3>
                <div className="mt-4 flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-bold tracking-tight">$199</span>
                  <span className="text-muted-foreground text-sm font-medium">/mo</span>
                </div>
                <ul className="space-y-4 mb-8">
                  <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-emerald-500" /> <span>Up to 10,000 conversations</span></li>
                  <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-emerald-500" /> <span>Unlimited AI Agents</span></li>
                  <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-emerald-500" /> <span>API Access & Webhooks</span></li>
                </ul>
                <Link href="/register">
                  <Button className="w-full">Start Free Trial</Button>
                </Link>
             </div>
          </div>
          <div className="text-center mt-8">
            <Link href="/pricing" className="text-primary hover:underline font-medium">View full pricing details →</Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-primary text-primary-foreground relative overflow-hidden">
         <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
         <div className="container px-4 md:px-6 relative z-10 text-center">
            <h2 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">Ready to automate your support?</h2>
            <p className="text-xl opacity-90 max-w-2xl mx-auto mb-10">
              Join thousands of forward-thinking companies that deliver instant, accurate customer support 24/7.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register">
                <Button size="lg" variant="secondary" className="h-14 px-8 text-lg text-primary font-bold w-full sm:w-auto">
                  Get Started for Free
                </Button>
              </Link>
              <Link href="/contact-sales">
                <Button size="lg" variant="outline" className="h-14 px-8 text-lg bg-transparent border-primary-foreground/30 hover:bg-primary-foreground/10 text-white w-full sm:w-auto">
                  Contact Sales
                </Button>
              </Link>
            </div>
         </div>
      </section>
    </>
  );
}
