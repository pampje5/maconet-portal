import { useState, useEffect } from "react";
import api from "../api";
import toast from "react-hot-toast";

export default function SullairSettingsPage() {

  const [form, setForm] = useState({
    contact_name: "",
    email: ""
  });

  function updateField(k, v) {
    setForm(prev => ({ ...prev, [k]: v }));
  }

  async function loadSettings() {
    try {
      const res = await api.get("/sullair/settings");

      if (res.data) setForm(res.data);

    } catch (err) {
      console.error(err);
    }
  }

  async function saveSettings() {
    try {
      await api.post("/sullair/settings", form);

      toast.success("Sullair instellingen opgeslagen");
    } catch (err) {
      toast.error("Opslaan mislukt");
    }
  }

  useEffect(() => {
    loadSettings();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">

      <h1 className="text-2xl font-bold mb-6">
        Sullair instellingen
      </h1>

      <div className="bg-white rounded-2xl shadow p-6 w-full max-w-xl">

        <label className="font-medium">Contactpersoon</label>
        <input
          className="w-full border rounded px-3 py-2 mb-4"
          value={form.contact_name}
          onChange={e => updateField("contact_name", e.target.value)}
        />

        <label className="font-medium">E-mail</label>
        <input
          className="w-full border rounded px-3 py-2 mb-4"
          value={form.email}
          onChange={e => updateField("email", e.target.value)}
        />

        <button
          className="px-6 py-2 bg-green-600 text-white rounded"
          onClick={saveSettings}
        >
          Opslaan
        </button>

      </div>
    </div>
  );
}
