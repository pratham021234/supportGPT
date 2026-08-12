import { Loader2 } from "lucide-react";

export function AuthLoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center space-y-4 rounded-xl border bg-card p-8 shadow-lg text-center">
        <div className="relative flex h-16 w-16 items-center justify-center">
          <div className="absolute inset-0 animate-ping rounded-full bg-primary/20" />
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
        <div className="space-y-1">
          <h2 className="text-lg font-semibold tracking-tight">Authenticating</h2>
          <p className="text-sm text-muted-foreground">Validating your secure session...</p>
        </div>
      </div>
    </div>
  );
}
