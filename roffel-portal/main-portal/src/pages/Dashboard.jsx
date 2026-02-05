import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMe } from "../utils/auth";

import sullairImage from "./images/Sullair.png";
import maconetImage from "./images/Maconet.png";
import roffeloacImage from "./images/roffeloac.png";


export default function Dashboard() {

  const [me, setMe] = useState(null);

  useEffect(() => {
    getMe().then(setMe);
  }, []);

  
  function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">

      {/* HEADER */}
      <div className="flex items-center justify-between mb-8">

        <div className="flex items-center gap-4">
          <img src={maconetImage} alt="Maconet" className="h-12" />
          <img src={sullairImage} alt="Sullair" className="h-10" />
        </div>

        <h1 className="text-3xl font-bold">
          Maconet Portal
        </h1>

        <button
          onClick={logout}
          className="px-4 py-2 rounded bg-red-500 text-white"
        >
          Uitloggen
        </button>
      </div>

      {/* TEGELS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* Serviceorder */}
        <Link
          to="/serviceorder/new"
          className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
          <h2 className="text-xl font-semibold mb-2">Serviceorders</h2>
          <p className="text-gray-600">
            Serviceorders aanmaken en beheren
          </p>
        </Link>

        {/* Serviceorder Algemeen*/}

        <Link
          to="/serviceorder-numbers"
          className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
            <h2 className="text-xl font-semibold mb-2">Serviceorders Algemeen</h2>
            <p className="text-gray-600">
              Algemene Serviceorders en werkplaatsnummers
            </p>
        </Link>

        <Link
          to="/purchaseorderpage"
          className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
            <h2 className="text-xl font-semibold mb-2">Inkooporders Algemeen</h2>
            <p className="text-gray-600">
              Algemene Inkoopnummers
            </p>
        </Link>

          
        {/* Klantenbeheer */}
        <Link
          to="/customers"
          className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
          <h2 className="text-xl font-semibold mb-2">Klantenbeheer</h2>
          <p className="text-gray-600">
            Klanten en contactpersonen beheren
          </p>
        </Link>

        {/* Leverancierbeheer */}
        <Link
        to="/supplierspage"
        className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
          <h2 className="text-xl font-semibold mb-2">Leverancierbeheer</h2>
          <p className="text-gray-600">
            leveranciers en contactpersonen beheren
          </p>
        </Link>

        {/* Instellingen */}
       {me && me.role !== "user" && (
        <Link
          to="/settings"
          className="p-6 bg-white rounded-2xl shadow hover:shadow-lg transition block"
        >
          <h2 className="text-xl font-semibold mb-2">Instellingen</h2>
          <p className="text-gray-600">
            Portal- en Sullair instellingen
          </p>
        </Link>
      )}


      </div>

      {/* FOOTER */}
      <div className="mt-12 text-center text-sm text-gray-500">
        Created by
        <img src={roffeloacImage} alt="Roffel" className="h-8 inline ml-2" />
      </div>

    </div>
  );
}
