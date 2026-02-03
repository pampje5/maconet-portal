import { useState } from "react";
import toast from "react-hot-toast";
import api from "../api";


export default function ImportDuallistPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  

  async function handleUpload() {
    if (!file) {
      toast.error("Selecteer eerst een Excel bestand");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post(
        `/admin/import/duallist`,
        formData    
      );

      console.log("IMPORT RESULT:", res.data);

      toast.success(
        `Import geslaagd 
Nieuw: ${res.data.created}
Bijgewerkt: ${res.data.updated}`
      );

      setFile(null);
    } catch (err) {
      console.error("IMPORT ERROR:", err);

      toast.error(
        err.response?.data?.detail ||
        "Import mislukt"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-xl font-bold mb-4">
        Duallist importeren
      </h1>

      <input
        type="file"
        accept=".xlsx,.xls,.xlsm"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}
        disabled={loading}
        className={`mt-4 px-4 py-2 rounded text-white
          ${loading ? "bg-gray-400" : "bg-blue-600"}
        `}
      >
        {loading ? "Bezig met importeren..." : "Uploaden"}
      </button>
    </div>
  );
}

