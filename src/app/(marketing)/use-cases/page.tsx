import { Metadata } from "next";
import { ShoppingCart, HeartPulse, Building2, BookOpen, Cpu, Briefcase } from "lucide-react";

export const metadata: Metadata = {
  title: "Use Cases",
  description: "See how different industries use SupportGPT to automate support.",
};

const UseCaseCard = ({ icon: Icon, title, description, color }: { icon: any, title: string, description: string, color: string }) => (
  <div className="bg-background rounded-2xl border p-8 shadow-sm hover:shadow-md transition-all">
    <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center mb-6`}>
      <Icon className="w-6 h-6" />
    </div>
    <h3 className="text-xl font-bold mb-3">{title}</h3>
    <p className="text-muted-foreground">{description}</p>
  </div>
);

export default function UseCasesPage() {
  return (
    <div className="pb-24">
      <div className="pt-24 pb-20 text-center px-4 max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">Built for your industry</h1>
        <p className="text-xl text-muted-foreground">
          Discover how SupportGPT adapts to the unique knowledge and compliance requirements of different sectors.
        </p>
      </div>

      <div className="container px-4 md:px-6">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <UseCaseCard 
            icon={Cpu} 
            title="SaaS & Technology" 
            description="Sync your developer docs and API references so the AI can help users debug code, configure integrations, and navigate complex settings."
            color="bg-blue-500/10 text-blue-500"
          />
          <UseCaseCard 
            icon={ShoppingCart} 
            title="E-commerce" 
            description="Connect to your Shopify store to answer questions about shipping policies, return windows, and product specifications instantly."
            color="bg-emerald-500/10 text-emerald-500"
          />
          <UseCaseCard 
            icon={HeartPulse} 
            title="Healthcare" 
            description="Provide secure, HIPAA-compliant patient support based strictly on your approved medical policies and FAQ."
            color="bg-red-500/10 text-red-500"
          />
          <UseCaseCard 
            icon={BookOpen} 
            title="Education" 
            description="Help students navigate course catalogs, understand grading rubrics, and answer campus-specific questions."
            color="bg-amber-500/10 text-amber-500"
          />
          <UseCaseCard 
            icon={Building2} 
            title="Enterprise IT" 
            description="Deploy internal agents to help employees reset passwords, configure VPNs, and understand HR policies."
            color="bg-indigo-500/10 text-indigo-500"
          />
          <UseCaseCard 
            icon={Briefcase} 
            title="Financial Services" 
            description="Ensure compliance while answering questions about account types, fee structures, and loan applications."
            color="bg-slate-500/10 text-slate-500"
          />
        </div>
      </div>
    </div>
  );
}
