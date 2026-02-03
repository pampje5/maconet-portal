import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import toast from "react-hot-toast";
import AppHeader from "../components/AppHeader";

export default function ServiceOrderNumbers() {
  const navigate = useNavigate();

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadNumbers();
  }, []);

  async function loadNumbers() {
    setLoading(true);
    try {
      const res = await api.get("/serviceorder-numbers", {
        params: { status: "RESERVED" },
      });
      setRows(res.data);
    } catch {
      toast.error("Serviceorders konden niet worden geladen");
    } finally {
      setLoading(false);
    }
  }

  function statusBadge(status) {
    const map = {
      RESERVED: "bg-blue-50 text-blue-700",
      CONFIRMED: "bg-green-50 text-green-700",
      CANCELLED: "bg-red-50 text-red-700",
    };

    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${map[status]}`}>
        {status}
      </span>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader title="Serviceorders" />

      <main className="p-4 space-y-3 pt-16">
        {loading && (
          <div className="text-sm text-gray-500">
            Laden…
          </div>
        )}

        {!loading && !rows.length && (
          <div className="text-sm text-gray-500">
            Geen serviceorders gevonden
          </div>
        )}

        {rows.map((r) => (
          <button
            key={r.id}
            onClick={() =>
              navigate(`/serviceorders/${r.so_number}`)
            }
            className="
              w-full text-left
              bg-white rounded-xl
              px-4 py-3
              shadow-sm
              active:scale-[0.98]
              transition
            "
          >
            <div className="flex justify-between items-start">
              <div className="font-mono text-lg font-semibold">
                {r.so_number}
              </div>
              {statusBadge(r.status)}
            </div>

            <div className="mt-1 text-sm text-gray-700 line-clamp-2">
              {r.description || "— geen omschrijving —"}
            </div>

            <div className="mt-1 text-xs text-gray-400">
              {new Date(r.date).toLocaleDateString("nl-NL")}
            </div>
          </button>
        ))}
      </main>
    </div>
  );
}
