"use client";

import { useState, useEffect, useMemo } from "react";
import { useSession } from "next-auth/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { User, Bell, Save, Loader2, Check, Mail, Sparkles, Shield, MapPin, Settings2, Eye, Award } from "lucide-react";
import { usersApi } from "@/lib/api";
import { CATEGORIES } from "@/types";
import type { UserPreferences } from "@/types";
import { cn } from "@/lib/utils";

const INDIA_CITIES = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Noida", "Gurgaon", "Remote"];

export default function ProfilePage() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState(false);
  const [name, setName] = useState(session?.user?.name || "");
  const [prefs, setPrefs] = useState<UserPreferences>({
    preferred_categories: [],
    preferred_locations: [],
    preferred_companies: [],
    remote_only: false,
    email_alerts_enabled: true,
  });

  const { data: profile } = useQuery({
    queryKey: ["profile", session?.accessToken],
    queryFn: () => usersApi.me(session!.accessToken!),
    enabled: !!session?.accessToken,
  });

  const { data: savedSearches, isLoading: savedSearchesLoading } = useQuery({
    queryKey: ["saved-searches", session?.accessToken],
    queryFn: () => usersApi.listSavedSearches(session!.accessToken!),
    enabled: !!session?.accessToken,
  });

  const deleteSavedSearchMutation = useMutation({
    mutationFn: (searchId: string) => usersApi.deleteSavedSearch(session!.accessToken!, searchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-searches"] });
    },
  });

  useEffect(() => {
    if (profile) {
      setName(profile.name);
      setPrefs(profile.preferences);
    }
  }, [profile]);

  const updateMutation = useMutation({
    mutationFn: () => usersApi.update(session!.accessToken!, { name, preferences: prefs }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    },
  });

  const toggleCategory = (cat: string) => {
    setPrefs((p) => ({
      ...p,
      preferred_categories: p.preferred_categories.includes(cat)
        ? p.preferred_categories.filter((c) => c !== cat)
        : [...p.preferred_categories, cat],
    }));
  };

  const toggleLocation = (loc: string) => {
    setPrefs((p) => ({
      ...p,
      preferred_locations: p.preferred_locations.includes(loc)
        ? p.preferred_locations.filter((l) => l !== loc)
        : [...p.preferred_locations, loc],
    }));
  };

  // Profile setup completeness helper
  const completeness = useMemo(() => {
    let score = 20; // base score for registered
    if (name) score += 20;
    if (prefs.preferred_categories.length > 0) score += 20;
    if (prefs.preferred_locations.length > 0) score += 20;
    if (prefs.email_alerts_enabled) score += 20;
    return score;
  }, [name, prefs]);

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-muted-foreground bg-[#18181b]/40 border border-white/5 rounded-2xl glass max-w-xl mx-auto mt-10">
        <div className="w-14 h-14 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-4 text-orange-400">
          <User className="w-6 h-6" />
        </div>
        <h2 className="text-white font-bold text-base mb-1">Verify Your Profile</h2>
        <p className="text-xs text-muted-foreground max-w-xs text-center mb-4">
          Please log in to manage preferences, configure categories, and save jobs.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300 text-xs font-semibold mb-2">
          <Settings2 className="w-3.5 h-3.5 text-orange-400" /> Account Settings
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white mb-0.5">My Profile & Alert Preferences</h1>
        <p className="text-muted-foreground text-xs font-semibold">
          Configure job alerts, target categories, and location filters
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT COLUMN: Student Card & Setup Progress */}
        <div className="lg:col-span-1 space-y-6">
          {/* Avatar and completion card */}
          <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass">
            <div className="absolute top-0 right-0 -mt-8 -mr-8 w-24 h-24 bg-orange-500/3 rounded-full blur-2xl" />

            <div className="flex flex-col items-center text-center space-y-4">
              <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500 to-amber-600 rounded-full blur opacity-40 group-hover:opacity-60 transition-opacity duration-300" />
                <div className="relative w-20 h-20 rounded-full bg-gradient-to-tr from-orange-500 to-amber-600 flex items-center justify-center text-2xl font-black text-white uppercase shadow-lg shadow-orange-500/5">
                  {name.charAt(0) || "S"}
                </div>
              </div>

              <div>
                <h2 className="text-base font-extrabold text-white">{name || "Student Coder"}</h2>
                <p className="text-xs text-muted-foreground mt-0.5 font-medium">{session.user?.email}</p>
              </div>

              <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
                <Award className="w-3 h-3 text-emerald-400" /> Active Student
              </div>
            </div>

            {/* Completion progress */}
            <div className="mt-6 pt-6 border-t border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold">
                <span className="text-muted-foreground">Profile Completeness</span>
                <span className="text-orange-400 font-mono">{completeness}%</span>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${completeness}%` }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"
                />
              </div>
              <p className="text-[10px] text-muted-foreground leading-relaxed">
                Completing your profile improves matching accuracy for targeted internship alerts.
              </p>
            </div>
          </div>

          {/* Account Card */}
          <div className="rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass space-y-5">
            <h3 className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest flex items-center gap-2">
              <User className="w-4 h-4 text-orange-400" /> General Details
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1.5">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-[#09090b]/60 border border-white/5 rounded-xl text-xs text-white focus:outline-none focus:border-orange-500/40"
                  placeholder="Enter full name"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1.5">Email Address</label>
                <input
                  type="text"
                  value={session.user?.email || ""}
                  disabled
                  className="w-full px-3.5 py-2.5 bg-[#09090b]/30 border border-white/5 rounded-xl text-xs text-muted-foreground cursor-not-allowed"
                />
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Preferences setting dashboard */}
        <div className="lg:col-span-2 space-y-6">
          {/* Notifications Card */}
          <div id="alerts" className="rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass space-y-5">
            <h3 className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest flex items-center gap-2">
              <Bell className="w-4 h-4 text-orange-400" /> Notifications & Alerts
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-4 bg-[#18181b]/40 border border-white/5 rounded-xl">
                <div className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-orange-500/10 text-orange-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-white block">Email Curation Alerts</span>
                    <span className="text-[10px] text-muted-foreground">Receive matching daily internships</span>
                  </div>
                </div>
                <button
                  onClick={() => setPrefs((p) => ({ ...p, email_alerts_enabled: !p.email_alerts_enabled }))}
                  className={cn("relative w-9 h-5 rounded-full transition-colors shrink-0", prefs.email_alerts_enabled ? "bg-orange-600" : "bg-white/10")}
                >
                  <span className={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm", prefs.email_alerts_enabled ? "translate-x-4" : "translate-x-0")} />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-[#18181b]/40 border border-white/5 rounded-xl">
                <div className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
                    <Eye className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-white block">Remote Listings Only</span>
                    <span className="text-[10px] text-muted-foreground">Alert only for work-from-home</span>
                  </div>
                </div>
                <button
                  onClick={() => setPrefs((p) => ({ ...p, remote_only: !p.remote_only }))}
                  className={cn("relative w-9 h-5 rounded-full transition-colors shrink-0", prefs.remote_only ? "bg-orange-600" : "bg-white/10")}
                >
                  <span className={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm", prefs.remote_only ? "translate-x-4" : "translate-x-0")} />
                </button>
              </div>
            </div>
          </div>

          {/* Preferred Categories Card */}
          <div className="rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass space-y-4">
            <div>
              <h3 className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest flex items-center gap-2 mb-1">
                <Sparkles className="w-4 h-4 text-orange-400" /> Target Categories
              </h3>
              <p className="text-[11px] text-muted-foreground">Filter matching internships to these core domains</p>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {CATEGORIES.map((cat) => {
                const selected = prefs.preferred_categories.includes(cat);
                return (
                  <button
                    key={cat}
                    onClick={() => toggleCategory(cat)}
                    className={cn(
                      "text-[10px] font-bold px-3 py-1.5 rounded-full border transition-all uppercase tracking-wide",
                      selected
                        ? "bg-orange-600 border-transparent text-white shadow-lg shadow-orange-500/10"
                        : "bg-white/5 border-white/5 text-muted-foreground hover:border-orange-500/30 hover:text-white"
                    )}
                  >
                    {selected && <Check className="w-3.5 h-3.5 inline mr-1" />}
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Preferred Locations Card */}
          <div className="rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass space-y-4">
            <div>
              <h3 className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest flex items-center gap-2 mb-1">
                <MapPin className="w-4 h-4 text-orange-400" /> Target Locations
              </h3>
              <p className="text-[11px] text-muted-foreground">Select primary metropolitan tech hubs</p>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {INDIA_CITIES.map((city) => {
                const selected = prefs.preferred_locations.includes(city);
                return (
                  <button
                    key={city}
                    onClick={() => toggleLocation(city)}
                    className={cn(
                      "text-[10px] font-bold px-3 py-1.5 rounded-full border transition-all uppercase tracking-wide",
                      selected
                        ? "bg-orange-600 border-transparent text-white shadow-lg shadow-orange-500/10"
                        : "bg-white/5 border-white/5 text-muted-foreground hover:border-orange-500/30 hover:text-white"
                    )}
                  >
                    {selected && <Check className="w-3.5 h-3.5 inline mr-1" />}
                    {city}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Saved Searches & Alerts Card */}
          <div className="rounded-2xl border border-white/5 bg-[#18181b]/40 p-6 glass space-y-4">
            <div>
              <h3 className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest flex items-center gap-2 mb-1">
                <Settings2 className="w-4 h-4 text-orange-400" /> Saved Searches & Alerts
              </h3>
              <p className="text-[11px] text-muted-foreground">Manage your custom saved queries and email alert frequencies (instant, daily, weekly)</p>
            </div>

            {savedSearchesLoading ? (
              <div className="space-y-2 animate-pulse">
                {[...Array(2)].map((_, i) => (
                  <div key={i} className="h-14 bg-white/5 border border-white/5 rounded-xl" />
                ))}
              </div>
            ) : savedSearches?.length ? (
              <div className="space-y-3">
                {savedSearches.map((search: any) => (
                  <div key={search._id} className="flex items-center justify-between p-4 bg-[#09090b]/40 border border-white/5 rounded-xl gap-4">
                    <div className="space-y-1 min-w-0">
                      <span className="text-xs font-bold text-white block truncate">{search.name}</span>
                      <div className="flex flex-wrap items-center gap-x-2 text-[10px] text-muted-foreground">
                        <span className="capitalize bg-orange-500/10 text-orange-400 border border-orange-500/10 px-1.5 py-0.2 rounded font-semibold">
                          {search.frequency}
                        </span>
                        <span className="truncate">
                          Params: {Object.entries(search.query_params || {})
                            .map(([k, v]) => `${k}=${v}`)
                            .join(", ") || "None"}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteSavedSearchMutation.mutate(search._id)}
                      disabled={deleteSavedSearchMutation.isPending}
                      className="text-[10px] font-bold text-red-400 hover:text-red-300 px-2.5 py-1.5 rounded-lg border border-red-500/10 hover:bg-red-500/10 transition-all shrink-0"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground text-xs bg-[#09090b]/20 rounded-xl border border-white/5">
                No saved searches found. You can save search filters from the search page.
              </div>
            )}
          </div>

          {/* Sticky Save Changes Control */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={() => updateMutation.mutate()}
              disabled={updateMutation.isPending}
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-extrabold transition-all duration-300 shadow-lg",
                saved
                  ? "bg-emerald-600/10 border border-emerald-500/20 text-emerald-400"
                  : "bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white shadow-orange-500/10"
              )}
            >
              {updateMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : saved ? (
                <Check className="w-4 h-4" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {updateMutation.isPending ? "Saving changes..." : saved ? "Preferences saved!" : "Save Settings"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
