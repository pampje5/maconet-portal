import React from "react";

export default function StartPage({ onSelect }) {
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-10 w-[480px] text-center">
        
        <h1 className="text-3xl font-bold text-white mb-2">
          Roffel OA&C Tools
        </h1>

        <p className="text-slate-300 mb-8">
          Aanvraag • Offerte • Bestellen • Bevestigen
        </p>

        <div className="space-y-3">
          <button
            className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold"
            onClick={() => onSelect("hoofd")}
          >
            Aanvraag / Offerte / Bestellen
          </button>

          <button
            className="w-full py-3 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-semibold"
            onClick={() => onSelect("overzicht")}
          >
            Serviceorder overzicht
          </button>

          <button
            className="w-full py-3 rounded-xl bg-red-500 hover:bg-red-600 text-white font-semibold"
            onClick={() => window.close()}
          >
            Sluiten
          </button>
        </div>
      </div>
    </div>
  );
}
