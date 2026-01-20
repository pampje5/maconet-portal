import axios from "axios";

const API = "http://127.0.0.1:8000";

export async function getMe() {
  const token = localStorage.getItem("token");
  if (!token) return null;

  const res = await axios.get(`${API}/auth/whoami`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return res.data;
}
