import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { toast } from 'sonner';
import { useAuthStore } from '@/store/authStore';

export interface Workspace {
  id: string;
  name: string;
  created_at?: string;
  plan?: string;
  members_count?: number;
}

export interface WorkspaceInvitation {
  id: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
  expires_at: string;
}

export interface AuditLog {
  id: string;
  user_email: string;
  action: string;
  resource: string;
  ip_address: string;
  created_at: string;
}

export const workspacesService = {
  getWorkspaces: async (): Promise<Workspace[]> => {
    const res = await apiClient.get('/workspaces');
    return res.data;
  },
  
  getCurrentWorkspace: async (): Promise<Workspace> => {
    const res = await apiClient.get('/workspaces/current');
    return res.data;
  },
  
  createWorkspace: async (data: { name: string; industry?: string; region?: string }): Promise<Workspace> => {
    const res = await apiClient.post('/workspaces', data);
    return res.data;
  },
  
  switchWorkspace: async (workspace_id: string): Promise<Workspace> => {
    const res = await apiClient.post('/workspaces/switch', { workspace_id });
    return res.data;
  },
  
  updateWorkspace: async (id: string, data: { name?: string }): Promise<Workspace> => {
    const res = await apiClient.patch(`/workspaces/${id}`, data);
    return res.data;
  },
  
  getPendingInvitations: async (): Promise<WorkspaceInvitation[]> => {
    const res = await apiClient.get('/workspaces/invitations/pending');
    return res.data;
  },
  
  getAuditLogs: async (id: string): Promise<AuditLog[]> => {
    const res = await apiClient.get(`/workspaces/${id}/audit-logs`);
    return res.data;
  }
};

export const useWorkspaces = () => {
  return useQuery({
    queryKey: ['workspaces'],
    queryFn: workspacesService.getWorkspaces,
  });
};

export const useCurrentWorkspaceApi = () => {
  return useQuery({
    queryKey: ['workspace', 'current'],
    queryFn: workspacesService.getCurrentWorkspace,
  });
};

export const useAuditLogs = (workspaceId: string) => {
  return useQuery({
    queryKey: ['audit-logs', workspaceId],
    queryFn: () => workspacesService.getAuditLogs(workspaceId),
    enabled: !!workspaceId,
  });
};

export const usePendingInvitations = () => {
  return useQuery({
    queryKey: ['invitations', 'pending'],
    queryFn: workspacesService.getPendingInvitations,
  });
};

export const useCreateWorkspace = () => {
  const queryClient = useQueryClient();
  const switchWorkspaceState = useAuthStore(state => state.switchWorkspace);

  return useMutation({
    mutationFn: workspacesService.createWorkspace,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      // Automatically switch to the newly created workspace in Zustand
      switchWorkspaceState({ id: data.id, name: data.name, role: 'owner' });
      toast.success("Workspace created successfully");
    },
    onError: () => toast.error("Failed to create workspace")
  });
};

export const useSwitchWorkspace = () => {
  const queryClient = useQueryClient();
  const switchWorkspaceState = useAuthStore(state => state.switchWorkspace);
  
  return useMutation({
    mutationFn: workspacesService.switchWorkspace,
    onSuccess: (data) => {
      // Refresh the entire app cache because data belongs to the new workspace
      queryClient.clear(); 
      switchWorkspaceState({ id: data.id, name: data.name, role: 'member' });
      toast.success(`Switched to ${data.name}`);
    },
    onError: () => toast.error("Failed to switch workspace")
  });
};
