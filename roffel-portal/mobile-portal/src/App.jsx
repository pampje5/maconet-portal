import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import ProtectedRoute from "./components/ProtectedRoute";

import LoginPage from "./pages/LoginPage";
import ServiceOrderNumbers from "./pages/MobileServiceOrderNumbers";

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" />

      <Routes>
        {/* Login – publiek */}
        <Route path="/login" element={<LoginPage />} />

        {/* App root – beschermd */}
        <Route
          path="/"
          element={
            <ProtectedRoute minRole="user">
              <Navigate to="/serviceorders" replace />
            </ProtectedRoute>
          }
        />

        {/* Serviceorders – protected */}
        <Route
          path="/serviceorders"
          element={
            <ProtectedRoute minRole="user">
              <ServiceOrderNumbers />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
