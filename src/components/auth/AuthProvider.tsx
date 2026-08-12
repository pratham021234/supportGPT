"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/lib/api/auth";
import { AuthLoadingScreen } from "./AuthLoadingScreen";
import { usePathname, useRouter } from "next/navigation";

// List of routes that do not require authentication
const publicRoutes = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { 
    accessToken, 
    isAuthenticated, 
    isInitializing, 
    setInitializing, 
    updateUser, 
    logout 
  } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    let mounted = true;

    const initAuth = async () => {
      try {
        if (!accessToken) {
          throw new Error("No access token");
        }

        // Validate session by fetching the current user
        const response = await authService.getCurrentUser();
        // The API interceptor handles token refresh internally if 401 occurs
        
        if (mounted && response) {
          updateUser(response);
          // Assuming workspace context and permissions might be returned or inferred
          // If the backend returns them, update them via authStore actions
        }
      } catch (error) {
        // Validation failed, clear state
        if (mounted) {
          logout();
        }
      } finally {
        if (mounted) {
          setInitializing(false);
        }
      }
    };

    if (isInitializing) {
      initAuth();
    }
    
    return () => {
      mounted = false;
    };
  }, [accessToken, isInitializing, setInitializing, updateUser, logout]);

  useEffect(() => {
    // Redirection logic post-initialization
    if (!isInitializing) {
      const isPublicRoute = publicRoutes.some(route => pathname?.startsWith(route));
      const isAuthRoute = ["/login", "/register"].some(route => pathname?.startsWith(route));

      if (!isAuthenticated && !isPublicRoute) {
        // Redirect to login if trying to access protected route without auth
        router.replace("/login");
      } else if (isAuthenticated && isAuthRoute) {
        // Redirect to dashboard if trying to access login/register while authenticated
        router.replace("/dashboard");
      }
    }
  }, [isInitializing, isAuthenticated, pathname, router]);

  if (isInitializing) {
    return <AuthLoadingScreen />;
  }

  return <>{children}</>;
}
