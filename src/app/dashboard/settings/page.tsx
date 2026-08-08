import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { useQuery } from "@tanstack/react-query";
import { widgetClient } from "@/lib/api/widget-client";
import { billingClient } from "@/lib/api/billing-client";
import { Skeleton } from "@/components/ui/skeleton";

export default function SettingsPage() {
  const { data: widgetConfig, isLoading: loadingWidget } = useQuery({
    queryKey: ["settings-widget"],
    queryFn: widgetClient.getWidgetConfig,
  });

  const { data: billingInfo, isLoading: loadingBilling } = useQuery({
    queryKey: ["settings-billing"],
    queryFn: billingClient.getBillingInfo,
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your workspace, billing, and system preferences.
        </p>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-4">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="widget">Chat Widget</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
          <TabsTrigger value="api">API Keys</TabsTrigger>
        </TabsList>
        
        <TabsContent value="general" className="mt-6">
          <Card className="max-w-2xl">
            <CardHeader>
              <CardTitle>Workspace Profile</CardTitle>
              <CardDescription>
                Update your company information and support email.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="company">Company Name</Label>
                <Input id="company" defaultValue="Acme Corp" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Support Email</Label>
                <Input id="email" defaultValue="support@acmecorp.com" />
              </div>
              <div className="flex items-center justify-between mt-6">
                <div className="space-y-0.5">
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive daily summaries of unresolved tickets.</p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
            <CardFooter className="border-t px-6 py-4">
              <Button>Save Changes</Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="widget" className="mt-6">
          <Card className="max-w-2xl">
            <CardHeader>
              <CardTitle>Chat Widget Configuration</CardTitle>
              <CardDescription>
                Customize how the SupportGPT widget looks on your website.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingWidget ? (
                <div className="space-y-4">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-32 w-full mt-4" />
                </div>
              ) : (
                <>
                  <div className="space-y-2">
                    <Label>Primary Color</Label>
                    <div className="flex gap-2">
                      <div className="w-8 h-8 rounded-full bg-primary ring-2 ring-offset-2 ring-primary cursor-pointer"></div>
                      <div className="w-8 h-8 rounded-full bg-blue-500 cursor-pointer"></div>
                      <div className="w-8 h-8 rounded-full bg-emerald-500 cursor-pointer"></div>
                      <div className="w-8 h-8 rounded-full bg-zinc-900 cursor-pointer"></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="welcome">Welcome Message</Label>
                    <Input id="welcome" defaultValue={widgetConfig?.welcomeMessage || "Hi there! How can I help you today?"} />
                  </div>
                  <div className="space-y-2 mt-4 p-4 border rounded-md bg-muted/30">
                    <Label>Embed Code</Label>
                    <pre className="text-xs p-2 bg-muted rounded overflow-x-auto mt-2 text-muted-foreground">
                      {widgetConfig?.embedCode || `<script src="https://cdn.supportgpt.ai/widget.js" data-workspace-id="ws_12345"></script>`}
                    </pre>
                    <Button variant="outline" size="sm" className="mt-2">Copy Code</Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing" className="mt-6">
          <Card className="max-w-2xl">
            <CardHeader>
              <CardTitle>Subscription Plan</CardTitle>
              <CardDescription>
                You are currently on the Pro plan.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingBilling ? (
                <div className="space-y-4">
                  <Skeleton className="h-12 w-32 mb-1" />
                  <Skeleton className="h-4 w-48 mb-4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-2 w-full rounded-full" />
                </div>
              ) : (
                <>
                  <div className="text-3xl font-bold mb-1">${billingInfo?.price || 299}<span className="text-lg text-muted-foreground font-normal">/mo</span></div>
                  <p className="text-sm text-muted-foreground mb-4">Renews on {billingInfo?.renewalDate || 'Sept 1, 2026'}</p>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>AI Conversations ({billingInfo?.usage?.current?.toLocaleString() || '8,234'} / {billingInfo?.usage?.limit?.toLocaleString() || '10,000'})</span>
                      <span className="font-medium">{billingInfo ? Math.round((billingInfo.usage.current / billingInfo.usage.limit) * 100) : 82}%</span>
                    </div>
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${billingInfo ? (billingInfo.usage.current / billingInfo.usage.limit) * 100 : 82}%` }}></div>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
            <CardFooter className="border-t px-6 py-4 flex gap-2">
              <Button>Upgrade Plan</Button>
              <Button variant="outline">Manage Billing</Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="mt-6">
          <Card className="max-w-2xl">
            <CardHeader>
              <CardTitle>API Keys</CardTitle>
              <CardDescription>
                Use these keys to authenticate API requests from your backend.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Production Key</Label>
                <div className="flex gap-2">
                  <Input type="password" value="sk_live_1234567890abcdef" readOnly />
                  <Button variant="outline">Copy</Button>
                </div>
              </div>
            </CardContent>
            <CardFooter className="border-t px-6 py-4">
              <Button variant="secondary">Generate New Key</Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
