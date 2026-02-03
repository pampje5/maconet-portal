import { useEffect, useState } from "react";
import api from "../api";
import toast from "react-hot-toast";
import ActionBar from "../components/ActionBar";
import Button from "../components/ui/Button";



/**
 * ServiceOrderNumbers page
 * Administratieve pagina voor uitgifte en beheer van ServiceOrderNrs
 */
export default function ServiceOrderNumbers() {

  const currentYear = new Date().getFullYear();

  // =========================
  // State
  // =========================
  const [filters, setFilters] = useState({
    year: currentYear,
    month: "",
    quarter: "",
    status: "",
  });

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({});

  const [showEditModal, setShowEditModal] = useState(false);

  // =========================
  // Load list
  // =========================
  useEffect(() => {
    loadNumbers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

async function loadNumbers() {
  setLoading(true);
  try {
    const params = {};

    if (filters.year) params.year = filters.year;
    if (filters.month) params.month = Number(filters.month);
    if (filters.quarter) params.quarter = Number(filters.quarter);
    if (filters.status) params.status = filters.status;

    const res = await api.get(`/serviceorder-numbers`, {
      params,
    });

    setRows(res.data);
  } catch (err) {
    toast.error("Fout bij laden serviceordernummers");
  } finally {
    setLoading(false);
  }
}


  // =========================
  // Actions
  // =========================
  async function reserveNew() {
    try {
      const res = await api.post(
        "/serviceorder-numbers/reserve",
        null,
        
      );

      toast.success(`Nummer ${res.data.so_number} gereserveerd`);
      loadNumbers();
    } catch {
      toast.error("Kon geen nieuw nummer reserveren");
    }
  }

  async function reserveBatch() {
    try {
      const res = await api.post(
        "/serviceorder-numbers/reserve-batch/10",
        null,
      );

      toast.success(`${res.data.count} nummers gereserveerd voor werkplaats`);
      loadNumbers();
    } catch {
      toast.error("Batch reserveren mislukt");
    }
  }

  async function saveDetails() {
    if (!selected) return;

    try {
      // 🔧 Payload exact laten matchen met ServiceOrderNumberUpdate
      const payload = {
        customer_id: form.customer_id ?? null,
        customer_name_free: form.customer_name_free || null,

        supplier_id: form.supplier_id ?? null,
        supplier_name_free: form.supplier_name_free || null,

        description: form.description || null,
        type: form.type || null,

        offer: !!form.offer,
        offer_amount:
          form.offer
            ? (form.offer_amount === null || form.offer_amount === ""
                ? null
                : Number(form.offer_amount))
            : null,
      };

      await api.put(
        `/serviceorder-numbers/${selected.so_number}`,
        payload,
      );

      toast.success("Gegevens opgeslagen");
      setSelected(null);
      loadNumbers();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Opslaan mislukt");
    }
  }


  async function confirmNumber() {
    if (!selected) return;

    try {
      await api.post(
      `/serviceorder-numbers/${selected.so_number}/confirm`,
      null,
      );

      toast.success("Nummer bevestigd");
      setSelected(null);
      loadNumbers();
    } catch {
      toast.error("Bevestigen mislukt");
    }
  }

  async function cancelNumber() {
    if (!selected) return;

    try {
      await api.post(
        `/serviceorder-numbers/${selected.so_number}/cancel`,
        null,
      );

      toast.success("Nummer geannuleerd");
      setSelected(null);
      loadNumbers();
    } catch {
      toast.error("Annuleren mislukt");
    }
  }

  async function loadServiceOrderNumberDetails(soNumber) {
  try {
    const res = await api.get(
      `/serviceorder-numbers/${soNumber}`,
    );

    const r = res.data;

    setSelected(r);
    setForm({
      customer_id: r.customer_id ?? null,
      customer_name_free: r.customer_name_free ?? null,

      supplier_id: r.supplier_id ?? null,
      supplier_name_free: r.supplier_name_free ?? null,

      description: r.description ?? null,
      type: r.type ?? null,

      offer: !!r.offer,
      offer_amount: r.offer_amount ?? null,
    });


    setShowEditModal(true);
  } catch (err) {
    toast.error("Serviceordernummer kon niet worden geladen");
  }
}


  // =========================
  // Render helpers
  // =========================
  function statusBadge(status) {
    const map = {
      FREE: "bg-gray-200 text-gray-800",
      RESERVED: "bg-blue-100 text-blue-800",
      CONFIRMED: "bg-green-100 text-green-800",
      CANCELLED: "bg-red-100 text-red-800",
    };
    return (
      <span
        className={`px-2 py-1 rounded text-xs font-semibold ${map[status]}`}
      >
        {status}
      </span>
    );
  }

  // =========================
  // Render
  // =========================
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">
        ServiceOrderNummers
      </h1>

      {/* ================= Filters & Actions ================= */}
      <div className="flex gap-3 mb-4 items-center">
        {/* Jaar */}
        <select
          value={filters.year}
          onChange={(e) =>
            setFilters({ ...filters, year: e.target.value })
          }
        >
          {[currentYear - 1, currentYear, currentYear + 1].map(
            (y) => (
              <option key={y} value={y}>
                {y}
              </option>
            )
          )}
        </select>

          {/* Kwartaal */}
        <select
          value={filters.quarter}
          onChange={(e) =>
            setFilters({ ...filters, quarter: e.target.value, month: "" })
          }
        >
          <option value="">Alle kwartalen</option>
          <option value="1">Q1</option>
          <option value="2">Q2</option>
          <option value="3">Q3</option>
          <option value="4">Q4</option>
        </select>

        {/* Maand */}
        <select
          value={filters.month}
          onChange={(e) =>
            setFilters({ ...filters, month: e.target.value, quarter: "" })
          }
        >
          <option value="">Alle maanden</option>
          {[...Array(12)].map((_, i) => (
            <option key={i + 1} value={i + 1}>
              {new Date(2000, i).toLocaleString("nl-NL", { month: "long" })}
            </option>
          ))}
        </select>

        {/* Status */}
        <select
          value={filters.status || ""}
          onChange={(e) =>
            setFilters({
              ...filters,
              status: e.target.value || null,
            })
          }
        >
          <option value="">Alle statussen</option>
          <option value="FREE">FREE</option>
          <option value="RESERVED">RESERVED</option>
          <option value="CONFIRMED">CONFIRMED</option>
          <option value="CANCELLED">CANCELLED</option>
        </select>

        <div className="flex-1" />

        
      </div>

      {/* ================= Table ================= */}
      <div className="border rounded overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="p-2 text-left w-32">SO nr</th>
              <th className="p-2 w-28">Datum</th>
              <th className="p-2 text-left">Klant</th>
              <th className="p-2 text-left">Leverancier</th>
              <th className="p-2 text-left">Omschrijving</th>
              <th className="p-2 w-16">Type</th>
              <th className="p-2 w-32">Status</th>
            </tr>
          </thead>

            <tbody>
              {rows.map((r) => {
                const clickable = r.status === "RESERVED";

                return (
                  <tr
                    key={r.id}
                    className={`
                      border-b
                      ${clickable ? "hover:bg-blue-50 cursor-pointer" : "opacity-60"}
                    `}
                    onClick={() => {
                      if (r.status !== "RESERVED") return;
                      loadServiceOrderNumberDetails(r.so_number);
                    }}

                  >
                    <td className="p-2 font-mono font-semibold">
                      {r.so_number}
                    </td>

                    <td className="p-2 text-center">
                      {new Date(r.date).toLocaleDateString("nl-NL")}
                    </td>

                    <td className="p-2">
                      {r.customer_name_free || r.customer_name || "—"}
                    </td>

                    <td className="p-2">
                      {r.supplier_name_free || r.supplier_name || "—"}
                    </td>

                    <td className="p-2 truncate max-w-xs">
                      {r.description || "—"}
                    </td>

                    <td className="p-2 text-center">
                      {r.type || "—"}
                    </td>

                    <td className="p-2 flex items-center gap-2">
                      {statusBadge(r.status)}
                      {r.reserved_by === "WORKSHOP" && (
                        <span title="Werkplaats">🛠️</span>
                      )}
                    </td>
                  </tr>
                );
              })}

              {!rows.length && !loading && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-gray-500">
                    Geen serviceordernummers gevonden
                  </td>
                </tr>
              )}
            </tbody>
          </table>
      </div>

      {/* ================= Editor ================= */}
      {showEditModal && selected && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-lg rounded shadow-lg p-6">

            <h2 className="text-xl font-semibold mb-4">
              Serviceordernummer {selected.so_number}
            </h2>

            <label className="block mb-3">
              Omschrijving
              <input
                className="w-full border rounded px-3 py-2"
                value={form.description || ""}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
            </label>

            <label className="block mb-3">
              Leverancier
              <input
                className="w-full border rounded px-3 py-2"
                value={form.supplier_name_free || ""}
                onChange={(e) =>
                  setForm({ ...form, supplier_name_free: e.target.value })
                }
              />
            </label>

            <label className="block mb-3">
              Klant
              <input
                className="w-full border rounded px-3 py-2"
                value={form.customer_name_free ||""}
                onChange={(e) =>
                  setForm({ ...form, customer_name_free: e.target.value})
                }
              />
            </label>


            <label className="block mb-3">
              Type
              <select
                className="w-full border rounded px-3 py-2"
                value={form.type || ""}
                onChange={(e) =>
                  setForm({ ...form, type: e.target.value })
                }
              >
                <option value="">—</option>
                <option value="VO">VO</option>
                <option value="OH">OH</option>
              </select>
            </label>

            <label className="flex items-center gap-2 mb-4">
              <input
                type="checkbox"
                checked={!!form.offer}
                onChange={(e) =>
                  setForm({ ...form, offer: e.target.checked })
                }
              />
              Offerte
            </label>

            {form.offer && (
              <label className="block mb-4">
                Offertebedrag
                <input
                  type="number"
                  className="w-full border rounded px-3 py-2"
                  value={form.offer_amount || ""}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      offer_amount: e.target.value === ""
                        ? null
                        : Number(e.target.value),
                    })
                  }

                />
              </label>
            )}

            <div className="flex justify-between mt-6">
              <button
                className="px-4 py-2 bg-gray-300 rounded"
                onClick={() => setShowEditModal(false)}
              >
                Sluiten
              </button>

              <div className="flex gap-2">
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded"
                  onClick={async () => {
                    await saveDetails();
                    setShowEditModal(false);
                  }}
                >
                  Opslaan
                </button>

                <button
                  className="px-4 py-2 bg-green-600 text-white rounded"
                  onClick={async () => {
                    await confirmNumber();
                    setShowEditModal(false);
                  }}
                >
                  Bevestigen
                </button>

                <button
                  className="px-4 py-2 bg-red-600 text-white rounded"
                  onClick={async () => {
                    await cancelNumber();
                    setShowEditModal(false);
                  }}
                >
                  Annuleren
                </button>
              </div>
            </div>

          </div>
        </div>
      )}

      <ActionBar>
        <div className="flex gap-3">
          <Button variant="primary" onClick={reserveNew}>
              Nieuw nummer
          </Button>

          <Button variant="secondary" onClick={reserveBatch}>
            🛠️ Reserveer 10 (werkplaats)
          </Button>
        </div>
      </ActionBar>

    </div>
  );
}
