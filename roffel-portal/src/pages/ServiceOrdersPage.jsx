import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function ServiceOrdersPage() {
  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);

  useEffect(() => {
    loadOrders();
  }, []);

  async function loadOrders() {
    try {
      const res = await axios.get(`${API}/serviceorders/overview`, {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`,
        },
      });
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
              <th className="border p-2">Status</th>
              <th className="border p-2">Datum</th>
              <th className="border p-2"></th>
            </tr>
          </thead>

          <tbody>
            {orders.map((o) => (
              <tr key={o.so} className="hover:bg-gray-50">
                <td className="border p-2">{o.so}</td>
                <td className="border p-2">{o.supplier}</td>
                <td className="border p-2">{o.po}</td>
                <td className="border p-2">{o.status}</td>
                <td className="border p-2">
                  {new Date(o.created_at).toLocaleDateString()}
                </td>
                <td className="border p-2 text-center">
                  <button
                    className="px-3 py-1 bg-blue-600 text-white rounded"
                    onClick={() => navigate(`/serviceorder?so=${o.so}`)}
                  >
                    Open
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
