import { Link } from "react-router-dom";
import { LogOut, FileText, Users, Settings } from "lucide-react";

export default function Dashboard() {

  function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  return (
    <div className="min-h-screen bg-gray-50">

      {/* HEADER */}
      <div className="flex justify-between items-center p-6 border-b bg-white">
        <h1 className="text-2xl font-bold">
          Roffel Portal — Dashboard
        </h1>

        <button
          onClick={logout}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 text-white hover:bg-red-700"
        >
          <LogOut size={18} />
          Uitloggen
        </button>
      </div>

      {/* CONTENT */}
      <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* SERVICEORDERS */}
        <Link
          to="/serviceorder"
          className="p-6 rounded-2xl bg-white shadow hover:shadow-lg transition cursor-pointer flex flex-col gap-3"
        >
          <FileText size={28} />
          <div className="text-xl font-semibold">Nieuwe serviceorder</div>
          <div className="text-gray-500 text-sm">
            Aanmaken en beheren van serviceorders
          </div>
        </Link>

        {/* KLANTEN */}
        <Link
          to="/customers"
          className="p-6 rounded-2xl bg-white shadow hover:shadow-lg transition cursor-pointer flex flex-col gap-3"
        >
          <Users size={28} />
          <div className="text-xl font-semibold">Klantenbeheer</div>
          <div className="text-gray-500 text-sm">
            Klanten, contacten en prijstypen beheren
          </div>
        </Link>

        {/* INSTELLINGEN */}
        <div className="p-6 rounded-2xl bg-white shadow opacity-50 cursor-not-allowed flex flex-col gap-3">
          <Settings size={28} />
          <div className="text-xl font-semibold">Instellingen</div>
          <div className="text-gray-500 text-sm">
            (binnenkort beschikbaar)
          </div>
        </div>

      </div>

      {/* FOOTER */}
      <div className="text-center text-sm text-gray-500 py-4">
        Created by Roffel Organisatie Advies & Coaching
      </div>

    </div>
  );
}
