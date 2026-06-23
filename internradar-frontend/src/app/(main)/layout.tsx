"use client";

import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";
import { useAppStore } from "@/store/useStore";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { usePathname } from "next/navigation";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const sidebarOpen = useAppStore((s) => s.sidebarOpen);
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-background relative overflow-x-hidden selection:bg-orange-500/20 selection:text-orange-200 pb-20 lg:pb-0">
      {/* Premium dark-mode animated background overlays */}
      <div className="fixed inset-0 -z-50 pointer-events-none overflow-hidden">
        <div className="absolute top-[20%] left-[10%] w-[350px] h-[350px] rounded-full bg-orange-600/3 blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[20%] right-[10%] w-[450px] h-[450px] rounded-full bg-amber-600/3 blur-[150px] animate-pulse-slow" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:32px_32px]" />
      </div>

      <Header />
      <Sidebar />
      <main
        className={cn(
          "pt-14 transition-all duration-300",
          sidebarOpen ? "lg:pl-64" : "lg:pl-0"
        )}
      >
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto"
        >
          {children}
        </motion.div>
      </main>
      <MobileNav />
    </div>
  );
}
