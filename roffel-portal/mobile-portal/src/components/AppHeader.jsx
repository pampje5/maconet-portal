import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Header({ title }) {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <header className="h-14 bg-blue-600 text-white flex items-center justify-between px-4 shadow">
      <h1 className="font-semibold text-lg">{title}</h1>

      <button onClick={logout} className="opacity-90 hover:opacity-100">
        <LogOut size={20} />
      </button>
    </header>
  );
}
