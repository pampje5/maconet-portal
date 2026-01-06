import { Link } from "react-router-dom";

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">

      <h1 className="text-2xl font-bold mb-6">
        Instellingen
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* ACTIEF */}
        <Link
          to="/settings/sullair"
          className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
          <h2 className="text-xl font-semibold mb-2">Sullair gegevens</h2>
          <p className="text-gray-600">
            Standaard contact & e-mail voor aanvragen
          </p>
        </Link>

        {/* UITGEGRIJSDE TEGELS */}
        <div className="p-6 bg-gray-200 rounded-2xl opacity-60">
          <h2 className="text-xl font-semibold mb-2">Gebruikersbeheer</h2>
          <p>Coming soon…</p>
        </div>

        <div className="p-6 bg-gray-200 rounded-2xl opacity-60">
          <h2 className="text-xl font-semibold mb-2">Overige instellingen</h2>
          <p>Coming soon…</p>
        </div>
      </div>
    </div>
  );
}
