import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ServiceOrderEditPage() {
  const [so, setSo] = useState("");
  const navigate = useNavigate();

  function openOrder() {
    if (!so.trim()) return;
    navigate(`/serviceorder?so=${so}&mode=edit`);
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="bg-white max-w-lg mx-auto p-6 rounded-xl shadow">
        <h1 className="text-xl font-bold mb-4">
          Serviceorder bewerken
        </h1>

        <p className="text-sm text-gray-600 mb-4">
          Vul het serviceordernummer in dat je wilt bewerken.
        </p>

        <input
          className="w-full border rounded px-3 py-2 mb-4"
          placeholder="Bijv. SO-240315"
          value={so}
          onChange={(e) => setSo(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && openOrder()}
        />

        <div className="flex justify-end gap-2">
          <button
            className="px-4 py-2 bg-gray-400 rounded"
            onClick={() => setSo("")}
          >
            Wissen
          </button>

          <button
            className="px-4 py-2 bg-blue-600 text-white rounded"
            onClick={openOrder}
          >
            Open
          </button>
        </div>
      </div>
    </div>
  );
}
