const DEFAULT_BASE = "http://localhost:8000/api";

export const apiBase = import.meta.env.VITE_API_BASE || DEFAULT_BASE;

export const apiOrigin = (() => {
  try {
    const url = new URL(apiBase);
    return url.origin;
  } catch {
    return "";
  }
})();

export const getToken = () => localStorage.getItem("access_token");
export const setToken = (token) => localStorage.setItem("access_token", token);
export const clearToken = () => localStorage.removeItem("access_token");

export const buildQuery = (params) => {
  const entries = Object.entries(params || {}).filter(([, value]) => value !== "" && value != null);
  if (!entries.length) return "";
  return `?${new URLSearchParams(entries)}`;
};

export const apiFetch = async (path, options = {}) => {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const hasBody = options.body !== undefined && options.body !== null;
  const isFormData = hasBody && options.body instanceof FormData;
  if (hasBody && !isFormData && typeof options.body !== "string") {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers,
    body: hasBody && !isFormData && typeof options.body !== "string"
      ? JSON.stringify(options.body)
      : options.body,
  });

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message = isJson ? data.detail || JSON.stringify(data) : data;
    throw new Error(message || "요청에 실패했습니다.");
  }

  return data;
};

export const cleanPayload = (payload) => {
  const result = {};
  Object.entries(payload || {}).forEach(([key, value]) => {
    if (value === "" || value === undefined) return;
    result[key] = value;
  });
  return result;
};
