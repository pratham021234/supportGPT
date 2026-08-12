"use client";

import { useCurrentWorkspaceApi, useWorkspaces } from "@/lib/api/workspaces";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Upload } from "lucide-react";
import { useState, useEffect } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

export default function SettingsGeneralPage() {
  const { data: workspace, isLoading } = useCurrentWorkspaceApi();
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("technology");
  const [region, setRegion] = useState("us-east");

  useEffect(() => {
    if (workspace) {
      setName(workspace.name);
    }
  }, [workspace]);

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>;
  }

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">General & Branding</h2>
        <p className="text-muted-foreground mt-1">
          Manage your workspace profile, branding assets, and localization preferences.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workspace Profile</CardTitle>
          <CardDescription>Update your company information and default settings.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex gap-6 items-center">
            <div className="w-20 h-20 bg-muted rounded-md border-2 border-dashed flex items-center justify-center cursor-pointer hover:bg-muted/80 transition-colors">
              <Upload className="w-6 h-6 text-muted-foreground" />
            </div>
            <div className="space-y-1">
              <Label>Workspace Logo</Label>
              <p className="text-xs text-muted-foreground">Recommended: 256x256px PNG or SVG</p>
            </div>
          </div>
          <Separator />
          <div className="space-y-2">
            <Label htmlFor="company">Workspace Name</Label>
            <Input id="company" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Industry</Label>
              <Select value={industry} onValueChange={(val) => setIndustry(val as string)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technology">Technology & Software</SelectItem>
                  <SelectItem value="ecommerce">E-Commerce</SelectItem>
                  <SelectItem value="finance">Financial Services</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Data Region</Label>
              <Select value={region} onValueChange={(val) => setRegion(val as string)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select region" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="us-east">US East (N. Virginia)</SelectItem>
                  <SelectItem value="eu-central">EU Central (Frankfurt)</SelectItem>
                  <SelectItem value="ap-south">Asia Pacific (Mumbai)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
        <CardFooter className="border-t px-6 py-4 flex justify-end">
          <Button>Save Changes</Button>
        </CardFooter>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Branding & Theme</CardTitle>
          <CardDescription>Customize the appearance of customer-facing widgets and portals.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label>Brand Color</Label>
            <div className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-primary ring-2 ring-offset-2 ring-primary cursor-pointer"></div>
              <div className="w-10 h-10 rounded-full bg-blue-600 cursor-pointer border"></div>
              <div className="w-10 h-10 rounded-full bg-emerald-600 cursor-pointer border"></div>
              <div className="w-10 h-10 rounded-full bg-violet-600 cursor-pointer border"></div>
              <div className="w-10 h-10 rounded-full bg-rose-600 cursor-pointer border"></div>
              <div className="w-10 h-10 rounded-full bg-muted border flex items-center justify-center cursor-pointer">
                <Plus className="w-4 h-4 text-muted-foreground" />
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter className="border-t px-6 py-4 flex justify-end">
          <Button variant="outline">Save Theme</Button>
        </CardFooter>
      </Card>

      <Card className="border-destructive/20 bg-destructive/5">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>Permanently delete this workspace and all associated data.</CardDescription>
        </CardHeader>
        <CardFooter className="px-6 py-4 flex justify-start">
          <Button variant="destructive">Delete Workspace</Button>
        </CardFooter>
      </Card>
    </div>
  );
}

function Plus(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
  );
}
