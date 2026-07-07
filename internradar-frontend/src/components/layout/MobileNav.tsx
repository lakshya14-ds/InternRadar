"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Search, Bookmark, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const MOBILE_NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/internships", label: "Browse", icon: Search },
  { href: "/saved", label: "Bookmarks", icon: Bookmark },
  { href: "/profile", label: "Profile", icon: User },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <div className="fixed bottom-5 left-4 right-4 z-40 lg:hidden">
      <div className="flex items-center justify-around h-14 rounded-2xl border border-white/5 bg-[#050308]/80 backdrop-blur-lg shadow-2xl shadow-black/80 px-2">
        {MOBILE_NAV.map((item) => {
          const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className="relative flex flex-col items-center justify-center w-12 h-12 rounded-xl transition-all duration-200"
            >
              {active && (
                <motion.div
                  layoutId="activeMobileNavGlow"
                  className="absolute inset-0 bg-orange-500/10 rounded-xl border border-orange-500/20"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              <item.icon
                className={cn(
                  "w-4 h-4 transition-transform duration-200 relative z-10",
                  active ? "text-orange-400 scale-110" : "text-muted-foreground hover:text-white"
                )}
              />
              <span
                className={cn(
                  "text-[8px] font-bold mt-1 tracking-wider uppercase relative z-10",
                  active ? "text-orange-300 font-extrabold" : "text-muted-foreground"
                )}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
