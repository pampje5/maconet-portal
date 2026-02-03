import { useEffect, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import ActionBar from "../components/ActionBar";
import Button from "../components/ui/Button";

export default function CombineServiceOrders() {
  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadServiceOrders();
  }, []);

  async function loadServiceOrders() {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/serviceorders/for-po-merge`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Alleen orders die wachten op combinatie
      const filtered = res.data.filter(
        (o) => o.status === "WACHT_OP_COMBINATIE"
      );

      setRows(filtered);
    } catch {
      toast.error("Kon serviceorders niet laden");
    } finally {
      setLoading(false);
    }
  }

  function toggleSelection(so) {
    setSelected((prev) =>
      prev.includes(so)
        ? prev.filter((x) => x !== so)
        : [...prev, so]
    );
  }

  async function createPurchaseOrder() {
    if (selected.length === 0) {
      toast.error("Selecteer minimaal één serviceorder");
      return;
    }

    try {
      await axios.post(
        `${API}/purchaseorders/merge`,
        { serviceorders: selected },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("Purchase order aangemaakt");
      setSelected([]);
      loadServiceOrders();
    } catch (err) {
      toast.error(
        err.response?.data?.detail || "Aanmaken purchase order mislukt"
      );
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">
        Combineer serviceorders
      </h1>

      <div className="border rounded overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="p-2 w-10"></th>
              <th className="p-2 text-left w-32">SO nr</th>
              <th className="p-2 text-left">Klant</th>
              <th className="p-2 text-left">Leverancier</th>
              <th className="p-2 text-right w-32">Ordertotaal</th>
              <th className="p-2 w-28">Datum</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((r) => (
              <tr
                key={r.so}
                className="border-b hover:bg-blue-50 cursor-pointer"
                onClick={() => toggleSelection(r.so)}
              >
                <td className="p-2 text-center">
                  <input
                    type="checkbox"
                    checked={selected.includes(r.so)}
                    onChange={() => toggleSelection(r.so)}
                  />
                </td>

                <td className="p-2 font-mono font-semibold">
                  {r.so}
                </td>

                <td className="p-2">
                  {r.customer_name || "—"}
                </td>

                <td className="p-2">
                  {r.supplier_name || "—"}
                </td>

                <td className="p-2 text-right">
                  € {Number(r.order_total || 0).toFixed(2)}
                </td>

                <td className="p-2 text-center">
                  {new Date(r.created_at).toLocaleDateString("nl-NL")}
                </td>
              </tr>
            ))}

            {!rows.length && !loading && (
              <tr>
                <td colSpan={6} className="p-6 text-center text-gray-500">
                  Geen serviceorders beschikbaar voor combinatie
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <ActionBar>
        <Button
          variant="primary"
          onClick={createPurchaseOrder}
          disabled={selected.length === 0}
        >
          Maak purchase order ({selected.length})
        </Button>
      </ActionBar>
    </div>
  );
}
