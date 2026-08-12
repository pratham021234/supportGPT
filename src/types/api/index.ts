export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'agent' | 'viewer';
  avatarUrl?: string;
  createdAt: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  createdAt: string;
}

export interface AuthResponse {
  user: User;
  workspace: Workspace;
  accessToken: string;
  refreshToken: string;
}

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  status: 'processing' | 'ready' | 'error';
  url: string;
  createdAt: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  status: 'Active' | 'Inactive' | 'Training';
  sources: number;
  conversations: number;
  createdAt: string;
}

export interface Conversation {
  id: string;
  name: string;
  email?: string;
  query: string;
  status: 'Active' | 'Resolved' | 'Escalated';
  ai: boolean;
  time: string;
  messages: Array<{
    id: string;
    sender: 'user' | 'agent' | 'ai';
    content: string;
    timestamp: string;
  }>;
}

export interface Ticket {
  id: string;
  subject: string;
  customer: string;
  status: 'Open' | 'Pending' | 'Resolved' | 'Closed';
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  assignedTo?: string;
  created: string;
}

export interface Analytics {
  totalConversations: number;
  conversationsTrend: string;
  aiResolutionRate: number;
  resolutionTrend: string;
  knowledgeSources: number;
  knowledgeTrend: string;
  activeTickets: number;
  ticketsTrend: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  read: boolean;
  type: 'info' | 'warning' | 'error' | 'success';
  createdAt: string;
}

export interface Subscription {
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'past_due' | 'canceled';
  currentPeriodEnd: string;
  usage: {
    conversations: number;
    limit: number;
  };
}
