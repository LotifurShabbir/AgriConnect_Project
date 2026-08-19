import { Leaf, Lock, Mail } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { Link, useNavigate } from "react-router-dom";

import apiClient from "../api/client";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await apiClient.post("/auth/login", form);
      localStorage.setItem("agriconnect_user", JSON.stringify(res.data));
      toast.success(`Welcome back, ${res.data.name}!`);
      navigate("/");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Invalid email or password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-cream px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-forest text-gold">
            <Leaf className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-semibold text-forest-dark">AgriConnect</h1>
          <p className="text-sm text-gray-500">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="email">
              Email
            </label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                id="email"
                name="email"
                type="email"
                required
                value={form.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="input-field pl-10"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="password">
              Password
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                id="password"
                name="password"
                type="password"
                required
                value={form.password}
                onChange={handleChange}
                placeholder="********"
                className="input-field pl-10"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Signing in..." : "Sign In"}
          </button>

          <p className="text-center text-sm text-gray-500">
            Don&apos;t have an account?{" "}
            <Link to="/register" className="font-medium text-forest hover:text-forest-light">
              Register
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
