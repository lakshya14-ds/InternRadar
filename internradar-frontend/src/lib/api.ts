import axios from "axios";
import type { Internship, SearchParams, Stats, User, UserPreferences } from "@/types";

const BACKEND = process.env.NEXT_PUBLIC_API_URL || "/backend";

const api = axios.create({ baseURL: BACKEND });

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

export interface InternshipResponse {
  results: Internship[];
  total: number;
}

export const internshipsApi = {
  list: (page = 1, pageSize = 20): Promise<InternshipResponse> =>
    api.get<Internship[]>(`/internships?page=${page}&page_size=${pageSize}`).then((r) => ({
      results: r.data,
      total: parseInt(r.headers["x-total-count"] || "0", 10),
    })),

  search: (params: SearchParams): Promise<InternshipResponse> => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.append(k, String(v));
    });
    return api.get<Internship[]>(`/internships/search?${qs}`).then((r) => ({
      results: r.data,
      total: parseInt(r.headers["x-total-count"] || "0", 10),
    }));
  },

  getById: (id: string) =>
    api.get<Internship>(`/internships/${id}`).then((r) => r.data),

  latest: (limit = 6) =>
    api.get<Internship[]>(`/internships/latest?limit=${limit}`).then((r) => r.data),

  featuredMnc: (limit = 20) =>
    api.get<Internship[]>(`/internships/featured-mnc?limit=${limit}`).then((r) => r.data),

  startups: (limit = 20) =>
    api.get<Internship[]>(`/internships/startups?limit=${limit}`).then((r) => r.data),

  getRecommendations: (id: string) =>
    api.get<Internship[]>(`/internships/${id}/recommendations`).then((r) => r.data),
};

export const statsApi = {
  get: () => api.get<Stats>("/api/stats").then((r) => r.data),
};

export const authApi = {
  register: (email: string, password: string, name: string) =>
    api.post("/api/auth/register", { email, password, name }).then((r) => r.data),

  login: (email: string, password: string) =>
    api.post("/api/auth/login", { email, password, name: "" }).then((r) => r.data),
};

export const usersApi = {
  me: (token: string) =>
    api.get<User>("/api/users/me", { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  update: (token: string, data: { name?: string; preferences?: UserPreferences }) =>
    api.put<User>("/api/users/me", data, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  bookmarks: (token: string) =>
    api.get<Internship[]>("/api/users/me/bookmarks", { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  bookmarkIds: (token: string) =>
    api.get<string[]>("/api/users/me/bookmarks/ids", { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  addBookmark: (token: string, internshipId: string) =>
    api.post(`/api/users/me/bookmarks/${internshipId}`, {}, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  removeBookmark: (token: string, internshipId: string) =>
    api.delete(`/api/users/me/bookmarks/${internshipId}`, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  recommendations: (token: string) =>
    api.get<Internship[]>("/api/users/me/recommendations", { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  listSavedSearches: (token: string) =>
    api.get<any[]>("/api/users/me/saved-searches", { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  createSavedSearch: (token: string, data: { name: string; query_params: Record<string, any>; frequency: string }) =>
    api.post("/api/users/me/saved-searches", data, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),

  deleteSavedSearch: (token: string, searchId: string) =>
    api.delete(`/api/users/me/saved-searches/${searchId}`, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data),
};

export const companiesApi = {
  enrich: (companyName: string) =>
    api.get<{
      logo: string | null;
      website: string | null;
      industry: string | null;
      company_size: string | null;
      description: string | null;
    }>(`/companies/enrich/${encodeURIComponent(companyName)}`).then((r) => r.data),

  discover: (data: { name: string; careers_url?: string }) =>
    api.post<{
      success: boolean;
      company: {
        id: string;
        name: string;
        ats_provider: string;
        careers_url: string;
      };
    }>("/companies/discover", data).then((r) => r.data),

  getCompanyDetails: (companyName: string) =>
    api.get<any>(`/companies/details/${encodeURIComponent(companyName)}`).then((r) => r.data),
};

