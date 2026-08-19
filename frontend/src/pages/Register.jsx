import { Leaf } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { Link, useNavigate } from "react-router-dom";

import apiClient from "../api/client";

const ROLES = [
  { value: "Farmer", label: "Farmer", endpoint: "/users/farmers" },
  { value: "Customer", label: "Customer", endpoint: "/users/customers" },
  { value: "DeliveryMan", label: "Delivery Person", endpoint: "/users/delivery-men" },
];

const initialForm = {
  role: "Customer",
  Name: "",
  Email: "",
  password: "",
  Phone: "",
  Address: "",
  Bio: "",
  ShopID: "",
  VehicleNo: "",
};

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const selectedRole = ROLES.find((r) => r.value === form.role);
    const payload = {
      Name: form.Name,
      Email: form.Email,
      password: form.password,
      Address: form.Address || null,
      Phone: form.Phone || null,
    };
    if (form.role === "Farmer") {
      payload.Bio = form.Bio || null;
      payload.ShopID = form.ShopID ? Number(form.ShopID) : null;
    }
    if (form.role === "DeliveryMan") {
      payload.VehicleNo = form.VehicleNo || null;
    }

    try {
      await apiClient.post(selectedRole.endpoint, payload);
      toast.success("Account created successfully! Please sign in.");
      navigate("/login");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-cream px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-forest text-gold">
            <Leaf className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-semibold text-forest-dark">Create your account</h1>
          <p className="text-sm text-gray-500">Join the AgriConnect community</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="role">
              I am a
            </label>
            <select
              id="role"
              name="role"
              value={form.role}
              onChange={handleChange}
              className="input-field bg-white"
            >
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          <Field label="Full Name" name="Name" value={form.Name} onChange={handleChange} required />
          <Field label="Email" name="Email" type="email" value={form.Email} onChange={handleChange} required />
          <Field
            label="Password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required
          />
          <Field label="Phone" name="Phone" value={form.Phone} onChange={handleChange} />
          <Field label="Address" name="Address" value={form.Address} onChange={handleChange} />

          {form.role === "Farmer" && (
            <>
              <Field label="Bio" name="Bio" value={form.Bio} onChange={handleChange} textarea />
              <Field
                label="Shop ID (optional — leave blank if you don't have one yet)"
                name="ShopID"
                type="number"
                value={form.ShopID}
                onChange={handleChange}
              />
            </>
          )}

          {form.role === "DeliveryMan" && (
            <Field label="Vehicle No." name="VehicleNo" value={form.VehicleNo} onChange={handleChange} />
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Creating account..." : "Create Account"}
          </button>

          <p className="text-center text-sm text-gray-500">
            Already have an account?{" "}
            <Link to="/login" className="font-medium text-forest hover:text-forest-light">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

function Field({ label, name, value, onChange, type = "text", required = false, textarea = false }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor={name}>
        {label}
      </label>
      {textarea ? (
        <textarea id={name} name={name} value={value} onChange={onChange} rows={3} className="input-field" />
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          required={required}
          value={value}
          onChange={onChange}
          className="input-field"
        />
      )}
    </div>
  );
}
