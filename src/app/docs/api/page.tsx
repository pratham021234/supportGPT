import { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Reference",
  description: "REST API for SupportGPT integrations.",
};

export default function ApiReferencePage() {
  return (
    <div>
      <h1>API Reference</h1>
      <p className="lead">
        The SupportGPT API is organized around REST. Our API has predictable resource-oriented URLs, returns JSON-encoded responses, and uses standard HTTP response codes.
      </p>

      <h2>Authentication</h2>
      <p>
        Authenticate your API requests by including your secret API key in the Authorization header. You can manage your API keys in the Dashboard under Settings &gt; Developer.
      </p>
      
      <pre><code>{`Authorization: Bearer sgt_live_xxxxxxxxx`}</code></pre>

      <div className="bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-500 p-4 my-6 text-sm">
        <strong className="text-amber-800 dark:text-amber-300 font-semibold mb-1 block">Security Warning</strong>
        <p className="m-0 text-amber-700 dark:text-amber-400">
          Never share your secret API keys in publicly accessible areas such as GitHub, client-side code, and so forth. All API requests must be made over HTTPS.
        </p>
      </div>

      <hr className="my-10" />

      <h2>Tickets API</h2>
      <p>Manage human-escalated support tickets programmatically.</p>

      <h3>List all tickets</h3>
      <div className="flex items-center gap-3 mb-4">
        <span className="bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400 font-mono px-2 py-1 rounded text-xs font-bold">GET</span>
        <code className="bg-muted px-2 py-1 rounded text-sm">/v1/tickets</code>
      </div>
      <p>Returns a paginated list of tickets in your workspace.</p>

      <div className="grid md:grid-cols-2 gap-6 items-start mt-6">
        <div>
           <h4>Query Parameters</h4>
           <ul className="text-sm">
             <li><code>status</code> (optional) - Filter by open, closed, or pending.</li>
             <li><code>limit</code> (optional) - Number of results to return (max 100).</li>
           </ul>
        </div>
        <div>
          <h4>Response</h4>
          <pre className="text-xs bg-zinc-950 text-zinc-300 p-4 rounded-md overflow-x-auto"><code>{`{
  "object": "list",
  "data": [
    {
      "id": "tck_123",
      "status": "open",
      "subject": "Login issue",
      "created_at": 1691234567
    }
  ],
  "has_more": false
}`}</code></pre>
        </div>
      </div>

      <hr className="my-10" />

      <h2>Conversations API</h2>
      <p>Retrieve AI conversation transcripts.</p>

      <h3>Retrieve a conversation</h3>
      <div className="flex items-center gap-3 mb-4">
        <span className="bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400 font-mono px-2 py-1 rounded text-xs font-bold">GET</span>
        <code className="bg-muted px-2 py-1 rounded text-sm">/v1/conversations/:id</code>
      </div>

      <div className="grid md:grid-cols-2 gap-6 items-start mt-6">
        <div>
           <h4>Path Parameters</h4>
           <ul className="text-sm">
             <li><code>id</code> (required) - The ID of the conversation.</li>
           </ul>
        </div>
        <div>
          <h4>Response</h4>
          <pre className="text-xs bg-zinc-950 text-zinc-300 p-4 rounded-md overflow-x-auto"><code>{`{
  "id": "conv_987",
  "messages": [
    {
      "role": "user",
      "content": "How do I reset my password?"
    },
    {
      "role": "assistant",
      "content": "You can reset it in settings."
    }
  ]
}`}</code></pre>
        </div>
      </div>

    </div>
  );
}
