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

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  allowedDevOrigins: devOrigins,
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
