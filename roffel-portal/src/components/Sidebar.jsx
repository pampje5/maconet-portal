import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMe } from "../utils/auth";
import { useNavigationGuard } from "../context/NavigationGuardContext";
import FEATURES from "../config/features";

import {
  Home,
  Settings,
  FileSpreadsheet,
  ChevronDown,
  ChevronRight,
  PlusCircle,
  List,
  Edit
} from "lucide-react";

export default function Sidebar() {

  const location = useLocation();
  const [openSO, setOpenSO] = useState(true);
  const [me, setMe] = useState(null);
  const { guardedNavigate } = useNavigationGuard()
  

  useEffect(() => {
    getMe().then(setMe);
  }, []);

  const linkBase =
    "flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer";

  const active = "bg-blue-600 text-white";
  const inactive = "text-gray-700 hover:bg-gray-200";

  return (
    <div className="w-64 bg-white shadow-lg min-h-screen p-4 space-y-3">

      {/* Logo / Titel */}
      <div className="text-xl font-bold mb-4">
        Maconet Portal
      </div>

      {/* Dashboard */}
      <div
        className={`${linkBase} ${location.pathname === "/dashboard" ? active : inactive}`}
        onClick={() => guardedNavigate("/dashboard")}
      >
        <Home size={18} />
        Dashboard
      </div>

      {/* Serviceorder algemeen */}
      <div
        className={`${linkBase} ${location.pathname === "/serviceorder-numbers" ? active : inactive}`}
        onClick={() => guardedNavigate("/serviceorder-numbers")}
      >
        <List size={18} />
        Serviceorder algemeen
      </div>

      {/* Inkooporder algemeen */}
      <div
        className={`${linkBase} ${location.pathname === "/purchaseorderpage" ? active : inactive}`}
        onClick={() => guardedNavigate("/purchaseorderpage")}
      >
        <List size={18} />
        Inkooporder Algemeen
      </div>

     {/* Serviceorder blok */}
      <div>
        {/* Hoofdknop (alleen openen/sluiten, GEEN navigatie) */}
        <div
          className={`${linkBase} ${
            location.pathname.startsWith("/serviceorder/")
              ? active
              : inactive
          }`}
          onClick={() => setOpenSO(!openSO)}
        >
          <FileSpreadsheet size={18} />
          Serviceorder Sullair

          <span className="ml-auto">
            {openSO ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </span>
        </div>

        {/* Submenu */}
        {openSO && (
          <div className="ml-6 mt-2 space-y-1">

            <div
              className={`${linkBase} ${
                location.pathname === "/serviceorder/new" ? active : inactive
              }`}
              onClick={() => guardedNavigate("/serviceorder/new")}
            >
              <PlusCircle size={16} />
              Nieuwe serviceorder
            </div>

            <div
              className={`${linkBase} ${
                location.pathname === "/serviceorder/list" ? active : inactive
              }`}
              onClick={() => guardedNavigate("/serviceorder/list")}
            >
              <List size={16} />
              Overzicht
            </div>

            <div
              className={`${linkBase} ${
                location.pathname === "/serviceorder/edit" ? active : inactive
              }`}
              onClick={() => guardedNavigate("/serviceorder/edit")}
            >
              <Edit size={16} />
              Bewerken
            </div>

            {FEATURES.COMBINE_SERVICEORDERS &&(
            <div
              className={`${linkBase} ${
                location.pathname === "/combineserviceorders" ? active : inactive
              }`}
              onClick={() => guardedNavigate("/combineserviceorders")}
            >
              <List size={16} />
              Combineer serviceorders
            </div>
            )}

          </div>
        )}
      </div>


      {/* Instellingen */}
      
      {me && me.role !== "user" && (
      <div
        className={`${linkBase} ${location.pathname === "/settings" ? active : inactive}`}
        onClick={() => guardedNavigate("/settings")}
      >
        <Settings size={18} />
        Instellingen
      </div>
      
      )}
    </div>
  );
}
