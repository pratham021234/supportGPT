import { Metadata } from "next";
import { CheckCircle2, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pricing",
  description: "Simple, transparent pricing for teams of all sizes.",
};

const plans = [
  {
    name: "Starter",
    price: "49",
    description: "Perfect for small teams getting started with AI support.",
    features: [
      "Up to 1,000 AI resolutions/mo",
      "2 Custom AI Agents",
      "50 Knowledge Documents",
      "Standard Chat Widget",
      "Shared Inbox (3 seats)",
      "Email Support"
    ]
  },
  {
    name: "Growth",
    price: "99",
    popular: true,
    description: "For growing businesses with increasing support volumes.",
    features: [
      "Up to 5,000 AI resolutions/mo",
      "5 Custom AI Agents",
      "250 Knowledge Documents",
      "Custom Widget Branding",
      "Shared Inbox (10 seats)",
      "Prompt Studio Access",
      "Priority Email Support"
    ]
  },
  {
    name: "Professional",
    price: "199",
    description: "Advanced features for mature customer success teams.",
    features: [
      "Up to 10,000 AI resolutions/mo",
      "Unlimited AI Agents",
      "1,000 Knowledge Documents",
      "Advanced Analytics",
      "Unlimited Seats",
      "API & Webhook Access",
      "Remove 'Powered by' badge"
    ]
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "Custom limits and security for large organizations.",
    features: [
      "Custom volume limits",
      "Unlimited everything",
      "SOC2 Report Access",
      "SAML SSO",
      "Dedicated Success Manager",
      "Custom SLAs",
      "On-premise deployment options"
    ],
    buttonText: "Contact Sales",
    href: "/contact-sales"
  }
];

export default function PricingPage() {
  return (
    <div className="pb-24">
      {/* Header */}
      <div className="pt-24 pb-20 text-center px-4 max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">Pricing that scales with your support team</h1>
        <p className="text-xl text-muted-foreground">
          Start for free for 14 days. No credit card required. Only pay for successful AI resolutions.
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="container px-4 md:px-6">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {plans.map((plan) => (
            <div key={plan.name} className={`flex flex-col bg-background rounded-2xl border p-8 shadow-sm relative ${plan.popular ? 'border-primary shadow-lg ring-1 ring-primary' : ''}`}>
              {plan.popular && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <div className="bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Most Popular</div>
                </div>
              )}
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-muted-foreground text-sm h-10">{plan.description}</p>
              </div>
              <div className="mb-6 flex items-baseline gap-1">
                {plan.price !== "Custom" && <span className="text-4xl font-bold tracking-tight">$</span>}
                <span className="text-5xl font-bold tracking-tight">{plan.price}</span>
                {plan.price !== "Custom" && <span className="text-muted-foreground font-medium">/mo</span>}
              </div>
              <Link href={plan.href || "/register"} className="block w-full mb-8">
                <Button className="w-full h-12" variant={plan.popular ? "default" : "outline"}>
                  {plan.buttonText || "Start Free Trial"}
                </Button>
              </Link>
              <div className="flex-1 space-y-4">
                <p className="text-sm font-semibold">What's included:</p>
                <ul className="space-y-3">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div className="container px-4 md:px-6 mt-32 max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
        <div className="space-y-6">
          {[
            { q: "What counts as an AI resolution?", a: "A resolution is counted when the AI successfully answers a customer's query and the customer either confirms it was helpful or closes the chat without requesting human escalation." },
            { q: "Do I pay for human agent seats?", a: "No! Unlike traditional helpdesks, SupportGPT charges based on AI volume, not human seats. (Except on the Starter plan which is capped at 3)." },
            { q: "What happens if I exceed my document limit?", a: "You will be prompted to upgrade to the next tier. Your existing documents will remain active, but you won't be able to upload new ones." },
            { q: "Can I use my own OpenAI keys?", a: "Yes, Professional and Enterprise customers can bring their own LLM API keys to manage their own compute costs." }
          ].map((faq, i) => (
            <div key={i} className="border-b pb-6">
              <h4 className="text-lg font-bold flex items-center gap-2 mb-3"><HelpCircle className="w-5 h-5 text-primary"/> {faq.q}</h4>
              <p className="text-muted-foreground pl-7">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
