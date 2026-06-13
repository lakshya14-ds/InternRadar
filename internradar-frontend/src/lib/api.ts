import axios from "axios";
import type { Internship, SearchParams, Stats, User, UserPreferences } from "@/types";

const BACKEND = "/backend";

const api = axios.create({ baseURL: BACKEND });

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

export const internshipsApi = {
  list: (page = 1, pageSize = 20) =>
    api.get<Internship[]>(`/internships?page=${page}&page_size=${pageSize}`).then((r) => r.data),

  search: (params: SearchParams) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.append(k, String(v));
    });
    return api.get<Internship[]>(`/internships/search?${qs}`).then((r) => r.data);
  },

  getById: (id: string) =>
    api.get<Internship>(`/internships/${id}`).then((r) => r.data),

  latest: (limit = 6) =>
    api.get<Internship[]>(`/internships/latest?limit=${limit}`).then((r) => r.data),
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
};
