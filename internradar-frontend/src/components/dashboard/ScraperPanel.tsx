"use client";

import { useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import {
  RefreshCw, CheckCircle2, AlertCircle, Loader2,
  Zap, ChevronDown, ChevronUp, Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow, parseISO } from "date-fns";

interface ConnectorResult {
  connector: string;
  fetched: number;
  inserted: number;
  status: "done" | "error";
  error?: string;
}

interface ScraperStatus {
  is_running: boolean;
  last_run_at: string | null;
  last_fetched: number;
  last_inserted: number;
  current_connector: string | null;
  progress: ConnectorResult[];
  error: string | null;
}

const CONNECTOR_ORDER = ["Greenhouse", "Lever", "Ashby", "Workday", "SmartRecruiters", "ManualSource"];

async function fetchStatus(): Promise<ScraperStatus> {
  const r = await axios.get<ScraperStatus>("/backend/api/scraper/status");
  return r.data;
}

async function triggerScrape(): Promise<void> {
  await axios.post("/backend/api/scraper/trigger");
}

function ConnectorRow({ name, result, isCurrent }: {
  name: string;
  result?: ConnectorResult;
  isCurrent: boolean;
}) {
  return (
    <div className={cn(
      "flex items-center justify-between py-2 px-3 rounded-lg text-sm transition-all",
      isCurrent && "bg-indigo-500/10 border border-indigo-500/20",
      result?.status === "done" && "opacity-70",
      result?.status === "error" && "bg-red-500/5",
    )}>
      <div className="flex items-center gap-2">
        {isCurrent ? (
          <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin shrink-0" />
        ) : result?.status === "done" ? (
          <CheckCircle2 className="w-3.5 h-3.5 text-green-400 shrink-0" />
        ) : result?.status === "error" ? (
          <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
        ) : (
          <div className="w-3.5 h-3.5 rounded-full border border-white/20 shrink-0" />
        )}
        <span className={cn(
          isCurrent ? "text-indigo-300 font-medium" : "text-muted-foreground",
          result ? "text-foreground" : "",
        )}>
          {name}
        </span>
      </div>
      {result && result.status === "done" && (
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>{result.fetched} fetched</span>
          {result.inserted > 0 && (
            <span className="text-green-400 font-medium">+{result.inserted} new</span>
          )}
        </div>
      )}
      {result?.status === "error" && (
        <span className="text-xs text-red-400">Failed</span>
      )}
      {isCurrent && (
        <span className="text-xs text-indigo-400 animate-pulse">Running…</span>
      )}
    </div>
  );
}

export function ScraperPanel() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<ScraperStatus | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [justFinished, setJustFinished] = useState(false);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;

    const poll = async () => {
      try {
        const s = await fetchStatus();
        setStatus((prev) => {
          if (prev?.is_running && !s.is_running) setJustFinished(true);
          return s;
        });
        if (!s.is_running) {
          if (interval) clearInterval(interval);
          interval = null;
          queryClient.invalidateQueries({ queryKey: ["stats"] });
          queryClient.invalidateQueries({ queryKey: ["internships"] });
        }
      } catch {
        // ignore
      }
    };

    poll();
    interval = setInterval(poll, 2000);

    return () => { if (interval) clearInterval(interval); };
  }, [queryClient]);

  useEffect(() => {
    if (status?.is_running) {
      setExpanded(true);
      setJustFinished(false);
    }
  }, [status?.is_running]);

  useEffect(() => {
    if (justFinished) {
      setExpanded(true);
      const t = setTimeout(() => setJustFinished(false), 8000);
      return () => clearTimeout(t);
    }
  }, [justFinished]);

  const handleTrigger = async () => {
    setError(null);
    setTriggering(true);
    setExpanded(true);
    try {
      await triggerScrape();
      // Poll kicks in from useEffect interval
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Failed to trigger scraper");
    } finally {
      setTriggering(false);
    }
  };

  const isRunning = status?.is_running ?? false;
  const progressMap = new Map(status?.progress?.map((p) => [p.connector, p]) ?? []);

  const completedConnectors = new Set(status?.progress?.map((p) => p.connector) ?? []);
  const currentIdx = status?.current_connector
    ? CONNECTOR_ORDER.indexOf(status.current_connector)
    : -1;

  const totalNew = status?.last_inserted ?? 0;
  const lastRun = status?.last_run_at
    ? formatDistanceToNow(parseISO(status.last_run_at), { addSuffix: true })
    : null;

  return (
    <div className="bg-card border border-border/50 rounded-xl overflow-hidden">
      {/* Header row */}
      <div className="flex items-center justify-between px-5 py-4">
        <div className="flex items-center gap-2.5">
          <div className={cn(
            "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
            isRunning ? "bg-indigo-600/20" : "bg-muted/50"
          )}>
            {isRunning ? (
              <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
            ) : justFinished ? (
              <CheckCircle2 className="w-4 h-4 text-green-400" />
            ) : (
              <RefreshCw className="w-4 h-4 text-muted-foreground" />
            )}
          </div>
          <div>
            <div className="text-sm font-semibold">
              {isRunning
                ? "Scraping in progress…"
                : justFinished
                  ? `Done — ${totalNew} new internship${totalNew !== 1 ? "s" : ""} found`
                  : "Manual Scrape"}
            </div>
            {lastRun && !isRunning && (
              <div className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="w-3 h-3" /> Last run {lastRun}
              </div>
            )}
            {isRunning && status?.current_connector && (
              <div className="text-xs text-indigo-400 animate-pulse">
                Scanning {status.current_connector}…
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {(isRunning || status?.progress?.length) ? (
            <button
              onClick={() => setExpanded((p) => !p)}
              className="p-1.5 rounded-md hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          ) : null}
          <button
            onClick={handleTrigger}
            disabled={isRunning || triggering}
            className={cn(
              "flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all",
              isRunning || triggering
                ? "bg-muted/50 text-muted-foreground cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm hover:shadow-indigo-500/20 hover:shadow-lg"
            )}
          >
            {triggering ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Zap className="w-3.5 h-3.5" />
            )}
            {isRunning ? "Running…" : "Refresh Now"}
          </button>
        </div>
      </div>

      {/* Progress panel */}
      <AnimatePresence>
        {expanded && (isRunning || (status?.progress?.length ?? 0) > 0) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border/50 px-5 py-3 space-y-1">
              {CONNECTOR_ORDER.map((name) => {
                const shortName = name === "ManualSource" ? "ManualSource" : name;
                const result = progressMap.get(shortName);
                const isCurrent = status?.current_connector === shortName && isRunning;
                return (
                  <ConnectorRow
                    key={name}
                    name={shortName}
                    result={result}
                    isCurrent={isCurrent}
                  />
                );
              })}

              {/* Summary */}
              {!isRunning && status?.progress?.length && (
                <div className="mt-3 pt-3 border-t border-border/50 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{status.last_fetched} total listings checked</span>
                  <span className={cn(totalNew > 0 ? "text-green-400 font-semibold" : "")}>
                    {totalNew > 0 ? `+${totalNew} added to database` : "No new listings found"}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 mx-5 mb-3 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs"
          >
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
