import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";
import { SpeedInsights } from "@vercel/speed-insights/next";

export const metadata: Metadata = {
  title: "InternRadar — Discover Internships Before Everyone Else",
  description:
    "Track internships from startups, ATS platforms, research labs and top organizations across India.",
  keywords: ["internship", "India", "jobs", "ATS", "search", "opportunities"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
        <SpeedInsights />
      </body>
    </html>
  );
}
