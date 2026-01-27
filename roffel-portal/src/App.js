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
import ServiceOrdersPage from "./pages/ServiceOrdersPage";
import ServiceOrderEditPage from "./pages/ServiceOrderEditPage.jsx";
import CustomersPage from "./pages/CustomersPage";
import SettingsPage from "./pages/SettingsPage";
import SullairSettingsPage from "./pages/SullairSettingsPage";
import UsersPage from "./pages/UsersPage";
import ServiceOrderNumbers from "./pages/ServiceOrderNumbers.jsx";
import PurchaseOrdersPage from "./pages/PurchaseOrderPage.jsx";
import CombineServiceOrders from "./pages/CombineServiceOrders.jsx";
import { Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";


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
                <ServiceOrdersPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/serviceorder/edit"
          element={
            <ProtectedRoute>
              <Layout>
                <ServiceOrderEditPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/serviceorder"
          element={
            <ProtectedRoute>
              <Layout>
              <ServiceOrderPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/purchaseorderpage"
          element={
            <ProtectedRoute>
              <Layout>
                <PurchaseOrdersPage/>
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/combineserviceorders"
          element={
            <ProtectedRoute>
              <Layout>
                <CombineServiceOrders/>
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/serviceorder-numbers"
          element={
            <ProtectedRoute>
              <Layout>
                <ServiceOrderNumbers/>
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
            <ProtectedRoute minRole="admin">
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

        <Route
          path="/settings/users"
          element={
            <ProtectedRoute>
              <Layout>
                <UsersPage />
              </Layout>
            </ProtectedRoute>
          }
        />


      </Routes>
      <Toaster position="bottom-right" />
      
    </BrowserRouter>
  );
}

