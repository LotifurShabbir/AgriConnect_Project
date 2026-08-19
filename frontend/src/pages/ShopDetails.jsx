import { AlertCircle, ArrowLeft, Loader2, Package, Plus, Star, Store, X } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link, useParams } from "react-router-dom";

import apiClient from "../api/client";

const CATEGORIES = ["Fruits & Vegetables", "Grains", "Meat"];

const CATEGORY_STYLES = {
  "Fruits & Vegetables": "bg-forest/10 text-forest",
  Grains: "bg-gold/20 text-gold-dark",
  Meat: "bg-red-50 text-red-600",
};

export default function ShopDetails() {
  const { shopId } = useParams();

  const [shop, setShop] = useState(null);
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("loading"); // "loading" | "success" | "error"
  const [isModalOpen, setIsModalOpen] = useState(false);

  const currentUser = JSON.parse(localStorage.getItem("agriconnect_user") || "null");
  const canManageItems = currentUser?.role === "Farmer" || currentUser?.role === "Admin";

  const loadData = () => {
    setStatus("loading");
    Promise.all([
      apiClient.get(`/shops/${shopId}`),
      apiClient.get(`/shops/${shopId}/items`),
    ])
      .then(([shopRes, itemsRes]) => {
        setShop(shopRes.data);
        setItems(itemsRes.data);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shopId]);

  const handleItemCreated = (newItem) => {
    setItems((prev) => [...prev, newItem]);
  };

  return (
    <div className="space-y-6">
      <Link
        to="/shops"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-forest"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Shops
      </Link>

      {status === "loading" && (
        <div className="flex items-center gap-2 text-gray-500">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading shop...
        </div>
      )}

      {status === "error" && (
        <div className="flex items-center gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-600">
          <AlertCircle className="h-5 w-5" />
          Couldn&apos;t load this shop. It may not exist, or the API may be unreachable.
        </div>
      )}

      {status === "success" && shop && (
        <>
          <div className="card flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-forest/10 text-forest">
                <Store className="h-7 w-7" />
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-forest-dark">{shop.ShopName}</h2>
                <div className="mt-1 flex items-center gap-1 text-sm text-gold-dark">
                  <Star className="h-4 w-4 fill-gold text-gold" />
                  {shop.Review.toFixed(1)} rating
                </div>
              </div>
            </div>

            {canManageItems && (
              <button type="button" onClick={() => setIsModalOpen(true)} className="btn-primary">
                <Plus className="h-4 w-4" />
                Add Item
              </button>
            )}
          </div>

          <div>
            <h3 className="mb-3 text-lg font-semibold text-forest-dark">Inventory</h3>

            {items.length === 0 ? (
              <div className="card flex flex-col items-center gap-2 py-12 text-center">
                <Package className="h-8 w-8 text-gray-300" />
                <p className="text-sm text-gray-500">No items in this shop yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {items.map((item) => (
                  <div key={item.ItemID} className="card space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-semibold text-forest-dark">{item.Name}</p>
                      <span className={`badge ${CATEGORY_STYLES[item.Category] ?? "bg-gray-100 text-gray-500"}`}>
                        {item.Category}
                      </span>
                    </div>
                    <div className="flex items-baseline justify-between">
                      <p className="text-xl font-semibold text-forest">${item.Price.toFixed(2)}</p>
                      <p className="text-sm text-gray-500">{item.Stock} in stock</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {isModalOpen && (
        <AddItemModal
          shopId={shopId}
          onClose={() => setIsModalOpen(false)}
          onCreated={handleItemCreated}
        />
      )}
    </div>
  );
}

function AddItemModal({ shopId, onClose, onCreated }) {
  const [form, setForm] = useState({ Name: "", Category: CATEGORIES[0], Price: "", Stock: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await apiClient.post(`/shops/${shopId}/items`, {
        Name: form.Name,
        Category: form.Category,
        Price: Number(form.Price),
        Stock: Number(form.Stock),
      });
      toast.success(`"${res.data.Name}" added to inventory!`);
      onCreated(res.data);
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to add item.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="animate-fade-in fixed inset-0 z-50 flex items-center justify-center bg-forest-dark/40 p-4"
      onClick={onClose}
    >
      <div
        className="animate-scale-in w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-5 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-forest-dark">Add Item</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="Name">
              Item Name
            </label>
            <input
              id="Name"
              name="Name"
              required
              autoFocus
              value={form.Name}
              onChange={handleChange}
              placeholder="e.g. Organic Tomatoes"
              className="input-field"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="Category">
              Category
            </label>
            <select
              id="Category"
              name="Category"
              value={form.Category}
              onChange={handleChange}
              className="input-field bg-white"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="Price">
                Price ($)
              </label>
              <input
                id="Price"
                name="Price"
                type="number"
                min="0"
                step="0.01"
                required
                value={form.Price}
                onChange={handleChange}
                className="input-field"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="Stock">
                Stock
              </label>
              <input
                id="Stock"
                name="Stock"
                type="number"
                min="0"
                step="1"
                required
                value={form.Stock}
                onChange={handleChange}
                className="input-field"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <button type="button" onClick={onClose} className="btn-ghost">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary disabled:cursor-not-allowed disabled:opacity-60">
              {isSubmitting ? "Adding..." : "Add Item"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
