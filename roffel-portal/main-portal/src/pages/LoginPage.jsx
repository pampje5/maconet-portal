import { useState } from "react";
import api from "../api"
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, AlertTriangle } from "lucide-react";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [capsLockOn, setCapsLockOn] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);


  const handlePasswordKey = (e) => {
    const caps = e.getModifierState && e.getModifierState("CapsLock");
    setCapsLockOn(caps);
  };

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

          {/* Email */}
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

          {/* Password */}
          <div>
            <label className="block mb-1 font-medium">Wachtwoord</label>

            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                className="w-full border rounded-lg px-3 py-2 pr-10"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyUp={handlePasswordKey}
                onFocus={() => setPasswordFocused(true)}
                onBlur={() => {
                  setPasswordFocused(false);
                  setCapsLockOn(false);
                }}
                required
              />

              {/* Eye toggle */}
              <button
                type="button"
                onClick={() => setShowPassword(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>

              {/* Caps Lock tooltip */}
              {capsLockOn && passwordFocused && (
                <div className="absolute left-0 top-full mt-2 flex items-center gap-2 rounded-md bg-yellow-100 px-3 py-2 text-sm text-yellow-800 shadow">
                  <AlertTriangle size={16} />
                  Caps Lock staat aan
                </div>
              )}
            </div>
          </div>

          <div className="text-right">
            <a
              href="/forgot-password"
              className="text-sm text-blue-600 hover:underline"
            >
              Wachtwoord vergeten?
            </a>
          </div>

          <button
            type="submit"
            className="w-full py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 transition"
          >
            Inloggen
          </button>

        </form>
      </div>
    </div>
  );

}
