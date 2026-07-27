const TOKEN_KEY = "interviewforge_token";
const USER_KEY = "interviewforge_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, { ...options, headers });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }
  if (!res.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
      : detail || res.statusText;
    throw new Error(message);
  }
  return data;
}

export const api = {
  register: (body) => request("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body) => request("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => request("/auth/me"),
  updateProfile: (body) => request("/auth/me", { method: "PATCH", body: JSON.stringify(body) }),
  dashboard: () => request("/dashboard/stats"),
  listInterviews: () => request("/interviews"),
  getInterview: (id) => request(`/interviews/${id}`),
  startInterview: (body) => request("/interviews", { method: "POST", body: JSON.stringify(body) }),
  answerQuestion: (sessionId, questionId, body) =>
    request(`/interviews/${sessionId}/questions/${questionId}/answer`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  completeInterview: (sessionId) =>
    request(`/interviews/${sessionId}/complete`, { method: "POST" }),
  health: () => request("/health"),
};
