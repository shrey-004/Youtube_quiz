/**
 * api.ts — Centralized API client for the YouTube Quiz Generator.
 *
 * All communication with the FastAPI backend goes through this file.
 * Benefits:
 * - One place to change the API URL
 * - Consistent error handling
 * - Easy to mock in tests
 */

import axios from "axios";
import Cookies from "js-cookie";

// Base URL from environment variable
// In development: http://localhost:8000
// In production: your Render deployment URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor — automatically attach JWT token to every request
// This runs before every API call
apiClient.interceptors.request.use((config) => {
  const token = Cookies.get("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle 401 globally
// If token expires, redirect to login automatically
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove("access_token");
      Cookies.remove("username");
      Cookies.remove("user_id");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ─── AUTH ────────────────────────────────────────────────────────────────────

export const authAPI = {
  register: async (email: string, username: string, password: string) => {
    const response = await apiClient.post("/api/auth/register", {
      email,
      username,
      password,
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await apiClient.post("/api/auth/login", {
      email,
      password,
    });
    // Store token and user info in cookies
    const { access_token, username, user_id } = response.data;
    Cookies.set("access_token", access_token, { expires: 1 }); // 1 day
    Cookies.set("username", username, { expires: 1 });
    Cookies.set("user_id", user_id, { expires: 1 });
    return response.data;
  },

  logout: () => {
    Cookies.remove("access_token");
    Cookies.remove("username");
    Cookies.remove("user_id");
    window.location.href = "/login";
  },

  isLoggedIn: () => {
    return !!Cookies.get("access_token");
  },

  getUsername: () => {
    return Cookies.get("username") || "";
  },
};

// ─── QUIZZES ─────────────────────────────────────────────────────────────────

export const quizAPI = {
  generateQuiz: async (
    url: string,
    numEasy: number = 3,
    numMedium: number = 3,
    numHard: number = 2
  ) => {
    const response = await apiClient.post("/api/quizzes/generate", {
      url,
      num_easy: numEasy,
      num_medium: numMedium,
      num_hard: numHard,
    });
    return response.data;
  },

  submitQuiz: async (
    quizId: string,
    answers: { question_id: string; selected_answer: string }[]
  ) => {
    const response = await apiClient.post(`/api/quizzes/${quizId}/submit`, {
      quiz_id: quizId,
      answers,
    });
    return response.data;
  },

  getMyQuizzes: async () => {
    const response = await apiClient.get("/api/quizzes/my-quizzes");
    return response.data;
  },

  getMyAttempts: async () => {
    const response = await apiClient.get("/api/quizzes/my-attempts");
    return response.data;
  },
};