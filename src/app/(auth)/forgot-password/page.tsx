"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { authService } from "@/lib/api/auth";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Loader2, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

const formSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
});

export default function ForgotPasswordPage() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (cooldown > 0) {
      timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [cooldown]);

  const resetMutation = useMutation({
    mutationFn: authService.forgotPassword,
    onSuccess: () => {
      setIsSubmitted(true);
      setCooldown(60); // 60 seconds cooldown
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to send reset link");
    },
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    resetMutation.mutate(values.email);
  }

  if (isSubmitted) {
    return (
      <div className="flex flex-col gap-6 items-center text-center">
        <CheckCircle2 className="h-12 w-12 text-primary mb-2" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Check your email</h1>
          <p className="text-muted-foreground text-sm">
            We sent a password reset link to <span className="font-medium text-foreground">{form.getValues("email")}</span>
          </p>
        </div>
        <div className="w-full mt-4 space-y-4">
          <Button 
            variant="outline" 
            className="w-full" 
            disabled={cooldown > 0 || resetMutation.isPending}
            onClick={() => onSubmit(form.getValues())}
          >
            {resetMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {cooldown > 0 ? `Resend email in ${cooldown}s` : "Click to resend"}
          </Button>
          <Link href="/login" className="inline-block w-full">
            <Button className="w-full">Back to login</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Reset password</h1>
        <p className="text-muted-foreground text-sm">
          Enter your email address and we will send you a link to reset your password.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
               <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input placeholder="m@example.com" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={resetMutation.isPending}>
            {resetMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Send reset link"}
          </Button>
        </form>
      </Form>

      <div className="text-center text-sm text-muted-foreground">
        Remember your password?{" "}
        <Link href="/login" className="text-primary hover:underline">
          Sign in
        </Link>
      </div>
    </div>
  );
}
