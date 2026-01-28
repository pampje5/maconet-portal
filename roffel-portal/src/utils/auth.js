import axios from "axios";

const API = process.env.REACT_APP_API_URL

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
