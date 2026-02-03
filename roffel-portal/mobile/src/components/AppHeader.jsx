import { useNavigate } from "react-router-dom";

export default function AppHeader({ title = "Maconet" }) {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-20 bg-white border-b">
      <div className="h-14 px-4 flex items-center justify-between">
        <div className="font-semibold text-lg tracking-tight">
          {title}
        </div>

        <button
          onClick={logout}
          className="text-sm text-gray-500"
        >
          Uitloggen
        </button>
      </div>
    </header>
  );
}
