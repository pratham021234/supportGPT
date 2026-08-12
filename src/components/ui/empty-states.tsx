import { FileText, Ticket, MessageSquare, Bot, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border rounded-lg border-dashed bg-muted/10">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-4">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm">
          <Plus className="h-4 w-4 mr-2" />
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export const EmptyDocuments = ({ onUpload }: { onUpload?: () => void }) => (
  <EmptyState
    icon={<FileText className="h-6 w-6" />}
    title="No documents uploaded"
    description="Upload PDFs, text files, or provide website URLs to build your knowledge base."
    actionLabel="Upload Document"
    onAction={onUpload}
  />
);

export const EmptyTickets = ({ onCreate }: { onCreate?: () => void }) => (
  <EmptyState
    icon={<Ticket className="h-6 w-6" />}
    title="No active tickets"
    description="There are currently no support tickets matching your criteria."
    actionLabel="Create Ticket"
    onAction={onCreate}
  />
);

export const EmptyConversations = () => (
  <EmptyState
    icon={<MessageSquare className="h-6 w-6" />}
    title="No active conversations"
    description="Your AI agents are currently not handling any active chats."
  />
);

export const EmptyAgents = ({ onCreate }: { onCreate?: () => void }) => (
  <EmptyState
    icon={<Bot className="h-6 w-6" />}
    title="No AI agents"
    description="Create your first AI agent to start answering customer queries automatically."
    actionLabel="Create Agent"
    onAction={onCreate}
  />
);
