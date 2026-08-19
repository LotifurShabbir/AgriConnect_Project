import { Toaster } from "react-hot-toast";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import OrderHistory from "./pages/OrderHistory";
import Register from "./pages/Register";
import ShopDetails from "./pages/ShopDetails";
import ShopList from "./pages/ShopList";

function ProtectedRoute({ children }) {
  const isAuthenticated = Boolean(localStorage.getItem("agriconnect_user"));
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            borderRadius: "12px",
            background: "#ffffff",
            color: "#0F2E20",
            boxShadow: "0 10px 25px -5px rgba(15, 46, 32, 0.15)",
            fontSize: "0.875rem",
          },
          success: { iconTheme: { primary: "#1B4332", secondary: "#ffffff" } },
          error: { iconTheme: { primary: "#dc2626", secondary: "#ffffff" } },
        }}
      />

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/shops"
          element={
            <ProtectedRoute>
              <Layout>
                <ShopList />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/shops/:shopId"
          element={
            <ProtectedRoute>
              <Layout>
                <ShopDetails />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <Layout>
                <OrderHistory />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
