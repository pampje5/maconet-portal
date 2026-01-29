import { useState } from "react";
import api from "../api"
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(e) {
  e.preventDefault();

  try {
    setError("");

    const form = new URLSearchParams();
    form.append("username", email);   // OAuth2 expects "username"
    form.append("password", password);

    const res = await api.post(
      "/auth/login",
      form,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    localStorage.setItem("token", res.data.access_token);
    navigate("/dashboard");
  } catch (err) {
    console.error(err);
    setError("Login mislukt. Controleer e-mail en wachtwoord.");
  }
}


  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-md">

        <h1 className="text-2xl font-bold mb-6 text-center">
          Maconet Portal — Login
        </h1>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">

          <div>
            <label className="block mb-1 font-medium">E-mail</label>
            <input
              type="email"
              className="w-full border rounded-lg px-3 py-2"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Wachtwoord</label>
            <input
              type="password"
              className="w-full border rounded-lg px-3 py-2"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="text-right">
            <a href="/forgot-password" className="text-sm text-blue-600 hover:underline">
              Wachtwoord vergeten?
            </a>
          </div>

          <button
            type="submit"
            className="w-full py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 transition">
            Inloggen
          </button>
        </form>

      </div>
    </div>
  );
}
