"use client";

import { useState, useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import {
  RefreshCw, CheckCircle2, AlertCircle, Loader2,
  Zap, ChevronDown, ChevronUp, Clock, Server, Play, Check, Database
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

function ConnectorCard({ name, result, isCurrent }: {
  name: string;
  result?: ConnectorResult;
  isCurrent: boolean;
}) {
  const getBadgeStyle = () => {
    if (isCurrent) return "bg-orange-500/10 border-orange-500/30 text-orange-300";
    if (result?.status === "done") return "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
    if (result?.status === "error") return "bg-red-500/10 border-red-500/20 text-red-400";
    return "bg-white/5 border-white/5 text-muted-foreground";
  };

  const getBadgeText = () => {
    if (isCurrent) return "Scanning";
    if (result?.status === "done") return "Idle";
    if (result?.status === "error") return "Failed";
    return "Ready";
  };

  return (
    <motion.div
      layout
      className={cn(
        "relative rounded-xl border p-4 bg-[#18181b]/40 glass transition-all duration-300 flex flex-col justify-between min-h-[145px] overflow-hidden",
        isCurrent ? "border-orange-500/40 ring-1 ring-orange-500/10 shadow-lg shadow-orange-500/5" : "border-white/5 hover:border-white/10"
      )}
    >
      {/* Pulse effect for active scans */}
      {isCurrent && (
        <div className="absolute top-0 right-0 w-2 h-2 mt-3 mr-3 rounded-full bg-orange-500 animate-ping" />
      )}

      {/* Top Row: Logo & Status Badge */}
      <div className="flex items-center justify-between w-full">
        <div className="w-7 h-7 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-[10px] font-extrabold text-orange-400 shrink-0">
          {name.substring(0, 2).toUpperCase()}
        </div>
        <span className={cn("text-[9px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider shrink-0", getBadgeStyle())}>
          {getBadgeText()}
        </span>
      </div>

      {/* Middle Row: Title and Subtitle */}
      <div className="mt-3 flex-1 flex flex-col justify-center">
        <span className="text-xs font-bold text-white block truncate w-full" title={name}>
          {name}
        </span>
        <span className="text-[9px] text-muted-foreground font-semibold block mt-0.5 uppercase tracking-wider">
          Connector
        </span>
      </div>

      {/* Bottom Row: Metrics & Finish Status */}
      <div className="mt-3 pt-2.5 border-t border-white/5 flex items-center justify-between w-full">
        {result && result.status === "done" ? (
          <div className="space-y-0.5">
            <span className="text-[9px] font-semibold text-muted-foreground/80 block uppercase tracking-wider">Results</span>
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-white">
              <span>{result.fetched} Scanned</span>
              {result.inserted > 0 && (
                <span className="text-emerald-400 font-semibold">+{result.inserted}</span>
              )}
            </div>
          </div>
        ) : isCurrent ? (
          <div className="space-y-0.5">
            <span className="text-[9px] font-semibold text-orange-400/80 block uppercase tracking-wider animate-pulse">Running</span>
            <span className="text-[10px] font-bold text-white flex items-center gap-1">
              <Loader2 className="w-2.5 h-2.5 animate-spin text-orange-400 shrink-0" /> API Query
            </span>
          </div>
        ) : (
          <span className="text-[9px] font-semibold text-muted-foreground/60 uppercase tracking-wider">No Activity</span>
        )}

        {result?.status === "done" && (
          <div className="w-4 h-4 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <Check className="w-2.5 h-2.5" />
          </div>
        )}
      </div>
    </motion.div>
  );
}

export function ScraperPanel() {
  const queryClient = useQueryClient();
  const statusReadFailures = useRef(0);
  const [status, setStatus] = useState<ScraperStatus | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [justFinished, setJustFinished] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | undefined;

    const poll = async () => {
      try {
        const s = await fetchStatus();
        if (cancelled) return;
        statusReadFailures.current = 0;
        setError(null);
        setStatus((prev) => {
          if (prev?.is_running && !s.is_running) {
            setJustFinished(true);
            queryClient.invalidateQueries({ queryKey: ["stats"] });
            queryClient.invalidateQueries({ queryKey: ["internships"] });
          }
          return s;
        });
        if (s.is_running && !cancelled) {
          timeoutId = setTimeout(poll, 2500);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          statusReadFailures.current += 1;
          const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
          if (statusReadFailures.current >= 3) {
            setError(msg || "Unable to read scraper status");
          }
          timeoutId = setTimeout(poll, 2500);
        }
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [queryClient, status?.is_running]);

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
      const s = await fetchStatus();
      statusReadFailures.current = 0;
      setError(null);
      setStatus(s);
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

  const totalNew = status?.last_inserted ?? 0;
  const lastRun = status?.last_run_at
    ? formatDistanceToNow(parseISO(status.last_run_at), { addSuffix: true })
    : null;

  // Calculate overall scraper progress percentage
  const totalCount = CONNECTOR_ORDER.length;
  const finishedCount = status?.progress?.length ?? 0;
  const progressPercent = totalCount > 0 ? (finishedCount / totalCount) * 100 : 0;

  return (
    <div className="bg-[#18181b]/40 border border-white/5 rounded-2xl overflow-hidden glass">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between px-6 py-5 gap-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            "w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300",
            isRunning ? "bg-orange-500/20 text-orange-400" : "bg-white/5 text-muted-foreground"
          )}>
            {isRunning ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : justFinished ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <Server className="w-5 h-5" />
            )}
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              {isRunning
                ? "Indexing ATS Career Portals"
                : justFinished
                  ? `Scan Completed — ${totalNew} New Internships Indexed`
                  : "ATS Curation Scraper Control"}
              {isRunning && (
                <span className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-ping" />
              )}
            </h2>
            <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5 font-medium">
              {lastRun && !isRunning && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-orange-400/70" /> Last scan run {lastRun}
                </span>
              )}
              {isRunning && status?.current_connector && (
                <span className="text-orange-300/80 animate-pulse font-semibold">
                  Scan: {status.current_connector}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {(isRunning || status?.progress?.length) ? (
            <button
              onClick={() => setExpanded((p) => !p)}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-white/5 hover:border-white/10 hover:bg-white/5 transition-all text-xs font-semibold text-muted-foreground hover:text-white"
            >
              Connectors
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          ) : null}
          <button
            onClick={handleTrigger}
            disabled={isRunning || triggering}
            className={cn(
              "flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all duration-300",
              isRunning || triggering
                ? "bg-white/5 border border-white/5 text-muted-foreground cursor-not-allowed"
                : "bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white shadow-lg shadow-orange-500/20"
            )}
          >
            {triggering ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            {isRunning ? "Indexing..." : "Scan & Curation"}
          </button>
        </div>
      </div>

      {/* Progress timeline bar */}
      {isRunning && (
        <div className="w-full h-1 bg-white/5 relative">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="h-full bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500"
          />
        </div>
      )}

      {/* Expandable connector grid */}
      <AnimatePresence>
        {expanded && (isRunning || (status?.progress?.length ?? 0) > 0) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="overflow-hidden border-t border-white/5"
          >
            <div className="px-6 py-5 space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {CONNECTOR_ORDER.map((name) => {
                  const shortName = name === "ManualSource" ? "ManualSource" : name;
                  const result = progressMap.get(shortName);
                  const isParallel = status?.current_connector?.startsWith("Running ") ?? false;
                  const isCurrent = isRunning && (
                    status?.current_connector === shortName ||
                    (isParallel && !completedConnectors.has(shortName))
                  );
                  return (
                    <ConnectorCard
                      key={name}
                      name={shortName}
                      result={result}
                      isCurrent={isCurrent}
                    />
                  );
                })}
              </div>

              {/* Run Metrics Summary footer */}
              {!isRunning && status?.progress?.length && (
                <div className="pt-4 border-t border-white/5 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-muted-foreground gap-2 font-medium">
                  <span className="flex items-center gap-1.5">
                    <Database className="w-4 h-4 text-orange-400/80" />
                    Processed {status.last_fetched} opportunities during last session
                  </span>
                  <span className={cn("px-2.5 py-0.5 rounded-full", totalNew > 0 ? "bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20" : "")}>
                    {totalNew > 0 ? `+${totalNew} new openings indexed successfully` : "All monitored opportunities already up-to-date"}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Notice */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 mx-6 mb-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs"
          >
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
