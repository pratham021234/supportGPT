"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/lib/api/auth";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);
  const updateUser = useAuthStore((state) => state.updateUser);
  
  useEffect(() => {
    const handleCallback = async () => {
      // In a real OAuth flow, the backend might redirect here with tokens in the URL
      // Or we might exchange an authorization code for tokens here
      
      const accessToken = searchParams?.get("access_token");
      const refreshToken = searchParams?.get("refresh_token");
      const error = searchParams?.get("error");
      
      if (error) {
        toast.error(`Authentication failed: ${error}`);
        router.push("/login");
        return;
      }
      
      if (!accessToken || !refreshToken) {
        // Fallback simulation for demonstration if backend doesn't pass tokens yet
        // In a real app this would be an error
        toast.error("Invalid OAuth callback parameters.");
        router.push("/login");
        return;
      }
      
      try {
        // Set tokens in store temporarily so API calls succeed
        useAuthStore.getState().updateToken(accessToken, refreshToken);
        
        // Fetch user profile with the new tokens
        const userResponse = await authService.getCurrentUser();
        const user = userResponse.data;
        
        // Complete the login in state
        login(
          user, 
          null, 
          user.permissions || [], 
          accessToken, 
          refreshToken
        );
        
        toast.success("Successfully logged in with Google");
        router.push("/dashboard");
      } catch (err: any) {
        toast.error(err.message || "Failed to complete Google authentication");
        router.push("/login");
      }
    };
    
    handleCallback();
  }, [searchParams, router, login, updateUser]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
      <Loader2 className="h-12 w-12 text-primary animate-spin" />
      <h1 className="text-xl font-semibold tracking-tight">Authenticating with Google...</h1>
      <p className="text-sm text-muted-foreground">Please wait while we complete your sign in.</p>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    }>
      <GoogleCallbackContent />
    </Suspense>
  );
}
