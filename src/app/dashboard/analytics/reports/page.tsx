"use client";

import { useState } from "react";
import { analyticsService } from "@/lib/api/analytics";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download, Loader2, Save, Calendar, FileSpreadsheet } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export default function ReportsPage() {
  const [metric, setMetric] = useState("TICKETS");
  const [format, setFormat] = useState("CSV");
  const [isExporting, setIsExporting] = useState(false);
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const blob = await analyticsService.exportReport(metric, format);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `${metric.toLowerCase()}_export.${format.toLowerCase()}`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("Export successful");
    } catch (e) {
      toast.error("Export failed");
    } finally {
      setIsExporting(false);
    }
  };

  const handleSchedule = () => {
    setIsScheduleOpen(false);
    toast.success("Report scheduled successfully. Check your email inbox.");
  };

  return (
    <div className="flex flex-col gap-6 w-full pt-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-semibold">Custom Reports & Exports</h2>
          <p className="text-sm text-muted-foreground">Build, export, and schedule custom data reports.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Report Builder</CardTitle>
            <CardDescription>Configure data exports for external analysis</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Select Metric / Data Source</Label>
              <Select value={metric} onValueChange={(val) => setMetric(val as string)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="TICKETS">Tickets & Resolutions</SelectItem>
                  <SelectItem value="KNOWLEDGE_GAPS">Knowledge Gaps</SelectItem>
                  <SelectItem value="AI_PERFORMANCE">AI Performance Logs</SelectItem>
                  <SelectItem value="CSAT">Customer Satisfaction Scores</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Export Format</Label>
              <Select value={format} onValueChange={(val) => setFormat(val as string)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CSV">CSV Spreadsheet (.csv)</SelectItem>
                  <SelectItem value="XLSX">Excel Workbook (.xlsx)</SelectItem>
                  <SelectItem value="PDF">PDF Document (.pdf)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between border-t p-6">
            <Dialog open={isScheduleOpen} onOpenChange={setIsScheduleOpen}>
              <DialogTrigger render={
                <Button variant="outline">
                  <Calendar className="mr-2 h-4 w-4" /> Schedule
                </Button>
              } />
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Schedule Report Delivery</DialogTitle>
                  <DialogDescription>Automatically send this report to your email on a recurring basis.</DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>Frequency</Label>
                    <Select defaultValue="weekly">
                      <SelectTrigger><SelectValue/></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsScheduleOpen(false)}>Cancel</Button>
                  <Button onClick={handleSchedule}>Save Schedule</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Button onClick={handleExport} disabled={isExporting}>
              {isExporting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileSpreadsheet className="mr-2 h-4 w-4" />}
              Generate Export
            </Button>
          </CardFooter>
        </Card>

        <Card className="bg-muted/30 border-dashed">
          <CardContent className="flex flex-col items-center justify-center h-full text-center p-8 space-y-4">
            <div className="p-4 rounded-full bg-background border">
              <Save className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Saved Reports</h3>
              <p className="text-sm text-muted-foreground mt-1 max-w-sm">
                You haven't saved any custom report configurations yet. Create a report and save it to access it quickly later.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
