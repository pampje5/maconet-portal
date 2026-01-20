import { useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";

const API = "http://127.0.0.1:8000";

export default function CreateUserModal({ onClose, onCreated }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("user");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      await axios.post(
        `${API}/users/create`,
        { email, role },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      toast.success("Gebruiker aangemaakt (reset verplicht)");
      onCreated();     // users opnieuw laden
      onClose();       // modal sluiten
    } catch (err) {
      console.error(err);
      toast.error("Aanmaken mislukt");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">

        <h2 className="text-xl font-bold mb-4">
          Nieuwe gebruiker
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">

          <div>
            <label className="block text-sm font-medium mb-1">
              E-mail
            </label>
            <input
              type="email"
              required
              className="w-full border rounded-lg px-3 py-2"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Rol
            </label>
            <select
              className="w-full border rounded-lg px-3 py-2"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
              <option value="designer">Designer</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-gray-200"
            >
              Annuleren
            </button>

            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white disabled:opacity-50"
            >
              {loading ? "Bezig…" : "Aanmaken"}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}
