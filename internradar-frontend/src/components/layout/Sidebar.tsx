"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import {
  LayoutDashboard, Search, Bookmark, User, Settings,
  Briefcase, TrendingUp, Zap, Palette, BarChart2, Shield, Cloud, Megaphone
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/useStore";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/internships", label: "Internships", icon: Search },
  { href: "/saved", label: "Saved", icon: Bookmark },
  { href: "/profile", label: "Profile", icon: User },
];

const CATEGORIES_NAV = [
  { href: "/internships?category=Software+Engineering", label: "Software Engineering", icon: Zap },
  { href: "/internships?category=Data+Science", label: "Data Science", icon: TrendingUp },
  { href: "/internships?category=Machine+Learning", label: "Machine Learning", icon: Briefcase },
  { href: "/internships?category=UI%2FUX", label: "UI/UX", icon: Palette },
  { href: "/internships?category=Product", label: "Product", icon: Settings },
  { href: "/internships?category=Data+Analytics", label: "Data Analytics", icon: BarChart2 },
  { href: "/internships?category=Cybersecurity", label: "Cybersecurity", icon: Shield },
  { href: "/internships?category=Cloud+%26+DevOps", label: "Cloud & DevOps", icon: Cloud },
  { href: "/internships?category=Marketing", label: "Marketing", icon: Megaphone },
];

export function Sidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { sidebarOpen } = useAppStore();

  const currentCategory = searchParams.get("category");

  return (
    <aside
      className={cn(
        "fixed left-4 top-[4.5rem] bottom-4 z-30 flex flex-col rounded-2xl border border-white/5 bg-[#080214]/65 backdrop-blur-xl shadow-2xl shadow-indigo-950/20 transition-all duration-300 overflow-hidden",
        sidebarOpen ? "w-56" : "w-0 border-0 opacity-0 pointer-events-none"
      )}
    >
      <div className="flex-1 overflow-y-auto py-5 px-4 space-y-6">
        <div>
          <p className="text-[10px] font-bold text-muted-foreground/60 uppercase tracking-widest px-3 mb-2.5">Menu</p>
          <nav className="space-y-1">
            {NAV.map((item) => {
              const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href) && !currentCategory);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 border",
                    active
                      ? "bg-gradient-to-r from-orange-500/10 to-amber-500/5 text-orange-300 border-orange-500/20 shadow-lg shadow-orange-500/5"
                      : "text-muted-foreground border-transparent hover:text-foreground hover:bg-white/5"
                  )}
                >
                  {active && (
                    <span className="absolute left-0 w-1 h-5 rounded-r bg-orange-500" />
                  )}
                  <item.icon className={cn("w-4 h-4 shrink-0 transition-transform duration-200 group-hover:scale-110", active ? "text-orange-400" : "text-muted-foreground group-hover:text-foreground")} />
                  <span className="truncate">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div>
          <p className="text-[10px] font-bold text-muted-foreground/60 uppercase tracking-widest px-3 mb-2.5">Quick Filters</p>
          <nav className="space-y-1">
            {CATEGORIES_NAV.map((item) => {
              const categoryParam = item.href.split("category=")[1];
              const active = pathname === "/internships" && categoryParam && currentCategory === decodeURIComponent(categoryParam);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group relative flex items-center gap-3 px-3 py-2 rounded-xl text-[11px] font-semibold tracking-wide transition-all duration-200 border",
                    active
                      ? "bg-gradient-to-r from-orange-500/10 to-amber-500/5 text-orange-300 border-orange-500/20 shadow-lg shadow-orange-500/5"
                      : "text-muted-foreground border-transparent hover:text-foreground hover:bg-white/5"
                  )}
                >
                  {active && (
                    <span className="absolute left-0 w-0.5 h-4 rounded-r bg-orange-500" />
                  )}
                  <item.icon className={cn("w-3.5 h-3.5 shrink-0 transition-transform duration-200 group-hover:scale-110", active ? "text-orange-400" : "text-muted-foreground group-hover:text-foreground")} />
                  <span className="truncate">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </aside>
  );
}
