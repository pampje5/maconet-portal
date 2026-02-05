import { useState } from "react";
import toast from "react-hot-toast";
import api from "../api";

export default function ImportDuallistPage() {
  const [file, setFile] = useState(null);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);

  async function handleUpload() {
    if (!file) {
      toast.error("Selecteer eerst een Excel bestand");
      return;
    }

    setIsImporting(true);
    setImportResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post(
        "/admin/import/duallist",
        formData
      );

      setImportResult(res.data);
      toast.success("Duallist succesvol verwerkt");
      setFile(null);
    } catch (err) {
      console.error("IMPORT ERROR:", err);

      toast.error(
        err.response?.data?.detail || "Import mislukt"
      );
    } finally {
      setIsImporting(false);
    }
  }

  return (
    <div className="max-w-xl bg-white p-6 rounded-2xl shadow">
      <h1 className="text-xl font-bold mb-4">
        Duallist importeren
      </h1>

      {/* Bestand kiezen */}
      <input
        type="file"
        accept=".xlsx,.xls,.xlsm"
        onChange={(e) => setFile(e.target.files[0])}
        className="block w-full border rounded px-3 py-2"
      />

      {/* Upload knop */}
      <button
        onClick={handleUpload}
        disabled={isImporting}
        className={`mt-4 px-4 py-2 rounded text-white w-full
          ${isImporting ? "bg-gray-400" : "bg-blue-600"}
        `}
      >
        {isImporting ? "Bezig met importeren…" : "Uploaden"}
      </button>

      {/* Spinner + status */}
      {isImporting && (
        <div className="flex items-center gap-2 text-blue-600 mt-4">
          <svg
            className="animate-spin h-5 w-5"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            />
          </svg>
          <span>Import wordt verwerkt…</span>
        </div>
      )}

      {/* Blijvend importresultaat */}
      {importResult && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="font-semibold mb-2">
            Importresultaat
          </h2>

          <ul className="text-sm space-y-1">
            <li>📄 Sheet: {importResult.sheet_used}</li>
            <li>➕ Aangemaakt: {importResult.created}</li>
            <li>🔁 Bijgewerkt: {importResult.updated}</li>
            <li>⚠️ Overgeslagen: {importResult.skipped}</li>
            <li>🧯 Dubbel in bestand: {importResult.duplicates_in_file}</li>
            <li className="font-medium mt-2">
              Totaal verwerkt: {importResult.total_processed}
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
