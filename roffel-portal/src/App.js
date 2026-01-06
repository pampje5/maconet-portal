import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import ServiceOrderPage from "./pages/ServiceOrderPage";
import CustomersPage from "./pages/CustomersPage";
import SettingsPage from "./pages/SettingsPage";
import SullairSettingsPage from "./pages/SullairSettingsPage";
import { Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";

function Placeholder({title}) {
  return <h1 className="text-2xl">{title}</h1>
}


export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Navigate to="/login" />} />


        <Route path="/login" element={<LoginPage />} />

        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password/:token" element={<ResetPasswordPage />} />


        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/serviceorder/new"
          element={
            <ProtectedRoute>
              <Layout>
                <ServiceOrderPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/serviceorder/list"
          element={
            <ProtectedRoute>
              <Layout>
                <Placeholder title={"Overzicht serviceorders"} />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/serviceorder/edit"
          element={
            <ProtectedRoute>
              <Layout>
                <Placeholder title="Bestaande serviceorder bewerken" />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/customers"
          element={
            <ProtectedRoute>
              <Layout>
                <CustomersPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <SettingsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/settings/sullair"  
          element={
            <ProtectedRoute>
              <Layout>
                <SullairSettingsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

      </Routes>
      <Toaster position="bottom-right" />
      
    </BrowserRouter>
  );
}

