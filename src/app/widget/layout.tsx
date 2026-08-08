import { Suspense } from "react";
import { Loader2 } from "lucide-react";

export default function WidgetLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Suspense fallback={<div className="flex h-screen w-full items-center justify-center"><Loader2 className="animate-spin text-zinc-500" /></div>}>
      {children}
    </Suspense>
  );
}
