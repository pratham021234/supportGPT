import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { OverviewCharts } from "@/components/dashboard/overview-charts";

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Deep dive into your support performance and AI metrics.
          </p>
        </div>
      </div>

      <OverviewCharts />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Top Questions</CardTitle>
            <CardDescription>Most frequently asked topics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { topic: "Password Reset", count: 124 },
                { topic: "Billing & Invoices", count: 85 },
                { topic: "API Rate Limits", count: 62 },
                { topic: "Team Invites", count: 41 },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.topic}</span>
                  <span className="text-sm text-muted-foreground">{item.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Knowledge Gaps</CardTitle>
            <CardDescription>Topics where AI confidence is low</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { topic: "Enterprise SSO Setup", count: 18 },
                { topic: "Custom Webhooks", count: 14 },
                { topic: "Legacy API v1", count: 9 },
                { topic: "Data Export format", count: 5 },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.topic}</span>
                  <span className="text-sm text-destructive">{item.count} escalated</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Most Referenced Documents</CardTitle>
            <CardDescription>Knowledge base usage</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: "Getting Started Guide", uses: 452 },
                { name: "API Documentation", uses: 312 },
                { name: "Pricing FAQs", uses: 189 },
                { name: "Security Whitepaper", uses: 64 },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate max-w-[150px]">{item.name}</span>
                  <span className="text-sm text-muted-foreground">{item.uses} refs</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
