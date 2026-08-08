"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/use-auth";
import { Loader2, Palette, MessageSquare, Save, Settings2, Code } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function WidgetBuilderPage() {
  const { user } = useAuth();
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadSettings() {
      if (!user) return;
      try {
        const res = await fetch("/api/v1/widget/settings", {
          headers: { Authorization: `Bearer ${user.token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setConfig(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, [user]);

  const handleSave = async () => {
    if (!user || !config) return;
    setSaving(true);
    try {
      await fetch("/api/v1/widget/settings", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`,
        },
        body: JSON.stringify({
          primary_color: config.primary_color,
          launcher_text: config.launcher_text,
          welcome_message: config.welcome_message,
          logo_url: config.logo_url
        }),
      });
      // Optionally reload iframe preview
      const iframe = document.getElementById("widget-preview-iframe") as HTMLIFrameElement;
      if (iframe) {
        iframe.src = iframe.src;
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="flex justify-center p-8"><Loader2 className="animate-spin text-zinc-400" /></div>;

  const embedCode = `<script src="https://yourdomain.com/widget.js"></script>\n<script>\n  SupportGPT.init({\n    workspaceId: "${user?.workspace_id}",\n    agentId: "" // Optional: specific agent ID\n  });\n</script>`;

  return (
    <div className="flex h-[calc(100vh-64px)] w-full overflow-hidden bg-white">
      {/* Editor */}
      <div className="w-1/2 p-8 overflow-y-auto border-r border-zinc-200">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Widget Builder</h1>
            <p className="text-zinc-500 mt-1">Customize the look and feel of your chat widget.</p>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
            Save Changes
          </Button>
        </div>

        <div className="space-y-8">
          {/* Branding */}
          <div className="space-y-4">
            <h2 className="flex items-center text-lg font-semibold"><Palette className="w-5 h-5 mr-2 text-zinc-400"/> Branding</h2>
            
            <div className="space-y-2">
              <Label>Primary Color</Label>
              <div className="flex space-x-2">
                  <Input 
                    type="color" 
                    className="w-12 h-10 p-1 rounded-md"
                    value={config?.primary_color || "#000000"}
                    onChange={e => setConfig({...config, primary_color: e.target.value})}
                  />
                  <Input 
                    type="text" 
                    value={config?.primary_color || "#000000"}
                    onChange={e => setConfig({...config, primary_color: e.target.value})}
                  />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Company Logo URL</Label>
              <Input 
                type="url" 
                placeholder="https://..." 
                value={config?.logo_url || ""}
                onChange={e => setConfig({...config, logo_url: e.target.value})}
              />
            </div>
          </div>

          {/* Messaging */}
          <div className="space-y-4">
            <h2 className="flex items-center text-lg font-semibold"><MessageSquare className="w-5 h-5 mr-2 text-zinc-400"/> Messaging</h2>
            
            <div className="space-y-2">
              <Label>Launcher Text</Label>
              <Input 
                type="text" 
                value={config?.launcher_text || ""}
                onChange={e => setConfig({...config, launcher_text: e.target.value})}
              />
            </div>

            <div className="space-y-2">
              <Label>Welcome Message</Label>
              <Textarea 
                value={config?.welcome_message || ""}
                onChange={e => setConfig({...config, welcome_message: e.target.value})}
                rows={3}
              />
            </div>
          </div>
          
          {/* Embed */}
          <div className="space-y-4">
            <h2 className="flex items-center text-lg font-semibold"><Code className="w-5 h-5 mr-2 text-zinc-400"/> Installation</h2>
            
            <div className="space-y-2">
              <Label>Embed Code</Label>
              <div className="bg-zinc-900 text-zinc-50 p-4 rounded-md text-sm font-mono whitespace-pre-wrap">
                  {embedCode}
              </div>
              <p className="text-xs text-zinc-500">Place this script immediately before the closing &lt;/body&gt; tag on your website.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="w-1/2 bg-zinc-50 p-8 flex items-center justify-center relative">
         <div className="absolute top-4 left-4 flex items-center text-zinc-400 font-medium text-sm">
             <Settings2 className="w-4 h-4 mr-2" /> Live Preview
         </div>
         {/* Live Preview Iframe */}
         <div className="relative w-[380px] h-[600px] rounded-2xl shadow-2xl overflow-hidden border border-zinc-200">
             {user && (
                 <iframe 
                    id="widget-preview-iframe"
                    src={`/widget?workspaceId=${user.workspace_id}`} 
                    className="w-full h-full border-none bg-white" 
                 />
             )}
         </div>
      </div>
    </div>
  );
}
