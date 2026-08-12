import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { toast } from 'sonner';

export interface MarketplaceApp {
  id: string;
  name: string;
  category: string;
  description: string;
}

export interface Connection {
  id: string;
  provider: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const integrationsService = {
  getMarketplace: async (): Promise<MarketplaceApp[]> => {
    const res = await apiClient.get('/integrations/marketplace');
    return res.data;
  },

  getConnections: async (): Promise<Connection[]> => {
    const res = await apiClient.get('/integrations');
    return res.data;
  },

  connect: async (provider: string, auth_code: string): Promise<any> => {
    const res = await apiClient.post('/integrations/connect', { provider, auth_code });
    return res.data;
  },

  disconnect: async (connectionId: string): Promise<any> => {
    const res = await apiClient.post(`/integrations/${connectionId}/disconnect`);
    return res.data;
  }
};

export const useMarketplace = () => {
  return useQuery({
    queryKey: ['integrations-marketplace'],
    queryFn: integrationsService.getMarketplace,
  });
};

export const useConnections = () => {
  return useQuery({
    queryKey: ['integrations-connections'],
    queryFn: integrationsService.getConnections,
  });
};

export const useConnectIntegration = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ provider, auth_code }: { provider: string; auth_code: string }) => 
      integrationsService.connect(provider, auth_code),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations-connections'] });
      toast.success('Successfully connected integration');
    },
    onError: () => toast.error('Failed to connect integration')
  });
};

export const useDisconnectIntegration = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: integrationsService.disconnect,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations-connections'] });
      toast.success('Successfully disconnected integration');
    },
    onError: () => toast.error('Failed to disconnect integration')
  });
};
