import { apiClient } from './api-client';

export interface KnowledgeDocument {
  id: string;
  name: string;
  type: string;
  status: string;
  chunks: number;
  date: string;
}

export const knowledgeClient = {
  getDocuments: () => 
    apiClient<KnowledgeDocument[]>('/knowledge'),
};
