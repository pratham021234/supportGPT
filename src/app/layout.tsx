import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Providers } from "@/components/providers";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { Toaster } from "sonner";
import { GlobalErrorBoundary } from "@/components/global-error-boundary";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "SupportGPT AI - Enterprise Customer Support Automation",
    template: "%s | SupportGPT"
  },
  description: "Automate your customer support with SupportGPT AI. Powerful RAG, seamless ticketing, and deep insights.",
  openGraph: {
    title: "SupportGPT AI - Enterprise Customer Support",
    description: "Automate your customer support with highly-tuned AI.",
    url: "https://supportgpt.ai",
    siteName: "SupportGPT",
    images: [{ url: "https://supportgpt.ai/og-image.png", width: 1200, height: 630 }],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SupportGPT AI - Enterprise Customer Support",
    description: "Automate your customer support with highly-tuned AI."
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <GlobalErrorBoundary>
            <Providers>
              <AuthProvider>
                <TooltipProvider>{children}</TooltipProvider>
              </AuthProvider>
            </Providers>
          </GlobalErrorBoundary>
          <Toaster richColors position="top-right" />
        </ThemeProvider>
      </body>
    </html>
  );
}
