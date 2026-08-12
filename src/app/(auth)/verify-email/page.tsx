"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { authService } from "@/lib/api/auth";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { toast } from "sonner";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams?.get("token");
  const router = useRouter();
  
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setErrorMessage("No verification token provided.");
      return;
    }

    const verify = async () => {
      try {
        await authService.verifyEmail(token);
        setStatus("success");
      } catch (error: any) {
        setStatus("error");
        setErrorMessage(error.message || "Failed to verify email. The link may be expired.");
      }
    };

    verify();
  }, [token]);

  return (
    <div className="flex flex-col gap-6 items-center text-center">
      {status === "loading" && (
        <>
          <Loader2 className="h-12 w-12 text-primary animate-spin mb-2" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Verifying Email</h1>
            <p className="text-muted-foreground text-sm">
              Please wait while we verify your email address...
            </p>
          </div>
        </>
      )}

      {status === "success" && (
        <>
          <CheckCircle2 className="h-12 w-12 text-green-500 mb-2" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Email Verified</h1>
            <p className="text-muted-foreground text-sm">
              Your email has been successfully verified. You can now access your account.
            </p>
          </div>
          <Button asChild className="w-full mt-4">
            <Link href="/login">Continue to Login</Link>
          </Button>
        </>
      )}

      {status === "error" && (
        <>
          <XCircle className="h-12 w-12 text-destructive mb-2" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Verification Failed</h1>
            <p className="text-muted-foreground text-sm">{errorMessage}</p>
          </div>
          <Button asChild className="w-full mt-4">
            <Link href="/login">Back to Login</Link>
          </Button>
        </>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col gap-6 items-center text-center">
        <Loader2 className="h-12 w-12 text-primary animate-spin mb-2" />
        <h1 className="text-3xl font-bold tracking-tight mb-2">Loading...</h1>
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
