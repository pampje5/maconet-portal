import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import api from "../api";

export default function ResetPasswordPage() {

  const { token } = useParams();
  const navigate = useNavigate();

  const [pwd, setPwd] = useState("");
  const [done, setDone] = useState(false);

  async function submit(e) {
    e.preventDefault();

    await api.post("/auth/reset-password", {
      token: token,
      password: pwd
    });

    setDone(true);

    setTimeout(() => navigate("/login"), 2000);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <div className="bg-white p-8 rounded-xl shadow w-full max-w-md">

        <h1 className="text-xl font-bold mb-4">Nieuw wachtwoord</h1>

        {done ? (
          <div className="text-green-700">
            Wachtwoord gewijzigd ✔ Je wordt doorgestuurd…
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">

            <input
              type="password"
              className="w-full border rounded px-3 py-2"
              placeholder="Nieuw wachtwoord"
              value={pwd}
              onChange={e => setPwd(e.target.value)}
              required
            />

            <button className="w-full bg-green-600 text-white py-2 rounded">
              Opslaan
            </button>

          </form>
        )}

      </div>
    </div>
  );
}
