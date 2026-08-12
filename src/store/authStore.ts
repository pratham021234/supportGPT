import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Workspace {
  id: string;
  name: string;
  role: string;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  avatar_url?: string;
  roles: string[];
  permissions?: string[];
  token?: string;
  workspace_id?: string;
  name?: string;
}

interface AuthState {
  user: User | null;
  workspace: Workspace | null;
  permissions: string[];
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  
  login: (user: User, workspace: Workspace | null, permissions: string[], accessToken: string, refreshToken: string) => void;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  updateUser: (user: Partial<User>) => void;
  switchWorkspace: (workspace: Workspace) => void;
  updateToken: (accessToken: string, refreshToken: string) => void;
  setInitializing: (isInitializing: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      workspace: null,
      permissions: [],
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitializing: true,
      
      login: (user, workspace, permissions, accessToken, refreshToken) =>
        set({ user, workspace, permissions, accessToken, refreshToken, isAuthenticated: true }),
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),
      updateUser: (updatedUser) =>
        set((state) => ({ user: state.user ? { ...state.user, ...updatedUser } : null })),
      switchWorkspace: (workspace) =>
        set({ workspace }),
      updateToken: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken }),
      setInitializing: (isInitializing) =>
        set({ isInitializing }),
      logout: () => set({ 
        user: null, 
        workspace: null, 
        permissions: [], 
        accessToken: null, 
        refreshToken: null, 
        isAuthenticated: false 
      }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ 
        user: state.user,
        workspace: state.workspace,
        permissions: state.permissions,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      }), // Don't persist isInitializing
    }
  )
);
