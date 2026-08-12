"use client";

import { useNotifications, useNotificationPreferences, useMarkNotificationRead, useUpdateNotificationPreferences } from "@/lib/api/notifications";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Loader2, Bell, CheckCheck, Inbox } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { useState, useEffect } from "react";

export default function NotificationsPage() {
  const { data: notifications, isLoading: loadingNotifs } = useNotifications();
  const { data: prefs, isLoading: loadingPrefs } = useNotificationPreferences();
  const { mutate: markRead } = useMarkNotificationRead();
  const { mutate: updatePrefs, isPending: updating } = useUpdateNotificationPreferences();

  const [emailEnabled, setEmailEnabled] = useState(false);
  const [inAppEnabled, setInAppEnabled] = useState(false);
  const [digestEnabled, setDigestEnabled] = useState(false);

  useEffect(() => {
    if (prefs) {
      setEmailEnabled(prefs.email_enabled);
      setInAppEnabled(prefs.in_app_enabled);
      setDigestEnabled(prefs.digest_enabled);
    }
  }, [prefs]);

  const handleSavePrefs = () => {
    updatePrefs({ 
      email_enabled: emailEnabled, 
      in_app_enabled: inAppEnabled, 
      digest_enabled: digestEnabled 
    });
  };

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Notification Center</h2>
        <p className="text-muted-foreground mt-1">
          View your alerts and manage how SupportGPT communicates with you.
        </p>
      </div>

      <Tabs defaultValue="inbox" className="w-full">
        <TabsList>
          <TabsTrigger value="inbox" className="gap-2"><Inbox className="w-4 h-4" /> Inbox</TabsTrigger>
          <TabsTrigger value="preferences" className="gap-2"><Bell className="w-4 h-4" /> Preferences</TabsTrigger>
        </TabsList>

        <TabsContent value="inbox" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row justify-between items-center pb-4">
              <div>
                <CardTitle>Unread Alerts</CardTitle>
                <CardDescription>Recent events that require your attention.</CardDescription>
              </div>
              <Button variant="outline" size="sm" className="gap-2">
                <CheckCheck className="w-4 h-4" /> Mark All Read
              </Button>
            </CardHeader>
            <CardContent>
              {loadingNotifs ? (
                <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
              ) : !notifications || notifications.length === 0 ? (
                <div className="text-center p-12 text-muted-foreground border border-dashed rounded-md">
                  <Bell className="w-8 h-8 mx-auto mb-3 opacity-20" />
                  <p>You're all caught up!</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {notifications.map(n => (
                    <div key={n.id} className="p-4 border rounded-md flex justify-between items-start bg-muted/20">
                      <div>
                        <h4 className="font-semibold text-sm">{n.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{n.message}</p>
                        <span className="text-xs text-muted-foreground mt-2 block">{new Date(n.created_at).toLocaleString()}</span>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => markRead(n.id)}>Dismiss</Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Delivery Methods</CardTitle>
              <CardDescription>Choose how you want to receive alerts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {loadingPrefs ? (
                <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
              ) : (
                <>
                  <div className="flex justify-between items-center">
                    <div>
                      <Label className="text-base font-semibold">In-App Notifications</Label>
                      <p className="text-sm text-muted-foreground">Show a badge and popup when you are using the app.</p>
                    </div>
                    <Switch checked={inAppEnabled} onCheckedChange={setInAppEnabled} />
                  </div>
                  <Separator />
                  <div className="flex justify-between items-center">
                    <div>
                      <Label className="text-base font-semibold">Email Alerts</Label>
                      <p className="text-sm text-muted-foreground">Send an email for critical system events.</p>
                    </div>
                    <Switch checked={emailEnabled} onCheckedChange={setEmailEnabled} />
                  </div>
                  <Separator />
                  <div className="flex justify-between items-center">
                    <div>
                      <Label className="text-base font-semibold">Daily Digest</Label>
                      <p className="text-sm text-muted-foreground">Receive a summary email of all activity every morning.</p>
                    </div>
                    <Switch checked={digestEnabled} onCheckedChange={setDigestEnabled} />
                  </div>
                </>
              )}
            </CardContent>
            <CardFooter className="border-t px-6 py-4 flex justify-end">
              <Button onClick={handleSavePrefs} disabled={updating || loadingPrefs}>
                {updating && <Loader2 className="w-4 h-4 mr-2 animate-spin" />} Save Preferences
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
