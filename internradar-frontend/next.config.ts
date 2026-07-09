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

function getBackendUrl(): string | null {
  const urls = [
    process.env.NEXT_PUBLIC_API_URL,
    process.env.BACKEND_URL
  ];
  for (const url of urls) {
    if (url) {
      const clean = url.trim();
      const lower = clean.toLowerCase();
      if (
        lower !== "undefined" &&
        lower !== "null" &&
        lower !== "" &&
        lower !== "backend_url" &&
        (lower.startsWith("http://") || lower.startsWith("https://") || lower.startsWith("/"))
      ) {
        return clean;
      }
    }
  }
  return null;
}

const nextConfig: NextConfig = {
  allowedDevOrigins: devOrigins,
  async rewrites() {
    const backendUrl = getBackendUrl();
    if (process.env.NODE_ENV === "production") {
      if (!backendUrl) {
        return [];
      }
      return [
        {
          source: "/backend/:path*",
          destination: `${backendUrl}/:path*`,
        },
      ];
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
