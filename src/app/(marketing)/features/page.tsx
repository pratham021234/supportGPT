import { Metadata } from "next";
import { Bot, MessageSquare, Shield, Zap, Search, Layout, Settings2, BarChart3, Clock, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Features",
  description: "Explore the powerful features of SupportGPT.",
};

const FeatureItem = ({ icon: Icon, title, description }: { icon: any, title: string, description: string }) => (
  <div className="flex gap-4">
    <div className="mt-1 bg-primary/10 p-3 rounded-lg h-fit text-primary">
      <Icon className="w-6 h-6" />
    </div>
    <div>
      <h3 className="font-bold text-xl mb-2">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
    </div>
  </div>
);

export default function FeaturesPage() {
  return (
    <div className="pb-24">
      {/* Header */}
      <div className="bg-zinc-950 text-white pt-24 pb-32 text-center px-4">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">Built for scale. Designed for speed.</h1>
        <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
          SupportGPT provides a comprehensive suite of tools to automate your customer service pipeline from end to end.
        </p>
      </div>

      {/* Main Features */}
      <div className="container px-4 md:px-6 -mt-16">
        <div className="bg-background rounded-2xl shadow-xl border p-8 md:p-12 grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
          <FeatureItem 
            icon={Bot} 
            title="Custom AI Agents" 
            description="Create specialized agents with unique personas, instructions, and access to specific knowledge bases. Configure fallback behaviors when the AI is unsure." 
          />
          <FeatureItem 
            icon={Search} 
            title="RAG Knowledge Engine" 
            description="Our advanced Retrieval-Augmented Generation pipeline ingests your PDFs, Notion pages, and URLs, ensuring answers are strictly derived from your ground truth data." 
          />
          <FeatureItem 
            icon={MessageSquare} 
            title="Omnichannel Widget" 
            description="Embed our beautiful chat widget on your website with a single line of code. It supports streaming responses, markdown, and automatic citation linking." 
          />
          <FeatureItem 
            icon={Layout} 
            title="Human Handoff Inbox" 
            description="When queries get too complex, agents seamlessly transition the chat to a human-readable ticket in your shared team inbox, maintaining full context." 
          />
          <FeatureItem 
            icon={BarChart3} 
            title="Resolution Analytics" 
            description="Track your deflection rate, average resolution time, and agent CSAT scores with our comprehensive business intelligence dashboards." 
          />
          <FeatureItem 
            icon={Shield} 
            title="Enterprise Security" 
            description="Your data is encrypted at rest and in transit. We offer strict role-based access controls (RBAC) and SOC2 compliant infrastructure." 
          />
        </div>
      </div>

      {/* Deep Dive Section */}
      <div className="container px-4 md:px-6 mt-32 max-w-5xl mx-auto">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl font-bold mb-6">Prompt Studio</h2>
            <p className="text-lg text-muted-foreground mb-6">
              Take complete control over how your AI behaves. The Prompt Studio lets you test instructions, evaluate responses against real customer queries, and adjust temperature and penalty parameters before deploying to production.
            </p>
            <ul className="space-y-3">
              <li className="flex items-center gap-3"><Settings2 className="text-primary w-5 h-5"/> Test against live data</li>
              <li className="flex items-center gap-3"><Clock className="text-primary w-5 h-5"/> Version control your prompts</li>
              <li className="flex items-center gap-3"><Lock className="text-primary w-5 h-5"/> Strict hallucination guardrails</li>
            </ul>
          </div>
          <div className="bg-zinc-100 rounded-2xl aspect-square flex items-center justify-center border relative overflow-hidden">
             {/* Mockup visual */}
             <div className="absolute inset-0 bg-gradient-to-br from-zinc-200 to-zinc-300 opacity-50"></div>
             <div className="w-3/4 h-3/4 bg-white shadow-xl rounded-xl border flex flex-col p-4 relative z-10">
               <div className="w-1/2 h-4 bg-zinc-200 rounded mb-6"></div>
               <div className="flex-1 border rounded p-3 bg-zinc-50 mb-4 font-mono text-xs text-zinc-500">
                 You are a helpful assistant for Acme Corp. Always cite your sources. If you don't know the answer, escalate to a human.
               </div>
               <div className="h-10 bg-primary rounded-md text-white text-sm font-medium flex items-center justify-center">Test Prompt</div>
             </div>
          </div>
        </div>
      </div>

      <div className="container px-4 md:px-6 mt-32 text-center">
        <h2 className="text-3xl font-bold mb-6">Ready to see it in action?</h2>
        <Link href="/register">
          <Button size="lg" className="h-14 px-8 text-lg">Start Free Trial</Button>
        </Link>
      </div>
    </div>
  );
}
