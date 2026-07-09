import type { NextConfig } from "next";

const devOrigins = [
  "*.pike.replit.dev",
  "*.replit.dev",
  "*.repl.co",
  "localhost:5000",
  "*.loca.lt",
  "tasty-papers-greet.loca.lt",
  "internradar-dev.loca.lt",
];

const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL;

const nextConfig: NextConfig = {
  allowedDevOrigins: devOrigins,
  async rewrites() {
    if (!backendUrl && process.env.NODE_ENV === "production") {
      return [];
    }
    const dest = backendUrl || "http://localhost:8000";
    return [
      {
        source: "/backend/:path*",
        destination: `${dest}/:path*`,
      },
    ];
  },
};

export default nextConfig;
