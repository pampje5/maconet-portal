import { useEffect, useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";

export default function ServiceOrdersPage() {
  
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);

  useEffect(() => {
    loadOrders();
  }, []);

  function statusBadge(status) {
  const map = {
    OPEN: "bg-blue-100 text-blue-800",
    AANGEVRAAGD: "bg-yellow-100 text-yellow-800",
    OFFERTE: "bg-purple-100 text-purple-800",
    BESTELD: "bg-orange-100 text-orange-800",
    ONTVANGEN: "bg-green-100 text-green-800",
    AFGEHANDELD: "bg-gray-200 text-gray-800",
  };

  return (
    <span
      className={`px-2 py-1 rounded text-xs font-semibold ${
        map[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status}
    </span>
  );
}


  async function loadOrders() {
    try {
      const res = await api.get("/serviceorders/overview");
      setOrders(res.data);
    } catch (err) {
      console.error(err);
      alert("Kon serviceorders niet laden");
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold mb-6">Serviceorders</h1>

      <div className="bg-white rounded-xl shadow p-4">
        <table className="w-full text-sm border">
          <thead className="bg-gray-200">
            <tr>
              <th className="border p-2">SO</th>
              <th className="border p-2">Klant</th>
              <th className="border p-2">PO</th>
              <th className="border p-2">Datum</th>
              <th className="border p-2 text-center">Status</th>
            </tr>
          </thead>

          <tbody>
            {orders.map((o) => (
              <tr
                key={o.so}
                className="hover:bg-blue-50 cursor-pointer"
                onClick={() => navigate(`/serviceorder?so=${o.so}`)}
                title="Klik om serviceorder te openen"
              >
                <td className="border p-2 font-mono font-semibold">
                  {o.so}
                </td>

                <td className="border p-2">
                  {o.customer_name || o.customer_id || "—"}
                </td>

                <td className="border p-2">
                  {o.po || "—"}
                </td>

                <td className="border p-2">
                  {new Date(o.created_at).toLocaleDateString()}
                </td>

                <td className="border p-2 text-center">
                  {statusBadge(o.status)}
                </td>
              </tr>
            ))}
          </tbody>

        </table>
      </div>
    </div>
  );
}
