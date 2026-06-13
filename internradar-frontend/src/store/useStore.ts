import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  bookmarkedIds: Set<string>;
  theme: "dark" | "light";
  sidebarOpen: boolean;
  setBookmarkedIds: (ids: string[]) => void;
  toggleBookmark: (id: string) => void;
  isBookmarked: (id: string) => boolean;
  setTheme: (theme: "dark" | "light") => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      bookmarkedIds: new Set(),
      theme: "dark",
      sidebarOpen: true,
      setBookmarkedIds: (ids) => set({ bookmarkedIds: new Set(ids) }),
      toggleBookmark: (id) => {
        const next = new Set(get().bookmarkedIds);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        set({ bookmarkedIds: next });
      },
      isBookmarked: (id) => get().bookmarkedIds.has(id),
      setTheme: (theme) => set({ theme }),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
    }),
    {
      name: "internradar-store",
      partialize: (state) => ({
        theme: state.theme,
        bookmarkedIds: Array.from(state.bookmarkedIds),
      }),
      onRehydrateStorage: () => (state) => {
        if (state && Array.isArray((state as unknown as { bookmarkedIds: string[] }).bookmarkedIds)) {
          state.bookmarkedIds = new Set(
            (state as unknown as { bookmarkedIds: string[] }).bookmarkedIds
          );
        }
      },
    }
  )
);
