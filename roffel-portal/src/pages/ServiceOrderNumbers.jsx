import { useEffect, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";




/**
 * ServiceOrderNumbers page
 * Administratieve pagina voor uitgifte en beheer van ServiceOrderNrs
 */
export default function ServiceOrderNumbers() {

  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const currentYear = new Date().getFullYear();

  // =========================
  // State
  // =========================
  const [filters, setFilters] = useState({
    year: currentYear,
    month: null,
    quarter: null,
    status: null,
  });

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({});

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
      const res = await axios.get(`${API}/serviceorder-numbers`, {
        params: filters,
        headers: { Authorization: `Bearer ${token}` },
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
      const res = await axios.post(
        `${API}/serviceorder-numbers/reserve`,
        null,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success(`Nummer ${res.data.so_number} gereserveerd`);
      loadNumbers();
    } catch {
      toast.error("Kon geen nieuw nummer reserveren");
    }
  }

  async function reserveBatch() {
    try {
      const res = await axios.post(
        `${API}/serviceorder-numbers/reserve-batch/10`,
        null,
        { headers: { Authorization: `Bearer ${token}` } }
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
     await axios.put(
      `${API}/serviceorder-numbers/${selected.so_number}`,
      form,
      { headers: { Authorization: `Bearer ${token}` } }
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
      await axios.post(
      `${API}/serviceorder-numbers/${selected.so_number}/confirm`,
      null,
      { headers: { Authorization: `Bearer ${token}` } }
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
      await axios.post(
        `${API}/serviceorder-numbers/${selected.so_number}/cancel`,
        null,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("Nummer geannuleerd");
      setSelected(null);
      loadNumbers();
    } catch {
      toast.error("Annuleren mislukt");
    }
  }

  // =========================
  // Render helpers
  // =========================
  function statusBadge(status) {
    const map = {
      FREE: "bg-gray-300",
      RESERVED: "bg-blue-400",
      CONFIRMED: "bg-green-500",
      CANCELLED: "bg-red-400",
    };
    return (
      <span
        className={`px-2 py-1 rounded text-white text-xs ${map[status]}`}
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

        <button
          className="btn btn-primary"
          onClick={reserveNew}
        >
          + Nieuw nummer
        </button>

        <button
          className="btn btn-secondary"
          onClick={reserveBatch}
        >
          Reserveer 10 (werkplaats)
        </button>
      </div>

      {/* ================= Table ================= */}
      <div className="border rounded overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2 text-left">SO nr</th>
              <th className="p-2">Datum</th>
              <th className="p-2">Klant</th>
              <th className="p-2">Leverancier</th>
              <th className="p-2">Omschrijving</th>
              <th className="p-2">Type</th>
              <th className="p-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.id}
                className={`border-t hover:bg-gray-50 cursor-pointer ${
                  r.status !== "RESERVED"
                    ? "opacity-60 cursor-not-allowed"
                    : ""
                }`}
                onClick={() => {
                  if (r.status !== "RESERVED") return;
                  setSelected(r);
                  setForm({
                    customer_id: r.customer_id,
                    customer_name_free: r.customer_name_free,
                    supplier: r.supplier,
                    description: r.description,
                    type: r.type,
                    offer: r.offer,
                    offer_amount: r.offer_amount,
                  });
                }}
              >
                <td className="p-2 font-mono">{r.so_number}</td>
                <td className="p-2">
                  {new Date(r.date).toLocaleDateString()}
                </td>
                <td className="p-2">
                  {r.customer_name_free || r.customer_id || ""}
                </td>
                <td className="p-2">{r.supplier}</td>
                <td className="p-2">{r.description}</td>
                <td className="p-2">{r.type}</td>
                <td className="p-2 text-center">
                  {statusBadge(r.status)}
                </td>
              </tr>
            ))}

            {!rows.length && !loading && (
              <tr>
                <td colSpan={7} className="p-4 text-center">
                  Geen resultaten
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* ================= Editor ================= */}
      {selected && (
        <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg p-4">
          <h2 className="text-lg font-semibold mb-4">
            {selected.so_number}
          </h2>

          <label className="block mb-2">
            Omschrijving
            <input
              className="w-full"
              value={form.description || ""}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
            />
          </label>

          <label className="block mb-2">
            Leverancier
            <input
              className="w-full"
              value={form.supplier || ""}
              onChange={(e) =>
                setForm({ ...form, supplier: e.target.value })
              }
            />
          </label>

          <label className="block mb-2">
            Type
            <select
              className="w-full"
              value={form.type || ""}
              onChange={(e) =>
                setForm({ ...form, type: e.target.value })
              }
            >
              <option value="">–</option>
              <option value="VO">VO</option>
              <option value="OH">OH</option>
            </select>
          </label>

          <label className="flex items-center gap-2 mb-2">
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
                className="w-full"
                value={form.offer_amount || ""}
                onChange={(e) =>
                  setForm({
                    ...form,
                    offer_amount: e.target.value,
                  })
                }
              />
            </label>
          )}

          <div className="flex gap-2">
            <button className="btn btn-primary" onClick={saveDetails}>
              Opslaan
            </button>
            <button
              className="btn btn-success"
              onClick={confirmNumber}
            >
              Bevestigen
            </button>
            <button
              className="btn btn-danger"
              onClick={cancelNumber}
            >
              Annuleren
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
