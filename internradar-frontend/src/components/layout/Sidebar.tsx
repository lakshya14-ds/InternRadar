"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Search, Bookmark, User, Settings,
  Briefcase, TrendingUp, Zap,
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
  { href: "/internships?category=Product", label: "Product", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen } = useAppStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-14 bottom-0 z-30 flex flex-col border-r border-border/50 bg-background/95 backdrop-blur-xl transition-all duration-300",
        sidebarOpen ? "w-56" : "w-0 overflow-hidden"
      )}
    >
      <div className="flex-1 overflow-y-auto py-4 px-3">
        <div className="mb-6">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 mb-2">Menu</p>
          <nav className="space-y-0.5">
            {NAV.map((item) => {
              const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 px-2 py-2 rounded-lg text-sm font-medium transition-all",
                    active
                      ? "bg-indigo-600/10 text-indigo-400 border border-indigo-500/20"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent"
                  )}
                >
                  <item.icon className="w-4 h-4 shrink-0" />
                  <span className="truncate">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 mb-2">Quick Filters</p>
          <nav className="space-y-0.5">
            {CATEGORIES_NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
              >
                <item.icon className="w-3.5 h-3.5 shrink-0" />
                <span className="truncate">{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </aside>
  );
}
