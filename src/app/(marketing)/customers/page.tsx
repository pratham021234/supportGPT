import { Metadata } from "next";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { BarChart, TrendingDown, Clock } from "lucide-react";

export const metadata: Metadata = {
  title: "Customer Stories",
  description: "Read how leading companies transform their support with SupportGPT.",
};

export default function CustomersPage() {
  return (
    <div className="pb-24">
      <div className="pt-24 pb-20 text-center px-4 max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">Customer Stories</h1>
        <p className="text-xl text-muted-foreground">
          See how teams use SupportGPT to automate millions of conversations and deliver better experiences.
        </p>
      </div>

      <div className="container px-4 md:px-6">
        <div className="bg-zinc-950 text-white rounded-3xl overflow-hidden shadow-2xl max-w-6xl mx-auto flex flex-col md:flex-row mb-16">
          <div className="p-12 md:w-1/2 flex flex-col justify-center">
             <div className="mb-8 opacity-70 font-mono text-xl tracking-widest uppercase">SOYUZ</div>
             <h2 className="text-3xl md:text-4xl font-bold mb-6">"We automated 82% of our L1 support volume in two weeks."</h2>
             <p className="text-zinc-400 mb-8 text-lg">
               Soyuz, a fast-growing fintech startup, was drowning in repetitive support tickets. By deploying SupportGPT across their knowledge base, they eliminated the backlog and improved CSAT scores.
             </p>
             <div className="flex gap-4">
               <Button variant="secondary">Read Case Study</Button>
             </div>
          </div>
          <div className="bg-primary p-12 md:w-1/2 flex flex-col justify-center text-primary-foreground gap-8">
             <div className="flex items-center gap-4">
               <div className="bg-white/20 p-4 rounded-xl"><TrendingDown className="w-8 h-8" /></div>
               <div>
                 <div className="text-4xl font-bold mb-1">82%</div>
                 <div className="opacity-90">Deflection Rate</div>
               </div>
             </div>
             <div className="flex items-center gap-4">
               <div className="bg-white/20 p-4 rounded-xl"><Clock className="w-8 h-8" /></div>
               <div>
                 <div className="text-4xl font-bold mb-1">2 mins</div>
                 <div className="opacity-90">Avg. Resolution Time</div>
               </div>
             </div>
             <div className="flex items-center gap-4">
               <div className="bg-white/20 p-4 rounded-xl"><BarChart className="w-8 h-8" /></div>
               <div>
                 <div className="text-4xl font-bold mb-1">+24%</div>
                 <div className="opacity-90">CSAT Improvement</div>
               </div>
             </div>
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
           {/* Secondary Case Studies */}
           <div className="border rounded-2xl p-8 bg-background">
              <div className="mb-6 opacity-50 font-serif text-2xl font-bold">Globex</div>
              <h3 className="text-2xl font-bold mb-4">Scaling e-commerce support across 5 timezones</h3>
              <p className="text-muted-foreground mb-6">How Globex used multilingual AI agents to provide 24/7 support during the holiday rush without hiring additional temporary staff.</p>
              <Link href="#" className="text-primary font-medium hover:underline">Read story →</Link>
           </div>
           <div className="border rounded-2xl p-8 bg-background">
              <div className="mb-6 opacity-50 font-sans text-2xl font-bold tracking-tighter">Initech</div>
              <h3 className="text-2xl font-bold mb-4">Securing internal HR knowledge</h3>
              <p className="text-muted-foreground mb-6">Initech deployed a secure, SOC2 compliant internal SupportGPT instance to help employees navigate complex benefits and payroll questions.</p>
              <Link href="#" className="text-primary font-medium hover:underline">Read story →</Link>
           </div>
        </div>
      </div>
    </div>
  );
}
