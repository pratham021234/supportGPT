import { AlertCircle, Lock, UserX, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

interface AuthErrorProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  actionText?: string;
  actionHref?: string;
}

export function AuthError({
  title,
  description,
  icon = <AlertCircle className="h-12 w-12 text-destructive" />,
  actionText = "Back to Login",
  actionHref = "/login"
}: AuthErrorProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="mx-auto max-w-md text-center border-dashed">
        <CardHeader>
          <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-muted">
            {icon}
          </div>
          <CardTitle className="text-2xl">{title}</CardTitle>
          <CardDescription className="text-base">{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            If you believe this is an error, please contact support or try logging in again.
          </p>
        </CardContent>
        <CardFooter className="flex justify-center">
          <Button asChild className="w-full sm:w-auto">
            <Link href={actionHref}>{actionText}</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

export function SessionExpired() {
  return (
    <AuthError
      title="Session Expired"
      description="Your session has expired due to inactivity. Please log in again to continue."
      icon={<Clock className="h-12 w-12 text-amber-500" />}
    />
  );
}

export function Unauthorized() {
  return (
    <AuthError
      title="Unauthorized Access"
      description="You need to be logged in to access this page."
      icon={<UserX className="h-12 w-12 text-destructive" />}
    />
  );
}

export function AccessDenied() {
  return (
    <AuthError
      title="Access Denied"
      description="You do not have the required permissions to view this resource."
      icon={<Lock className="h-12 w-12 text-destructive" />}
      actionText="Go to Dashboard"
      actionHref="/dashboard"
    />
  );
}
