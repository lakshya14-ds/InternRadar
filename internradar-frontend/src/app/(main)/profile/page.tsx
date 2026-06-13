"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { User, Bell, Save, Loader2, Check, Mail } from "lucide-react";
import { usersApi } from "@/lib/api";
import { CATEGORIES } from "@/types";
import type { UserPreferences } from "@/types";
import { cn } from "@/lib/utils";

const INDIA_CITIES = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Noida", "Gurgaon", "Remote"];

function SectionCard({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="bg-card border border-border/50 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-5">
        <Icon className="w-4 h-4 text-indigo-400" />
        <h2 className="font-semibold">{title}</h2>
      </div>
      {children}
    </div>
  );
}

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

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-muted-foreground">
        <User className="w-12 h-12 mb-3 opacity-20" />
        <p className="font-medium">Sign in to view your profile</p>
      </div>
    );
  }

  return (
    <div className="space-y-5 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold mb-0.5">Profile & Preferences</h1>
        <p className="text-muted-foreground text-sm">Customize your experience and email alerts</p>
      </div>

      {/* Account */}
      <SectionCard title="Account" icon={User}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1.5">Full Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2.5 bg-muted/50 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all" />
          </div>
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1.5">Email</label>
            <input value={session.user?.email || ""} disabled
              className="w-full px-3 py-2.5 bg-muted/30 border border-border/50 rounded-lg text-sm text-muted-foreground cursor-not-allowed" />
          </div>
        </div>
      </SectionCard>

      {/* Email Alerts */}
      <div id="alerts"><SectionCard title="Email Alerts" icon={Bell}>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border/50">
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-indigo-400" />
              <div>
                <p className="text-sm font-medium">Email Notifications</p>
                <p className="text-xs text-muted-foreground">Get alerts when matching internships are posted</p>
              </div>
            </div>
            <button
              onClick={() => setPrefs((p) => ({ ...p, email_alerts_enabled: !p.email_alerts_enabled }))}
              className={cn("relative w-10 h-5 rounded-full transition-colors shrink-0", prefs.email_alerts_enabled ? "bg-indigo-600" : "bg-muted")}
            >
              <span className={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm", prefs.email_alerts_enabled ? "translate-x-5" : "translate-x-0")} />
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border/50">
            <div>
              <p className="text-sm font-medium">Remote Only</p>
              <p className="text-xs text-muted-foreground">Only alert for remote internships</p>
            </div>
            <button
              onClick={() => setPrefs((p) => ({ ...p, remote_only: !p.remote_only }))}
              className={cn("relative w-10 h-5 rounded-full transition-colors shrink-0", prefs.remote_only ? "bg-indigo-600" : "bg-muted")}
            >
              <span className={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm", prefs.remote_only ? "translate-x-5" : "translate-x-0")} />
            </button>
          </div>
        </div>
      </SectionCard></div>

      {/* Preferred Categories */}
      <SectionCard title="Preferred Categories" icon={Bell}>
        <p className="text-xs text-muted-foreground mb-3">Select categories to receive email alerts for</p>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button key={cat} onClick={() => toggleCategory(cat)}
              className={cn("text-xs px-3 py-1.5 rounded-full border transition-all", prefs.preferred_categories.includes(cat) ? "bg-indigo-600/10 text-indigo-400 border-indigo-500/30" : "border-border/50 text-muted-foreground hover:border-indigo-500/30 hover:text-foreground")}>
              {prefs.preferred_categories.includes(cat) && <Check className="w-3 h-3 inline mr-1" />}
              {cat}
            </button>
          ))}
        </div>
      </SectionCard>

      {/* Preferred Locations */}
      <SectionCard title="Preferred Locations" icon={User}>
        <p className="text-xs text-muted-foreground mb-3">Select cities to focus on</p>
        <div className="flex flex-wrap gap-2">
          {INDIA_CITIES.map((city) => (
            <button key={city} onClick={() => toggleLocation(city)}
              className={cn("text-xs px-3 py-1.5 rounded-full border transition-all", prefs.preferred_locations.includes(city) ? "bg-indigo-600/10 text-indigo-400 border-indigo-500/30" : "border-border/50 text-muted-foreground hover:border-indigo-500/30 hover:text-foreground")}>
              {prefs.preferred_locations.includes(city) && <Check className="w-3 h-3 inline mr-1" />}
              {city}
            </button>
          ))}
        </div>
      </SectionCard>

      {/* Save Button */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <button onClick={() => updateMutation.mutate()} disabled={updateMutation.isPending}
          className={cn("flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all", saved ? "bg-green-600/10 text-green-400 border border-green-500/20" : "bg-indigo-600 hover:bg-indigo-500 text-white")}>
          {updateMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {updateMutation.isPending ? "Saving..." : saved ? "Saved!" : "Save Changes"}
        </button>
      </motion.div>
    </div>
  );
}
