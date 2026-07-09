import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";
import crypto from "crypto";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getDeterministicPassword(googleId: string): string {
  const secret = process.env.NEXTAUTH_SECRET || "internradar-secret-dev";
  return crypto.createHmac("sha256", secret).update(googleId).digest("hex");
}

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET || "internradar-secret-dev",
  session: { strategy: "jwt", maxAge: 30 * 24 * 60 * 60 },
  pages: { signIn: "/login" },
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "dummy-google-client-id",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "dummy-google-client-secret",
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;
        try {
          const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
              name: "",
            }),
          });
          if (!res.ok) return null;
          const data = await res.json();
          return {
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            accessToken: data.access_token,
          };
        } catch {
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
        if (account?.provider === "google") {
          const email = user.email!;
          const name = user.name || "";
          const deterministicPassword = getDeterministicPassword(user.id);
          try {
            // 1. Try to login
            const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email, password: deterministicPassword }),
            });
            if (!res.ok) {
              // 2. If login fails, register the user
              const regRes = await fetch(`${BACKEND_URL}/api/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  email,
                  name,
                  password: deterministicPassword,
                  preferences: {
                    preferred_categories: [],
                    preferred_locations: [],
                    preferred_companies: [],
                    remote_only: false,
                    email_alerts_enabled: true,
                  },
                }),
              });
              if (regRes.ok) {
                const regData = await regRes.json();
                token.accessToken = regData.access_token;
                token.id = regData.user.id;
              }
            } else {
              const data = await res.json();
              token.accessToken = data.access_token;
              token.id = data.user.id;
            }
          } catch (err) {
            console.error("Google authentication synchronization failed:", err);
          }
        } else {
          token.accessToken = (user as { accessToken?: string }).accessToken;
        }
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string | undefined;
      if (session.user) {
        (session.user as { id?: string }).id = token.id as string;
      }
      return session;
    },
  },
};
