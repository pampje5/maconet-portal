import axios from "axios";
import dotenv from "dotenv";

dotenv.config()

console.warn(process.env.API_URL);

const api = axios.create({
  baseURL: process.env.API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
