import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export default function SullairSettingsPage() {

  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [form, setForm] = useState({
    contact_name: "",
    email: ""
  });

  function updateField(k, v) {
    setForm(prev => ({ ...prev, [k]: v }));
  }

  async function loadSettings() {
    try {
      const res = await axios.get(`${API}/sullair/settings`, {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`
        }
      });

      if (res.data) setForm(res.data);

    } catch (err) {
      console.error(err);
    }
  }

  async function saveSettings() {
    try {
      await axios.post(`${API}/sullair/settings`, form, {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`
        }
      });

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
