import { ReactNode } from "react";
import Link from "next/link";
import { MessageSquareCode } from "lucide-react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="flex flex-col justify-center p-8 lg:p-24 items-center lg:items-start bg-background">
        <div className="w-full max-w-sm flex flex-col gap-8">
          <Link href="/" className="flex items-center gap-2 text-primary font-bold text-2xl w-fit">
            <MessageSquareCode className="h-8 w-8" />
            <span>SupportGPT</span>
          </Link>
          {children}
        </div>
      </div>
      <div className="hidden lg:flex flex-col justify-center p-24 bg-zinc-950 text-zinc-50 relative overflow-hidden">
        <div className="absolute inset-0 bg-primary/20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/20 via-background/0 to-background/0" />
        <div className="relative z-10 max-w-lg">
          <h2 className="text-4xl font-bold mb-6">Scale your customer support with AI.</h2>
          <p className="text-zinc-400 text-lg mb-8">
            Deploy intelligent agents that learn from your documentation, past tickets, and website to resolve customer queries instantly.
          </p>
          <div className="flex items-center gap-4">
            <div className="flex -space-x-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="w-10 h-10 rounded-full border-2 border-zinc-950 bg-zinc-800" />
              ))}
            </div>
            <p className="text-sm text-zinc-400">Join 10,000+ support teams</p>
          </div>
        </div>
      </div>
    </div>
  );
}
