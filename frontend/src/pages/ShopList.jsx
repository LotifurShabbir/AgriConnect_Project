import { AlertCircle, Leaf, Loader2, Plus, Star, Store, X } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";

import apiClient from "../api/client";

const GRADIENTS = [
  "from-forest to-forest-light",
  "from-forest-dark to-forest",
  "from-gold-dark to-gold",
  "from-forest-light to-gold-dark",
];

export default function ShopList() {
  const [shops, setShops] = useState([]);
  const [status, setStatus] = useState("loading"); // "loading" | "success" | "error"
  const [isModalOpen, setIsModalOpen] = useState(false);

  const currentUser = JSON.parse(localStorage.getItem("agriconnect_user") || "null");
  const canCreateShop = currentUser?.role === "Farmer" || currentUser?.role === "Admin";

  const loadShops = () => {
    setStatus("loading");
    apiClient
      .get("/shops")
      .then((res) => {
        setShops(res.data);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  };

  useEffect(() => {
    loadShops();
  }, []);

  const handleCreated = (newShop) => {
    setShops((prev) => [...prev, newShop]);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-forest-dark">Shops</h2>
          <p className="text-sm text-gray-500">Browse registered farmer shops.</p>
        </div>

        {canCreateShop && (
          <button type="button" onClick={() => setIsModalOpen(true)} className="btn-primary">
            <Plus className="h-4 w-4" />
            Create New Shop
          </button>
        )}
      </div>

      {status === "loading" && (
        <div className="flex items-center gap-2 text-gray-500">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading shops...
        </div>
      )}

      {status === "error" && (
        <div className="flex items-center gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-600">
          <AlertCircle className="h-5 w-5" />
          Couldn&apos;t load shops. Is the API running at the configured VITE_API_URL?
        </div>
      )}

      {status === "success" && shops.length === 0 && (
        <div className="card flex flex-col items-center gap-2 py-12 text-center">
          <Store className="h-8 w-8 text-gray-300" />
          <p className="text-sm text-gray-500">No shops yet.</p>
        </div>
      )}

      {status === "success" && shops.length > 0 && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {shops.map((shop) => (
            <ShopCard key={shop.ShopID} shop={shop} />
          ))}
        </div>
      )}

      {isModalOpen && (
        <CreateShopModal
          farmerId={currentUser?.role === "Farmer" ? currentUser.id : null}
          onClose={() => setIsModalOpen(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}

function ShopCard({ shop }) {
  const gradient = GRADIENTS[shop.ShopID % GRADIENTS.length];

  return (
    <Link to={`/shops/${shop.ShopID}`} className="card-interactive group block overflow-hidden">
      <div className={`relative flex h-28 items-center justify-center bg-gradient-to-br ${gradient}`}>
        <Store className="h-10 w-10 text-white/25" />
        <div className="absolute -bottom-5 left-5 flex h-11 w-11 items-center justify-center rounded-xl bg-white text-forest shadow-md ring-1 ring-gray-100">
          <Leaf className="h-5 w-5" />
        </div>
      </div>

      <div className="px-5 pb-5 pt-8">
        <p className="font-semibold text-forest-dark transition-colors group-hover:text-forest">
          {shop.ShopName}
        </p>
        <div className="mt-1 flex items-center gap-1 text-sm text-gold-dark">
          <Star className="h-4 w-4 fill-gold text-gold" />
          {shop.Review.toFixed(1)}
        </div>
      </div>
    </Link>
  );
}

function CreateShopModal({ farmerId, onClose, onCreated }) {
  const [shopName, setShopName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await apiClient.post("/shops", {
        ShopName: shopName,
        FarmerID: farmerId,
      });
      toast.success(`"${res.data.ShopName}" was created!`);
      onCreated(res.data);
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create shop.");
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
          <h3 className="text-lg font-semibold text-forest-dark">Create New Shop</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="mb-1 block text-sm font-medium text-forest-dark" htmlFor="shopName">
              Shop Name
            </label>
            <input
              id="shopName"
              required
              autoFocus
              value={shopName}
              onChange={(e) => setShopName(e.target.value)}
              placeholder="e.g. Green Valley Farms"
              className="input-field"
            />
          </div>

          <div className="flex justify-end gap-2">
            <button type="button" onClick={onClose} className="btn-ghost">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary disabled:cursor-not-allowed disabled:opacity-60">
              {isSubmitting ? "Creating..." : "Create Shop"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
