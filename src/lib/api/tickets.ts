import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

const useWorkspaceContext = () => {
  return {
    workspaceId: "00000000-0000-0000-0000-000000000000",
    enabled: true
  };
};

export type TicketPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";
export type TicketStatus = "OPEN" | "IN_PROGRESS" | "WAITING_CUSTOMER" | "WAITING_INTERNAL" | "RESOLVED" | "CLOSED" | "REOPENED";
export type TicketSource = "AI_ESCALATION" | "CUSTOMER" | "AGENT" | "EMAIL" | "API" | "SYSTEM";

export interface Ticket {
  id: string;
  workspace_id: string;
  conversation_id: string | null;
  customer_id: string | null;
  title: string;
  description: string | null;
  priority: TicketPriority;
  status: TicketStatus;
  category: string | null;
  source: TicketSource;
  assigned_to: string | null;
  created_by: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SLAStatus {
  is_breached: boolean;
  time_remaining_minutes: number;
  deadline: string;
}

export interface TicketResponse {
  ticket: Ticket;
  sla?: SLAStatus;
}

export interface TicketComment {
  id: string;
  ticket_id: string;
  author_id: string | null;
  content: string;
  is_internal: boolean;
  created_at: string;
}

export const ticketsService = {
  getTickets: async () => {
    const res = await apiClient.get<Ticket[]>('/tickets');
    return res.data;
  },

  getTicket: async (id: string) => {
    const res = await apiClient.get<TicketResponse>(`/tickets/${id}`);
    return res.data;
  },

  createTicket: async (data: { title: string, description?: string, priority?: TicketPriority, category?: string }) => {
    const res = await apiClient.post<Ticket>('/tickets', data);
    return res.data;
  },

  updateStatus: async (id: string, status: TicketStatus) => {
    const res = await apiClient.patch<Ticket>(`/tickets/${id}/status`, { status });
    return res.data;
  },

  assignTicket: async (id: string, user_id: string) => {
    const res = await apiClient.post<Ticket>(`/tickets/${id}/assign`, { assigned_user_id: user_id });
    return res.data;
  },

  resolveTicket: async (id: string) => {
    const res = await apiClient.post<Ticket>(`/tickets/${id}/resolve`);
    return res.data;
  },

  closeTicket: async (id: string) => {
    const res = await apiClient.post<Ticket>(`/tickets/${id}/close`);
    return res.data;
  },

  getComments: async (id: string) => {
    const res = await apiClient.get<TicketComment[]>(`/tickets/${id}/comments`);
    return res.data;
  },

  addComment: async (id: string, content: string, is_internal: boolean) => {
    const res = await apiClient.post<TicketComment>(`/tickets/${id}/comments`, { content, is_internal });
    return res.data;
  },

  // Mock Operations Data
  getOperationsDashboard: async () => {
    return {
      open_tickets: 42,
      resolved_today: 18,
      sla_compliance: 94.5,
      avg_resolution_time: "4h 12m",
      escalations: 3
    };
  },
  
  getAgentWorkload: async () => {
    return [
      { id: "1", name: "Alice Smith", assigned: 12, pending: 4, resolution_rate: 98, workload_score: 85 },
      { id: "2", name: "Bob Johnson", assigned: 8, pending: 2, resolution_rate: 95, workload_score: 60 },
      { id: "3", name: "Charlie Davis", assigned: 15, pending: 7, resolution_rate: 92, workload_score: 95 },
    ];
  },

  getTicketAnalytics: async () => {
    return {
      volume_trends: [
        { date: "Mon", count: 45 }, { date: "Tue", count: 52 }, { date: "Wed", count: 38 },
        { date: "Thu", count: 65 }, { date: "Fri", count: 48 }, { date: "Sat", count: 20 }, { date: "Sun", count: 15 }
      ],
      priority_breakdown: { low: 25, medium: 45, high: 20, urgent: 10 }
    };
  }
};

// Hooks
export const useTickets = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['tickets', workspaceId],
    queryFn: () => ticketsService.getTickets(),
    refetchInterval: 30000,
  });
};

export const useTicket = (id: string | null) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['ticket', workspaceId, id],
    queryFn: () => id ? ticketsService.getTicket(id) : null,
    enabled: !!id,
  });
};

export const useCreateTicket = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (data: Parameters<typeof ticketsService.createTicket>[0]) => ticketsService.createTicket(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', workspaceId] });
    }
  });
};

export const useUpdateTicketStatus = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (status: TicketStatus) => ticketsService.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ticket', workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ['tickets', workspaceId] });
    }
  });
};

export const useAssignTicket = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (userId: string) => ticketsService.assignTicket(id, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ticket', workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ['tickets', workspaceId] });
    }
  });
};

export const useTicketComments = (id: string | null) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['ticket-comments', workspaceId, id],
    queryFn: () => id ? ticketsService.getComments(id) : null,
    enabled: !!id,
  });
};

export const useAddTicketComment = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (data: { content: string, is_internal: boolean }) => 
      ticketsService.addComment(id, data.content, data.is_internal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ticket-comments', workspaceId, id] });
    }
  });
};

export const useTicketOperations = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['ticket-operations', workspaceId],
    queryFn: () => ticketsService.getOperationsDashboard(),
  });
};

export const useAgentWorkload = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['agent-workload', workspaceId],
    queryFn: () => ticketsService.getAgentWorkload(),
  });
};

export const useTicketAnalytics = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['ticket-analytics', workspaceId],
    queryFn: () => ticketsService.getTicketAnalytics(),
  });
};
