"use client";

import { useAuthStore } from "@/store/authStore";
import { AccessDenied, Unauthorized } from "./AuthError";
import { AuthLoadingScreen } from "./AuthLoadingScreen";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isInitializing } = useAuthStore();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || isInitializing) return <AuthLoadingScreen />;

  if (!isAuthenticated) {
    router.replace("/login");
    return <Unauthorized />;
  }

  return <>{children}</>;
}

export function RoleGuard({ 
  allowedRoles, 
  children 
}: { 
  allowedRoles: string[]; 
  children: React.ReactNode 
}) {
  const { user, isInitializing } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || isInitializing) return <AuthLoadingScreen />;

  const hasRole = user?.roles?.some(role => allowedRoles.includes(role));

  if (!hasRole) {
    return <AccessDenied />;
  }

  return <>{children}</>;
}

export function PermissionGuard({ 
  permissions, 
  children,
  fallback = null
}: { 
  permissions: string[]; 
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  const { permissions: userPermissions, isInitializing } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || isInitializing) return null;

  // Verify user has all required permissions
  const hasPermissions = permissions.every(p => userPermissions.includes(p));

  if (!hasPermissions) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
