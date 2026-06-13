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

export interface Stats {
  total_internships: number;
  total_companies: number;
  total_users: number;
  new_today: number;
  new_this_week: number;
  categories: { category: string; count: number }[];
  sources: { source: string; count: number }[];
  newest: { company: string; title: string; url: string } | null;
}

export interface SearchParams {
  title?: string;
  company?: string;
  location?: string;
  category?: string;
  source?: string;
  remote?: boolean;
  posted_after?: string;
  limit?: number;
}

export const CATEGORIES = [
  "Software Engineering",
  "Data Science",
  "Data Analytics",
  "Machine Learning",
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
] as const;
