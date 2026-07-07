"use client";

import { useState, useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import {
  RefreshCw, CheckCircle2, AlertCircle, Loader2,
  Zap, ChevronDown, ChevronUp, Clock, Server, Play, Check, Database, Activity
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow, parseISO } from "date-fns";

interface ConnectorResult {
  connector: string;
  fetched: number;
  inserted: number;
  status: "done" | "error";
  error?: string;
  runtime_seconds?: number;
  speed?: number;
  circuit_breaker_state?: string;
}

interface ScraperStatus {
  is_running: boolean;
  last_run_at: string | null;
  last_fetched: number;
  last_inserted: number;
  current_connector: string | null;
  progress: ConnectorResult[];
  error: string | null;
  total_speed?: number | null;
  success_rate?: number | null;
  eta_seconds?: number | null;
}

const CONNECTOR_ORDER = [
  "Greenhouse",
  "Lever",
  "Ashby",
  "Workday",
  "SmartRecruiters",
  "ManualSource",
  "Internshala",
  "JSearch",
  "YC",
  "Simplify",
  "Wellfound",
  "RippleMatch",
  "Handshake"
];

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
    if (isCurrent) return "bg-orange-500/10 border-orange-500/30 text-orange-400";
    if (result?.circuit_breaker_state === "open") return "bg-red-500/10 border-red-500/20 text-red-400";
    if (result?.status === "done") return "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
    if (result?.status === "error") return "bg-red-500/10 border-red-500/20 text-red-400";
    return "bg-white/5 border-white/5 text-muted-foreground/60";
  };

  const getBadgeText = () => {
    if (isCurrent) return "Scanning";
    if (result?.circuit_breaker_state === "open") return "Tripped";
    if (result?.status === "done") return "Idle";
    if (result?.status === "error") return "Failed";
    return "Ready";
  };

  return (
    <motion.div
      layout
      className={cn(
        "relative rounded-2xl border p-4 bg-[#0a080f] glass transition-all duration-300 flex flex-col justify-between min-h-[145px] overflow-hidden",
        isCurrent ? "border-orange-500/30 ring-1 ring-orange-500/10 shadow-lg shadow-orange-500/5" : "border-white/5 hover:border-white/10"
      )}
    >
      {/* Pulse effect for active scans */}
      {isCurrent && (
        <div className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-orange-500 animate-ping" />
      )}

      {/* Top Row: Logo & Status Badge */}
      <div className="flex items-center justify-between w-full">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-500/10 to-amber-500/5 border border-orange-500/20 flex items-center justify-center text-[10px] font-black text-orange-400 shrink-0">
          {name.substring(0, 2).toUpperCase()}
        </div>
        <span className={cn("text-[8px] font-extrabold px-2.5 py-0.5 rounded-full border uppercase tracking-wider shrink-0", getBadgeStyle())}>
          {getBadgeText()}
        </span>
      </div>

      {/* Title */}
      <div className="mt-3 flex-1 flex flex-col justify-center">
        <span className="text-xs font-bold text-white block truncate w-full" title={name}>
          {name}
        </span>
        <span className="text-[9px] text-muted-foreground/50 font-bold block mt-0.5 uppercase tracking-wider">
          ATS Connector
        </span>
      </div>

      {/* Bottom Metrics */}
      <div className="mt-3 pt-2.5 border-t border-white/5 flex items-center justify-between w-full">
        {result && result.status === "done" ? (
          <div className="space-y-0.5 min-w-0">
            <div className="flex items-center gap-1 text-[10px] font-bold text-gray-200">
              <span>{result.fetched} Scanned</span>
              {result.inserted > 0 && (
                <span className="text-emerald-400 font-extrabold">+{result.inserted}</span>
              )}
            </div>
            {result.speed !== undefined && result.speed !== null && result.speed > 0 && (
              <span className="text-[9px] text-amber-400/80 block mt-0.5 font-bold">
                Throughput: {result.speed} roles/s
              </span>
            )}
            {result.runtime_seconds !== undefined && result.runtime_seconds !== null && (
              <span className="text-[9px] text-muted-foreground/50 block">
                Duration: {result.runtime_seconds}s
              </span>
            )}
          </div>
        ) : isCurrent ? (
          <div className="space-y-0.5">
            <span className="text-[9px] font-bold text-orange-400/80 block uppercase tracking-wider animate-pulse">Running</span>
            <span className="text-[10px] font-bold text-white flex items-center gap-1">
              <Loader2 className="w-2.5 h-2.5 animate-spin text-orange-400 shrink-0" /> API Scan
            </span>
          </div>
        ) : result?.circuit_breaker_state === "open" ? (
          <div className="space-y-0.5">
            <span className="text-[9px] font-bold text-red-400 block uppercase tracking-wider">Breaker Open</span>
            <span className="text-[10px] font-bold text-red-400/80">Tripped</span>
          </div>
        ) : (
          <span className="text-[9px] font-semibold text-muted-foreground/40 uppercase tracking-wider">No Curation</span>
        )}

        {result?.status === "done" && result.circuit_breaker_state !== "open" && (
          <div className="w-4.5 h-4.5 rounded-full bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 shrink-0">
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
    <div className="bg-[#0a080f]/40 border border-white/5 rounded-2xl overflow-hidden glass">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between px-6 py-5 gap-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            "w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300 border border-white/5",
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
            <h2 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
              {isRunning
                ? "Indexing ATS Career Portals"
                : justFinished
                  ? `Scan Completed — ${totalNew} New Internships Indexed`
                  : "ATS Curation Scraper Engine"}
              {isRunning && (
                <span className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
              )}
            </h2>
            <div className="flex items-center gap-3 text-[10px] text-muted-foreground mt-0.5 font-bold uppercase tracking-wider flex-wrap">
              {lastRun && !isRunning && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-orange-400/70" /> Last scan run {lastRun}
                </span>
              )}
              {isRunning && status?.current_connector && (
                <span className="text-orange-400 animate-pulse font-extrabold">
                  Target: {status.current_connector}
                </span>
              )}
              {isRunning && status?.eta_seconds !== undefined && status?.eta_seconds !== null && (
                <span className="text-amber-400 font-extrabold flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-amber-400" /> ETA: ~{status.eta_seconds}s
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {(isRunning || status?.progress?.length) ? (
            <button
              onClick={() => setExpanded((p) => !p)}
              className="flex items-center gap-1 px-3 py-2 rounded-xl border border-white/5 hover:border-white/10 hover:bg-white/5 transition-all text-xs font-bold text-muted-foreground hover:text-white"
            >
              Pipeline Status
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
            {isRunning ? "Running scan..." : "Start Scraper"}
          </button>
        </div>
      </div>

      {/* Progress timeline bar & Packet movement layer */}
      {isRunning && (
        <div className="w-full h-1 bg-white/5 relative overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="h-full bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500"
          />
          {/* Packet Flow Animation */}
          <div className="absolute inset-0 pointer-events-none" style={{ background: "transparent" }}>
            <div className="absolute top-0 bottom-0 w-8 bg-gradient-to-r from-transparent via-white/40 to-transparent" style={{ animation: "packet-move-right 1.8s infinite linear" }} />
          </div>
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
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
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
                <div className="pt-4 border-t border-white/5 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-muted-foreground gap-4 font-bold uppercase tracking-wider">
                  <div className="flex flex-wrap items-center gap-4">
                    <span className="flex items-center gap-1.5">
                      <Database className="w-4 h-4 text-orange-400/80" />
                      Processed {status.last_fetched} openings
                    </span>
                    {status.total_speed !== undefined && status.total_speed !== null && status.total_speed > 0 && (
                      <span className="flex items-center gap-1.5">
                        <Zap className="w-4 h-4 text-amber-400" />
                        Scan Rate: {status.total_speed} j/s
                      </span>
                    )}
                    {status.success_rate !== undefined && status.success_rate !== null && (
                      <span className="flex items-center gap-1.5">
                        <Activity className="w-4 h-4 text-emerald-400" />
                        Reliability: {Math.round(status.success_rate * 100)}%
                      </span>
                    )}
                  </div>
                  <span className={cn("px-3 py-1 rounded-xl text-[9px]", totalNew > 0 ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-black" : "bg-white/5 border border-white/5 font-semibold")}>
                    {totalNew > 0 ? `+${totalNew} new openings sync success` : "All career portal listings current"}
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
            className="flex items-center gap-2 mx-6 mb-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-bold"
          >
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
