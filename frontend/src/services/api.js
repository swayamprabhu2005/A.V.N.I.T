const API_BASE = "http://localhost:8000/api";
const WS_BASE = "ws://localhost:8000/ws/stream";

export async function fetchSystemStatus() {
  const res = await fetch(`${API_BASE}/system/status`);
  if (!res.ok) throw new Error("Failed to fetch system status");
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function fetchVehicles() {
  const res = await fetch(`${API_BASE}/vehicles`);
  if (!res.ok) throw new Error("Failed to fetch vehicles");
  return res.json();
}

export async function createVehicle(data) {
  const res = await fetch(`${API_BASE}/vehicles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create vehicle");
  }
  return res.json();
}

export async function updateVehicle(id, data) {
  const res = await fetch(`${API_BASE}/vehicles/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error("Failed to update vehicle");
  return res.json();
}

export async function deleteVehicle(id) {
  const res = await fetch(`${API_BASE}/vehicles/${id}`, {
    method: "DELETE"
  });
  if (!res.ok) throw new Error("Failed to delete vehicle");
  return res.json();
}

export async function fetchAlerts(limit = 20) {
  const res = await fetch(`${API_BASE}/alerts?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error("Failed to fetch demo scenarios");
  return res.json();
}

export function getWebSocketUrl() {
  return WS_BASE;
}
