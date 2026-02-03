import { useState } from "react";
import api from "../api";

export default function ForgotPasswordPage() {

  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  async function submit(e) {
    e.preventDefault();

    await api.post("/auth/request-password-reset", {
      email
    });

    setSent(true);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <div className="bg-white p-8 rounded-xl shadow w-full max-w-md">

        <h1 className="text-xl font-bold mb-4">Wachtwoord vergeten</h1>

        {sent ? (
          <div className="text-green-700">
            Als het e-mailadres bestaat is een link verzonden.
            Kijk in de backend console voor nu 😉
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">

            <input
              type="email"
              className="w-full border rounded px-3 py-2"
              placeholder="E-mail"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />

            <button className="w-full bg-blue-600 text-white py-2 rounded">
              Reset link aanvragen
            </button>

          </form>
        )}

      </div>
    </div>
  );
}
