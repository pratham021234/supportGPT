import { apiClient } from './api-client';

export interface WidgetConfig {
  primaryColor: string;
  welcomeMessage: string;
  embedCode: string;
}

export const widgetClient = {
  getWidgetConfig: () => 
    apiClient<WidgetConfig>('/widget/config'),
};
