"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Compass, Search } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#040108] text-white flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Floating abstract glowing blobs */}
      <div className="absolute top-[30%] left-[20%] w-[350px] h-[350px] rounded-full bg-orange-600/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[30%] right-[20%] w-[350px] h-[350px] rounded-full bg-amber-600/5 blur-[120px] pointer-events-none" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />

      <div className="relative text-center max-w-md mx-auto space-y-6 z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="relative inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-orange-500/10 border border-orange-500/20 text-orange-400 mb-2 shadow-lg shadow-orange-500/10"
        >
          <Compass className="w-10 h-10 animate-pulse-slow" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="space-y-2"
        >
          <h1 className="text-7xl font-black font-mono tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-400 to-yellow-300">
            404
          </h1>
          <h2 className="text-lg font-extrabold uppercase tracking-wider text-white">
            Lost in the Curation Pipeline?
          </h2>
          <p className="text-xs text-muted-foreground/80 leading-relaxed font-semibold max-w-sm mx-auto">
            The internship listing or configuration pathway you are looking for has either expired, been relocated, or is currently being crawled.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4"
        >
          <Link
            href="/"
            className="flex items-center justify-center gap-1.5 w-full sm:w-auto px-5 py-2.5 rounded-xl text-xs font-bold bg-white/5 border border-white/5 text-gray-200 hover:text-white hover:bg-white/10 transition-all focus:outline-none"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Return Home
          </Link>
          <Link
            href="/internships"
            className="flex items-center justify-center gap-1.5 w-full sm:w-auto px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white shadow-lg shadow-orange-500/25 transition-all focus:outline-none"
          >
            <Search className="w-3.5 h-3.5" /> Browse Internships
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
