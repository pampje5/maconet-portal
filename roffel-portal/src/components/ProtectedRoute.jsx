import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMe } from "../utils/auth";

const ROLE_LEVEL = {
  user: 1,
  admin: 2,
  developer: 3,
};

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
    return <div className="p-8">Laden…</div>;
  }

  // ❌ niet ingelogd
  if (!me) {
    return <Navigate to="/login" replace />;
  }

  // ❌ role te laag
  if (ROLE_LEVEL[me.role] < ROLE_LEVEL[minRole]) {
    return <Navigate to="/dashboard" replace />;
  }

  // ✅ toegestaan
  return children;
}
