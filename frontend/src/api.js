const configuredApi = import.meta.env.VITE_API_URL?.trim();
const API = configuredApi || "/api/v1";

export const API_ORIGIN = API.startsWith("http")
  ? API.replace(/\/api\/v1\/?$/, "")
  : window.location.origin;

export function assetUrl(path) {
  if (!path) return "";
  if (/^https?:\/\//i.test(path)) return path;
  return `${API_ORIGIN}${path.startsWith("/") ? path : `/${path}`}`;
}

export function token() {
  return localStorage.getItem("lostlink_token");
}

function formatDetail(detail) {
  if (!detail) return "Request failed.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => {
      if (typeof item === "string") return item;
      const loc = Array.isArray(item?.loc)
        ? item.loc.filter((x) => x !== "body").join(".")
        : "";
      return loc ? `${loc}: ${item?.msg || "Invalid value"}` : (item?.msg || "Invalid value");
    }).join(" • ");
  }
  if (typeof detail === "object") {
    return detail.message || detail.error || "Request failed.";
  }
  return String(detail);
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const t = token();
  if (t) headers.set("Authorization", `Bearer ${t}`);

  let res;
  try {
    res = await fetch(`${API}${path}`, { ...options, headers });
  } catch {
    throw new Error("LostLink could not reach the server. Check that Docker is running.");
  }

  const text = await res.text();
  let body = null;
  if (text) {
    try { body = JSON.parse(text); } catch { /* non-JSON response */ }
  }

  if (!res.ok) {
    if (res.status === 401) localStorage.removeItem("lostlink_token");
    const message = formatDetail(body?.detail) || body?.message || `Request failed (${res.status}).`;
    throw new Error(message);
  }

  return body ?? {};
}

export const api = {
  register: (data) => request("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }),
  login: (data) => request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }),
  me: () => request("/auth/me"),
  reports: (type = "") => request(`/reports${type ? `?type=${encodeURIComponent(type)}` : ""}`),
  matches: () => request("/matches"),
  createReport: (form) => request("/reports", { method: "POST", body: form }),
  claim: (id, private_detail) => request(`/matches/${id}/claims`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ private_detail }),
  }),
  health: () => request("/health"),
};
