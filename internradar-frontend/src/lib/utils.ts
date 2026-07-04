import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function timeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return "Unknown date";
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
  } catch {
    return "Unknown date";
  }
}

export function getInternshipId(internship: { _id?: string; id?: string }): string {
  return internship._id || internship.id || "";
}

export function sourceLabel(source: string): string {
  const map: Record<string, string> = {
    greenhouse: "Greenhouse",
    lever: "Lever",
    ashby: "Ashby",
    workday: "Workday",
    smartrecruiters: "SmartRecruiters",
    yc: "YC Jobs",
    wellfound: "Wellfound",
    simplify: "Simplify",
    ripplematch: "RippleMatch",
    handshake: "Handshake",
    jsearch: "JSearch",
    internshala: "Internshala",
    manual: "Manual",
  };
  return map[source.toLowerCase()] || source;
}

export function categoryColor(category: string | null): string {
  const colors: Record<string, string> = {
    "Software Engineering": "bg-blue-500/10 text-blue-400 border-blue-500/20",
    "Data Science": "bg-purple-500/10 text-purple-400 border-purple-500/20",
    "Data Analytics": "bg-violet-500/10 text-violet-400 border-violet-500/20",
    "Machine Learning": "bg-pink-500/10 text-pink-400 border-pink-500/20",
    "UI/UX": "bg-orange-500/10 text-orange-400 border-orange-500/20",
    "Research": "bg-teal-500/10 text-teal-400 border-teal-500/20",
    "Product": "bg-green-500/10 text-green-400 border-green-500/20",
    "Cloud & DevOps": "bg-sky-500/10 text-sky-400 border-sky-500/20",
    "Cybersecurity": "bg-red-500/10 text-red-400 border-red-500/20",
  };
  return colors[category || ""] || "bg-gray-500/10 text-gray-400 border-gray-500/20";
}
