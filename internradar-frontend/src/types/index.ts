export interface Internship {
  _id?: string;
  id?: string;
  external_id: string;
  source: string;
  company: string;
  title: string;
  location: string;
  remote: boolean;
  employment_type: string;
  url: string;
  posted_at: string | null;
  scraped_at: string;
  description: string;
  skills: string[];
  tags: string[];
  category: string | null;
  fingerprint: string;
  stipend?: string | null;
  salary?: string | null;
  stipend_numeric?: number | null;
  duration?: string | null;
  company_logo?: string | null;
  industry?: string | null;
  experience_level?: string | null;
  application_deadline?: string | null;
  benefits?: string[] | null;
  work_type?: string | null;
  company_size?: string | null;
  quality_score?: number | null;
  company_type?: string | null; // "startup" | "mnc" | "enterprise"
  funding_stage?: string | null;
}

export interface UserPreferences {
  preferred_categories: string[];
  preferred_locations: string[];
  preferred_companies: string[];
  remote_only: boolean;
  email_alerts_enabled: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
  preferences: UserPreferences;
  created_at?: string;
}

export interface ConnectorPerformance {
  connector: string;
  runtime_seconds: number;
  fetched: number;
  inserted: number;
  status: string;
  speed: number;
  circuit_breaker_state: string;
}

export interface Stats {
  total_internships: number;
  total_companies: number;
  total_users: number;
  new_today: number;
  new_this_week: number;
  categories: { category: string; count: number }[];
  sources: { source: string; count: number }[];
  top_companies?: { company: string; count: number }[];
  top_locations?: { location: string; count: number }[];
  startup_vs_mnc?: { name: string; value: number }[];
  remote_vs_onsite?: { name: string; value: number }[];
  newest: { company: string; title: string; url: string } | null;
  growth?: { date: string; count: number }[];
  connector_performance?: ConnectorPerformance[];
}

export interface SearchParams {
  q?: string;
  title?: string;
  company?: string;
  location?: string;
  category?: string;
  source?: string;
  remote?: boolean;
  posted_after?: string;
  min_stipend?: number;
  max_stipend?: number;
  duration?: string;
  skills?: string;
  sort_by?: string;
  limit?: number;
  page?: number;
  page_size?: number;
}

export const CATEGORIES = [
  "Software Engineering",
  "Data Science",
  "Data Analytics",
  "Machine Learning",
  "AI",
  "Cybersecurity",
  "Embedded & Hardware",
  "Cloud & DevOps",
  "Mobile Development",
  "UI/UX",
  "Research",
  "Product",
  "Business Analytics",
  "Finance",
  "Marketing",
  "Operations",
  "Human Resources",
  "Legal & Compliance",
  "Content & Writing",
  "Other",
] as const;

export const SOURCES = [
  "greenhouse",
  "lever",
  "ashby",
  "workday",
  "smartrecruiters",
  "manual",
  "internshala",
  "jsearch",
  "yc",
  "simplify",
  "wellfound",
  "ripplematch",
  "handshake",
] as const;
