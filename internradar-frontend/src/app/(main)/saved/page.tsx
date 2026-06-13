"use client";

import { useSession } from "next-auth/react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Bookmark, Search } from "lucide-react";
import Link from "next/link";
import { usersApi } from "@/lib/api";
import { InternshipCard } from "@/components/internships/InternshipCard";

export default function SavedPage() {
  const { data: session } = useSession();

  const { data: saved, isLoading } = useQuery({
    queryKey: ["bookmarks", session?.accessToken],
    queryFn: () => usersApi.bookmarks(session!.accessToken!),
    enabled: !!session?.accessToken,
  });

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-muted-foreground">
        <Bookmark className="w-12 h-12 mb-3 opacity-20" />
        <p className="font-medium mb-1">Sign in to see saved internships</p>
        <Link href="/login" className="mt-3 text-sm text-indigo-400 hover:text-indigo-300">Sign In</Link>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold mb-0.5">Saved Internships</h1>
        <p className="text-muted-foreground text-sm">
          {saved?.length !== undefined ? `${saved.length} saved` : "Loading..."}
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-card border border-border/50 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : !saved?.length ? (
        <div className="flex flex-col items-center justify-center py-24 text-muted-foreground bg-card border border-border/50 rounded-xl">
          <Bookmark className="w-12 h-12 mb-3 opacity-20" />
          <p className="font-medium mb-1">No saved internships yet</p>
          <p className="text-sm mb-4">Browse internships and bookmark the ones you like</p>
          <Link href="/internships" className="flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300 font-medium">
            <Search className="w-4 h-4" /> Browse Internships
          </Link>
        </div>
      ) : (
        <motion.div layout className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {saved.map((internship, i) => (
            <motion.div key={internship._id || internship.external_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
              <InternshipCard internship={internship} />
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
