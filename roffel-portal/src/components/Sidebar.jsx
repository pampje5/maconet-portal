import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMe } from "../utils/auth";

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
      <Link
        to="/dashboard"
        className={`${linkBase} ${location.pathname === "/dashboard" ? active : inactive}`}
      >
        <Home size={18} />
        Dashboard
      </Link>

      {/* Serviceorder blok */}
      <div>

        <div
          className={`${linkBase} ${location.pathname.includes("/serviceorder") ? active : inactive}`}
          onClick={() => setOpenSO(!openSO)}
        >
          <FileSpreadsheet size={18} />
          Serviceorder Sullair

          <span className="ml-auto">
            {openSO ? <ChevronDown size={16}/> : <ChevronRight size={16}/>}
          </span>
        </div>

        {openSO && (
          <div className="ml-6 mt-2 space-y-1">

            <Link
              to="/serviceorder/new"
              className={`${linkBase} ${location.pathname === "/serviceorder/new" ? active : inactive}`}
            >
              <PlusCircle size={16} />
              Nieuwe serviceorder
            </Link>

            <Link
              to="/serviceorder/list"
              className={`${linkBase} ${location.pathname === "/serviceorder/list" ? active : inactive}`}
            >
              <List size={16} />
              Overzicht
            </Link>

            <Link
              to="/serviceorder/edit"
              className={`${linkBase} ${location.pathname === "/serviceorder/edit" ? active : inactive}`}
            >
              <Edit size={16} />
              Bewerken
            </Link>

          </div>
        )}
      </div>

      {/* Instellingen */}
      
      {me && me.role !== "user" && (
      <Link
        to="/settings"
        className={`${linkBase} ${location.pathname === "/settings" ? active : inactive}`}
      >
        <Settings size={18} />
        Instellingen
      </Link>
      )}
    </div>
  );
}
