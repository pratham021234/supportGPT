import { apiClient } from './api-client';

export interface Ticket {
  id: string;
  subject: string;
  customer: string;
  status: string;
  priority: string;
  assignedTo: string;
  created: string;
}

export const ticketClient = {
  getTickets: () => 
    apiClient<Ticket[]>('/tickets'),
};
