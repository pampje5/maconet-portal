import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../api";

const ROLE_LEVEL = {
  user: 1,
  admin: 2,
  developer: 3,
};

async function getMe() {
  const res = await api.get("/auth/whoami");
  return res.data;
}

export default function ProtectedRoute({ children, minRole = "user" }) {
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then(setMe)
      .catch(() => setMe(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-6 text-gray-500">Laden…</div>;
  }

  // ❌ Niet ingelogd
  if (!me) {
    return <Navigate to="/login" replace />;
  }

  // ❌ Rol onvoldoende
  if (ROLE_LEVEL[me.role] < ROLE_LEVEL[minRole]) {
    return <Navigate to="/" replace />;
  }

  // ✅ Toegestaan
  return children;
}
