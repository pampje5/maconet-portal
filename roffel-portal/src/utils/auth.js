import api from "../api";

export async function getMe() {
  try {
    const res = await api.get("/auth/whoami");
    return res.data;
  } catch {
    return null;
  }
}

