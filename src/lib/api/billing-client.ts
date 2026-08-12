import { apiClient } from './client';

export interface BillingInfo {
  plan: string;
  price: number;
  renewalDate: string;
  usage: {
    current: number;
    limit: number;
  };
}

export const billingClient = {
  getBillingInfo: () => 
    apiClient<BillingInfo>('/billing/info'),
};
