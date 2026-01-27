import Sidebar from "./Sidebar";
import { NavigationGuardProvider } from "../context/NavigationGuardContext.jsx";

export default function Layout({ children }) {
  return (
    <NavigationGuardProvider>
      <div className="flex">
      <Sidebar />

      {/* MAIN CONTENT */}
      <div className="flex-1 bg-gray-100 min-h-screen p-6 relative">
        {children}
      </div>
    </div>
    </NavigationGuardProvider>
    
  );
}
