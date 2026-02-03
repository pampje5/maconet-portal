import { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";

const NavigationGuardContext = createContext(null);
export const useNavigationGuard = () => useContext(NavigationGuardContext);

export function NavigationGuardProvider({ children }) {
  const navigate = useNavigate();

  const [isBlocked, setIsBlocked] = useState(false);
  const [onBlockedNavigate, setOnBlockedNavigate] = useState(null);

  function guardedNavigate(to) {
    if (!isBlocked) {
      navigate(to);
      return;
    }
    // blok actief -> laat pagina (ServiceOrderPage) bepalen wat er gebeurt
    if (onBlockedNavigate) onBlockedNavigate(to);
  }

  // Pages kunnen dit zetten als ze “dirty” zijn
  function registerBlocker(blocked, handler) {
    setIsBlocked(blocked);
    setOnBlockedNavigate(() => handler);
  }

  return (
    <NavigationGuardContext.Provider value={{ guardedNavigate, registerBlocker }}>
      {children}
    </NavigationGuardContext.Provider>
  );
}
