import { Metadata } from "next";
import Link from "next/link";
import { BookOpen, Terminal, Zap, Shield } from "lucide-react";

export const metadata: Metadata = {
  title: "Documentation",
  description: "Learn how to integrate and deploy SupportGPT.",
};

const Card = ({ title, desc, icon: Icon, href }: any) => (
  <Link href={href} className="block border rounded-xl p-6 hover:border-primary hover:shadow-sm transition-all bg-card">
    <Icon className="w-8 h-8 text-primary mb-4" />
    <h3 className="text-lg font-semibold mb-2">{title}</h3>
    <p className="text-sm text-muted-foreground m-0">{desc}</p>
  </Link>
);

export default function DocsHomePage() {
  return (
    <div>
      <h1 className="text-4xl font-bold tracking-tight mb-4">SupportGPT Documentation</h1>
      <p className="text-xl text-muted-foreground mb-10">
        Everything you need to build, deploy, and scale AI-driven customer support.
      </p>

      <div className="grid sm:grid-cols-2 gap-6 not-prose mb-12">
        <Card 
          title="Getting Started" 
          desc="Learn the core concepts and launch your first AI agent in under 10 minutes." 
          icon={Zap} 
          href="/docs/getting-started" 
        />
        <Card 
          title="API Reference" 
          desc="Integrate SupportGPT deeply into your stack using our REST API." 
          icon={Terminal} 
          href="/docs/api" 
        />
        <Card 
          title="Knowledge Base" 
          desc="Best practices for structuring and formatting data for RAG ingestion." 
          icon={BookOpen} 
          href="#" 
        />
        <Card 
          title="Security & Compliance" 
          desc="Details on RBAC, encryption, data residency, and SOC2." 
          icon={Shield} 
          href="#" 
        />
      </div>

      <hr className="my-10" />

      <h2>What is SupportGPT?</h2>
      <p>
        SupportGPT is a B2B SaaS platform that enables companies to automate customer support using highly-tuned Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG). 
      </p>
      <p>
        Instead of answering the same repetitive questions, your human support team can focus on complex issues while the AI handles tier-1 requests instantly.
      </p>

      <h3>Core Components</h3>
      <ul>
        <li><strong>Knowledge Base:</strong> The ground-truth data (documents, URLs, FAQs) that the AI uses to formulate answers.</li>
        <li><strong>AI Agents:</strong> The customized personas that interact with customers. You can have different agents for different tasks (e.g., Sales Bot, Technical Support Bot).</li>
        <li><strong>Widget:</strong> An embeddable UI that customers interact with on your website.</li>
        <li><strong>Inbox (Conversations & Tickets):</strong> The internal dashboard where human agents can take over chats or respond to escalated tickets.</li>
      </ul>
    </div>
  );
}
