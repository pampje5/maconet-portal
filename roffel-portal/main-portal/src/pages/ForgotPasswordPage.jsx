import { useState } from "react";
import api from "../api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post("/auth/request-password-reset", {
        email,
      });
    } catch (err) {
      // Bewust geen foutmelding tonen (security)
      console.error("Password reset request failed", err);
    } finally {
      setSent(true);
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-md">
        <h1 className="text-xl font-bold mb-4">Wachtwoord vergeten</h1>

        {sent ? (
          <div className="text-green-700">
            Als dit e-mailadres bij ons bekend is, ontvang je binnen enkele
            minuten een e-mail met een link om je wachtwoord opnieuw in te
            stellen.
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <input
              type="email"
              className="w-full border rounded px-3 py-2"
              placeholder="E-mailadres"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
              disabled={loading}
            >
              {loading ? "Bezig..." : "Reset link aanvragen"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
