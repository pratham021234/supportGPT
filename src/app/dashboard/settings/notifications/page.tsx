"use client";

import { useAuth } from "@/store/use-auth";
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotificationPreferencesPage() {
    const { user } = useAuth();
    const [prefs, setPrefs] = useState({
        email_enabled: true,
        in_app_enabled: true,
        digest_enabled: false
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const load = async () => {
            if (!user) return;
            const res = await fetch("/api/v1/notifications/preferences", {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setPrefs(data);
            }
            setLoading(false);
        };
        load();
    }, [user]);

    const handleSave = async () => {
        if (!user) return;
        setSaving(true);
        await fetch("/api/v1/notifications/preferences", {
            method: "PATCH",
            headers: { 
                "Content-Type": "application/json",
                Authorization: `Bearer ${user.token}` 
            },
            body: JSON.stringify(prefs)
        });
        setSaving(false);
    };

    if (loading) return <div className="p-8">Loading preferences...</div>;

    return (
        <div className="flex flex-col gap-6 p-8 max-w-2xl">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Notification Preferences</h1>
                <p className="text-zinc-500 mt-1">Control how you receive alerts and summaries.</p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Delivery Channels</CardTitle>
                    <CardDescription>Select where you want to receive your notifications.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                            <Label>In-App Notifications</Label>
                            <p className="text-sm text-zinc-500">Receive alerts inside the dashboard bell icon.</p>
                        </div>
                        <Switch 
                            checked={prefs.in_app_enabled} 
                            onCheckedChange={c => setPrefs({...prefs, in_app_enabled: c})} 
                        />
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                            <Label>Email Notifications</Label>
                            <p className="text-sm text-zinc-500">Receive critical alerts directly to your inbox.</p>
                        </div>
                        <Switch 
                            checked={prefs.email_enabled} 
                            onCheckedChange={c => setPrefs({...prefs, email_enabled: c})} 
                        />
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                            <Label>Weekly Digests</Label>
                            <p className="text-sm text-zinc-500">Receive a weekly summary report of your workspace.</p>
                        </div>
                        <Switch 
                            checked={prefs.digest_enabled} 
                            onCheckedChange={c => setPrefs({...prefs, digest_enabled: c})} 
                        />
                    </div>
                </CardContent>
                <CardFooter className="border-t pt-4">
                    <Button onClick={handleSave} disabled={saving}>
                        {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : "Save Preferences"}
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
