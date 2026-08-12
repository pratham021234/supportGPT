import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Getting Started",
  description: "Launch your first AI agent in under 10 minutes.",
};

export default function GettingStartedPage() {
  return (
    <div>
      <h1>Getting Started</h1>
      <p className="lead">
        Follow this guide to configure your workspace, upload knowledge, and embed your first AI agent.
      </p>

      <h2>Step 1: Create a Workspace</h2>
      <p>
        When you first sign up, you will be prompted to create a Workspace. A Workspace represents your company or organization. All agents, knowledge documents, and billing are tied to a Workspace.
      </p>
      
      <h2>Step 2: Upload Knowledge</h2>
      <p>
        Before an AI agent can answer questions, it needs data. Head to the <strong>Knowledge Base</strong> tab in your dashboard.
      </p>
      <ol>
        <li>Click <strong>Add Knowledge</strong>.</li>
        <li>Select either <strong>File Upload</strong> (PDF, TXT, DOCX) or <strong>Website Crawl</strong>.</li>
        <li>Wait for the status to change to <code>Processed</code>. This means the data has been chunked and embedded in our vector database.</li>
      </ol>

      <h2>Step 3: Create an Agent</h2>
      <p>
        Now navigate to the <strong>Agents</strong> tab.
      </p>
      <ol>
        <li>Click <strong>Create Agent</strong>.</li>
        <li>Give it a name (e.g., "Support Bot").</li>
        <li>In the <strong>System Prompt</strong>, define its persona. For example: <em>"You are a helpful support agent for Acme Corp. Always be polite and concise."</em></li>
        <li>Link the knowledge documents you uploaded in Step 2 to this agent.</li>
      </ol>

      <h2>Step 4: Embed the Widget</h2>
      <p>
        Go to the <strong>Widget</strong> tab and grab your unique embed snippet. Paste it into the <code>&lt;head&gt;</code> of your website.
      </p>
      
      <pre><code>{`<script 
  src="https://cdn.supportgpt.com/widget.js" 
  data-workspace-id="ws_12345" 
  data-agent-id="ag_67890" 
  defer>
</script>`}</code></pre>

      <div className="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 p-4 my-6 text-sm">
        <strong className="text-blue-800 dark:text-blue-300 font-semibold mb-1 block">Pro Tip</strong>
        <p className="m-0 text-blue-700 dark:text-blue-400">
          You can test your agent internally using the <strong>Prompt Studio</strong> before embedding it live on your site.
        </p>
      </div>

      <h2>Step 5: Monitor & Refine</h2>
      <p>
        Once live, monitor incoming queries in the <strong>Conversations</strong> tab. If the AI hallucinates or fails to answer, you can instantly edit its Knowledge Base or adjust its Prompt to improve future responses.
      </p>
    </div>
  );
}
