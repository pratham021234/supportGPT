"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { CheckCircle2, Loader2, Building2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export default function ContactSalesPage() {
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
    }, 1000);
  };

  return (
    <div className="pb-24 pt-12">
      <div className="container px-4 md:px-6">
        <div className="grid lg:grid-cols-2 gap-16 max-w-6xl mx-auto">
          
          {/* Left: Info */}
          <div className="flex flex-col justify-center">
            <div className="inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium mb-6 bg-background shadow-sm w-fit">
              <Building2 className="w-4 h-4 text-primary mr-2" />
              Enterprise Solutions
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">Let's build your AI support strategy.</h1>
            <p className="text-xl text-muted-foreground mb-8">
              Get in touch with our team of experts to discuss custom integrations, volume pricing, and security requirements.
            </p>
            
            <div className="space-y-6">
              <div className="flex gap-4">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 shrink-0" />
                <div>
                  <h3 className="font-bold">Custom Deployment</h3>
                  <p className="text-muted-foreground">Dedicated infrastructure and custom LLM model options available for enterprise customers.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 shrink-0" />
                <div>
                  <h3 className="font-bold">White-glove Onboarding</h3>
                  <p className="text-muted-foreground">Our customer success engineers will help migrate your knowledge base and fine-tune your initial agents.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 shrink-0" />
                <div>
                  <h3 className="font-bold">Volume Discounts</h3>
                  <p className="text-muted-foreground">Custom pricing tiers for high-volume support operations resolving &gt;50,000 queries per month.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Form */}
          <div>
            <Card className="border shadow-lg">
              <CardContent className="p-8">
                {submitted ? (
                  <div className="text-center py-16">
                    <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                      <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                    </div>
                    <h3 className="text-2xl font-bold mb-4">Request Received</h3>
                    <p className="text-muted-foreground mb-8">
                      Thank you for your interest. One of our enterprise specialists will be in touch within 24 hours.
                    </p>
                    <Button variant="outline" onClick={() => setSubmitted(false)}>Submit Another Request</Button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="first-name">First name</Label>
                        <Input id="first-name" required />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="last-name">Last name</Label>
                        <Input id="last-name" required />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Work email</Label>
                      <Input id="email" type="email" placeholder="name@company.com" required />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="company">Company name</Label>
                      <Input id="company" required />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="employees">Company size</Label>
                        <select id="employees" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" required>
                          <option value="">Select...</option>
                          <option value="1-50">1-50 employees</option>
                          <option value="51-200">51-200 employees</option>
                          <option value="201-1000">201-1000 employees</option>
                          <option value="1000+">1000+ employees</option>
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="volume">Support volume / mo</Label>
                        <select id="volume" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" required>
                          <option value="">Select...</option>
                          <option value="<10k">&lt; 10,000</option>
                          <option value="10k-50k">10,000 - 50,000</option>
                          <option value=">50k">&gt; 50,000</option>
                        </select>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="message">How can we help?</Label>
                      <Textarea id="message" className="min-h-[100px]" placeholder="Tell us about your current support stack and goals..." />
                    </div>
                    <Button type="submit" className="w-full h-12 text-md" disabled={isSubmitting}>
                      {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : null}
                      Contact Sales
                    </Button>
                    <p className="text-xs text-muted-foreground text-center">
                      By submitting this form, you agree to our Privacy Policy.
                    </p>
                  </form>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
