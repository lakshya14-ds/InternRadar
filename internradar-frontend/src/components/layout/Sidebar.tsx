"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import {
  LayoutDashboard, Search, Bookmark, User, Settings,
  Briefcase, TrendingUp, Zap, Palette, BarChart2, Shield, Cloud, Megaphone, Sparkles
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/useStore";
import { motion } from "framer-motion";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/internships", label: "Browse Roles", icon: Search },
  { href: "/saved", label: "Bookmarks", icon: Bookmark },
  { href: "/profile", label: "My Profile", icon: User },
];

const CATEGORIES_NAV = [
  { href: "/internships?category=Software+Engineering", label: "Software Engineering", icon: Zap },
  { href: "/internships?category=AI", label: "AI & Deep Tech", icon: Sparkles },
  { href: "/internships?category=Data+Science", label: "Data Science", icon: TrendingUp },
  { href: "/internships?category=Machine+Learning", label: "Machine Learning", icon: Briefcase },
  { href: "/internships?category=UI%2FUX", label: "UI/UX Design", icon: Palette },
  { href: "/internships?category=Product", label: "Product Management", icon: Settings },
  { href: "/internships?category=Data+Analytics", label: "Data Analytics", icon: BarChart2 },
  { href: "/internships?category=Cybersecurity", label: "Cybersecurity", icon: Shield },
  { href: "/internships?category=Cloud+%26+DevOps", label: "Cloud & DevOps", icon: Cloud },
  { href: "/internships?category=Marketing", label: "Growth Marketing", icon: Megaphone },
];

export function Sidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { sidebarOpen } = useAppStore();

  const currentCategory = searchParams.get("category");

  return (
    <aside
      className={cn(
        "fixed left-4 top-[4.5rem] bottom-4 z-30 flex flex-col rounded-2xl border bg-[#050308]/60 backdrop-blur-md transition-all duration-300 overflow-hidden",
        sidebarOpen ? "w-56 border-white/5 opacity-100 shadow-2xl shadow-orange-950/5" : "w-0 border-transparent opacity-0 pointer-events-none"
      )}
    >
      <div className="flex-1 overflow-y-auto py-5 px-3 space-y-6 hide-scrollbar">
        <div>
          <p className="text-[9px] font-bold text-muted-foreground/40 uppercase tracking-widest px-3 mb-2">Core Menu</p>
          <nav className="space-y-1 relative">
            {NAV.map((item) => {
              const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href) && !currentCategory);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200",
                    active
                      ? "text-orange-300 font-bold"
                      : "text-muted-foreground hover:text-foreground hover:bg-white/[0.02]"
                  )}
                >
                  {active && (
                    <motion.div
                      layoutId="activeSidebarGlow"
                      className="absolute inset-0 bg-gradient-to-r from-orange-500/10 to-transparent border-l-2 border-orange-500 rounded-xl"
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}
                  <item.icon className={cn("w-4 h-4 shrink-0 relative z-10 transition-transform duration-200 group-hover:scale-110", active ? "text-orange-400" : "text-muted-foreground group-hover:text-foreground")} />
                  <span className="truncate relative z-10">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div>
          <p className="text-[9px] font-bold text-muted-foreground/40 uppercase tracking-widest px-3 mb-2">Verticals</p>
          <nav className="space-y-0.5">
            {CATEGORIES_NAV.map((item) => {
              const categoryParam = item.href.split("category=")[1];
              const active = pathname === "/internships" && categoryParam && currentCategory === decodeURIComponent(categoryParam);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group relative flex items-center gap-3 px-3 py-2 rounded-xl text-[11px] font-semibold tracking-wide transition-all duration-150",
                    active
                      ? "text-orange-300 font-bold"
                      : "text-muted-foreground hover:text-foreground hover:bg-white/[0.01]"
                  )}
                >
                  {active && (
                    <motion.div
                      layoutId="activeCategoryGlow"
                      className="absolute inset-0 bg-gradient-to-r from-orange-500/5 to-transparent border-l border-orange-500/60 rounded-xl"
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}
                  <item.icon className={cn("w-3.5 h-3.5 shrink-0 relative z-10 transition-transform duration-200 group-hover:scale-110", active ? "text-orange-400" : "text-muted-foreground group-hover:text-foreground")} />
                  <span className="truncate relative z-10">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </aside>
  );
}
