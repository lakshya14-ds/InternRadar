import type { NextConfig } from "next";

const devOrigins = [
  "*.pike.replit.dev",
  "*.replit.dev",
  "*.repl.co",
  "localhost:5000",
];

const nextConfig: NextConfig = {
  allowedDevOrigins: devOrigins,
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
