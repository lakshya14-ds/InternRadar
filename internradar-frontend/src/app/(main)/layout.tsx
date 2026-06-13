"use client";

import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { useAppStore } from "@/store/useStore";
import { cn } from "@/lib/utils";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const sidebarOpen = useAppStore((s) => s.sidebarOpen);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Sidebar />
      <main
        className={cn(
          "pt-14 transition-all duration-300",
          sidebarOpen ? "lg:pl-56" : "lg:pl-0"
        )}
      >
        <div className="p-4 md:p-6 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
}
