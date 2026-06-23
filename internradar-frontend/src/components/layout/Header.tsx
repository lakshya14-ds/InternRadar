"use client";

import Link from "next/link";
import { useSession, signOut } from "next-auth/react";
import { Bell, LogOut, User, Menu, Moon, Sun } from "lucide-react";
import { useAppStore } from "@/store/useStore";
import { useState } from "react";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { motion, AnimatePresence } from "framer-motion";

export function Header() {
  const { data: session } = useSession();
  const { theme, setTheme, setSidebarOpen, sidebarOpen } = useAppStore();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-40 flex items-center justify-between h-14 px-4 md:px-6 border-b border-white/5 bg-[#080214]/75 backdrop-blur-xl">
      <div className="flex items-center">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-1.5 rounded-lg hover:bg-white/5 text-muted-foreground hover:text-foreground transition-all mr-3 lg:hidden"
        >
          <Menu className="w-4 h-4" />
        </button>

        <Link href="/" className="flex items-center gap-2 mr-6 group">
          <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center shadow-lg shadow-orange-500/20 group-hover:scale-105 transition-transform duration-200">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <span className="font-bold text-sm bg-clip-text text-transparent bg-gradient-to-r from-orange-200 via-amber-200 to-yellow-200 hidden sm:block tracking-wide">
            InternRadar
          </span>
        </Link>

        {/* Command Palette search trigger */}
        <CommandPalette />
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-1.5 rounded-lg bg-card/40 hover:bg-card/80 border border-white/5 hover:border-white/10 text-muted-foreground hover:text-foreground transition-all duration-200"
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {session ? (
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 pl-1.5 pr-3 py-1 rounded-full bg-card/40 hover:bg-card/80 border border-white/5 hover:border-white/10 text-muted-foreground hover:text-foreground transition-all duration-200"
            >
              <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-xs font-bold text-white uppercase shadow-inner">
                {session.user?.name?.[0] || "U"}
              </div>
              <span className="text-xs font-semibold hidden sm:block">{session.user?.name?.split(" ")[0]}</span>
            </button>

            <AnimatePresence>
              {userMenuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 10 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 top-full mt-2 w-48 bg-[#09090b]/95 glass border border-white/10 rounded-xl shadow-2xl py-1.5 z-50 overflow-hidden"
                  >
                    <Link
                      href="/profile"
                      className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <User className="w-3.5 h-3.5" /> Profile
                    </Link>
                    <Link
                      href="/profile#alerts"
                      className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Bell className="w-3.5 h-3.5" /> Email Alerts
                    </Link>
                    <div className="border-t border-white/5 my-1.5" />
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        signOut({ callbackUrl: "/" });
                      }}
                      className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-red-400 hover:bg-red-500/10 transition-colors w-full text-left"
                    >
                      <LogOut className="w-3.5 h-3.5" /> Sign Out
                    </button>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        ) : (
          <Link
            href="/login"
            className="text-xs bg-orange-600 hover:bg-orange-500 hover:shadow-lg hover:shadow-orange-500/20 text-white px-4 py-2 rounded-lg transition-all duration-200 font-semibold"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
}
