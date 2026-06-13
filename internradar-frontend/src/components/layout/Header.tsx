"use client";

import Link from "next/link";
import { useSession, signOut } from "next-auth/react";
import { Briefcase, Bell, LogOut, User, Menu, Moon, Sun, Search } from "lucide-react";
import { useAppStore } from "@/store/useStore";
import { useState } from "react";

export function Header() {
  const { data: session } = useSession();
  const { theme, setTheme, setSidebarOpen, sidebarOpen } = useAppStore();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-40 flex items-center h-14 px-4 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="p-1.5 rounded-md hover:bg-accent transition-colors mr-3 lg:hidden"
      >
        <Menu className="w-4 h-4" />
      </button>

      <Link href="/dashboard" className="flex items-center gap-2 mr-6">
        <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
          <Briefcase className="w-3.5 h-3.5 text-white" />
        </div>
        <span className="font-bold text-sm hidden sm:block">InternRadar</span>
      </Link>

      <div className="flex-1 max-w-md hidden md:block">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search internships..."
            className="w-full pl-9 pr-4 py-1.5 text-sm bg-muted/50 border border-border/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring/50 placeholder:text-muted-foreground"
            onFocus={() => {
              window.location.href = "/internships";
            }}
          />
        </div>
      </div>

      <div className="flex items-center gap-2 ml-auto">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-1.5 rounded-md hover:bg-accent transition-colors"
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {session ? (
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-accent transition-colors"
            >
              <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white">
                {session.user?.name?.[0]?.toUpperCase() || "U"}
              </div>
              <span className="text-sm font-medium hidden sm:block">{session.user?.name?.split(" ")[0]}</span>
            </button>
            {userMenuOpen && (
              <div className="absolute right-0 top-full mt-1 w-48 bg-card border border-border rounded-xl shadow-xl py-1 z-50">
                <Link href="/profile" className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors" onClick={() => setUserMenuOpen(false)}>
                  <User className="w-4 h-4 text-muted-foreground" /> Profile
                </Link>
                <Link href="/profile#alerts" className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors" onClick={() => setUserMenuOpen(false)}>
                  <Bell className="w-4 h-4 text-muted-foreground" /> Email Alerts
                </Link>
                <div className="border-t border-border my-1" />
                <button
                  onClick={() => { setUserMenuOpen(false); signOut({ callbackUrl: "/" }); }}
                  className="flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-accent transition-colors w-full text-left"
                >
                  <LogOut className="w-4 h-4" /> Sign Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link href="/login" className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg transition-colors font-medium">
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
}
