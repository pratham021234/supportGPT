import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { toast } from 'sonner';

export interface Plan {
  id: string;
  name: string;
  stripe_price_id: string;
  price_monthly: number;
  features: Record<string, any>;
}

export interface Subscription {
  id: string;
  stripe_subscription_id: string;
  stripe_customer_id: string;
  status: string; // active, past_due, canceled, trialing
  current_period_end: string;
  cancel_at_period_end: boolean;
  plan: Plan;
}

export interface Invoice {
  id: string;
  stripe_invoice_id: string;
  amount_due: number;
  amount_paid: number;
  status: string; // paid, open, void, uncollectible
  invoice_pdf: string;
  created_at: string;
}

export interface UsageSummary {
  conversations_count: number;
  conversations_limit: number;
  documents_count: number;
  documents_limit: number;
  agents_count: number;
  agents_limit: number;
  api_calls_count: number;
  api_calls_limit: number;
}

export const billingService = {
  // Live Endpoints
  getPlans: async (): Promise<Plan[]> => {
    const res = await apiClient.get('/billing/plans');
    return res.data;
  },

  getSubscription: async (): Promise<Subscription> => {
    const res = await apiClient.get('/billing/subscription');
    return res.data;
  },

  getInvoices: async (): Promise<Invoice[]> => {
    const res = await apiClient.get('/billing/invoices');
    return res.data;
  },

  getUsage: async (): Promise<UsageSummary> => {
    const res = await apiClient.get('/billing/usage');
    return res.data;
  },

  createCheckout: async (plan_id: string): Promise<{ url: string }> => {
    const res = await apiClient.post('/billing/checkout', { plan_id });
    return res.data;
  },

  createCustomerPortal: async (): Promise<{ url: string }> => {
    const res = await apiClient.post('/billing/customer-portal');
    return res.data;
  },

  cancelSubscription: async (): Promise<{ message: string }> => {
    const res = await apiClient.post('/billing/cancel');
    return res.data;
  },

  getPaymentMethods: async (): Promise<any[]> => {
    const res = await apiClient.get('/billing/payment-methods');
    return res.data;
  },

  getSeats: async (): Promise<any> => {
    const res = await apiClient.get('/billing/seats');
    return res.data;
  },

  getHistory: async (): Promise<any[]> => {
    const res = await apiClient.get('/billing/history');
    return res.data;
  },

  getAnalytics: async (): Promise<any> => {
    const res = await apiClient.get('/billing/analytics');
    return res.data;
  },
  
  getTaxInfo: async (): Promise<any> => {
    const res = await apiClient.get('/billing/tax');
    return res.data;
  },

  updateTaxInfo: async (data: any): Promise<any> => {
    const res = await apiClient.post('/billing/tax', data);
    return res.data;
  }
};

// --- Hooks ---

export const usePlans = () => useQuery({ queryKey: ['billing-plans'], queryFn: billingService.getPlans });
export const useSubscription = () => useQuery({ queryKey: ['billing-subscription'], queryFn: billingService.getSubscription });
export const useInvoices = () => useQuery({ queryKey: ['billing-invoices'], queryFn: billingService.getInvoices });
export const useUsage = () => useQuery({ queryKey: ['billing-usage'], queryFn: billingService.getUsage });

export const usePaymentMethods = () => useQuery({ queryKey: ['billing-payment-methods'], queryFn: billingService.getPaymentMethods });
export const useSeats = () => useQuery({ queryKey: ['billing-seats'], queryFn: billingService.getSeats });
export const useBillingHistory = () => useQuery({ queryKey: ['billing-history'], queryFn: billingService.getHistory });
export const useBillingAnalytics = () => useQuery({ queryKey: ['billing-analytics'], queryFn: billingService.getAnalytics });
export const useTaxInfo = () => useQuery({ queryKey: ['billing-tax'], queryFn: billingService.getTaxInfo });

export const useCheckout = () => {
  return useMutation({
    mutationFn: billingService.createCheckout,
    onSuccess: (data) => {
      // Redirect to Stripe Hosted Checkout
      if (data.url) window.location.href = data.url;
    },
    onError: () => toast.error('Failed to initiate checkout. Stripe keys may be missing locally.')
  });
};

export const useCustomerPortal = () => {
  return useMutation({
    mutationFn: billingService.createCustomerPortal,
    onSuccess: (data) => {
      if (data.url) window.location.href = data.url;
    },
    onError: () => toast.error('Failed to open customer portal.')
  });
};

export const useCancelSubscription = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: billingService.cancelSubscription,
    onSuccess: () => {
      toast.success('Subscription cancelled successfully.');
      queryClient.invalidateQueries({ queryKey: ['billing-subscription'] });
    },
    onError: () => toast.error('Failed to cancel subscription.')
  });
};

export const useUpdateTaxInfo = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: billingService.updateTaxInfo,
    onSuccess: () => {
      toast.success('Tax information updated.');
      queryClient.invalidateQueries({ queryKey: ['billing-tax'] });
    },
    onError: () => toast.error('Failed to update tax information.')
  });
};
