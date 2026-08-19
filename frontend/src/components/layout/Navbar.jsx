import { Bell, LogOut, Search, User as UserIcon } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  const storedUser = localStorage.getItem("agriconnect_user");
  const user = storedUser ? JSON.parse(storedUser) : null;

  const handleLogout = () => {
    localStorage.removeItem("agriconnect_user");
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-gray-100 bg-white px-6 shadow-sm">
      <h1 className="text-lg font-semibold text-forest-dark">AgriConnect</h1>

      <div className="flex flex-1 items-center justify-center px-8">
        <div className="relative w-full max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search shops, items, orders..."
            className="w-full rounded-full border border-gray-200 bg-cream py-2 pl-10 pr-4 text-sm text-forest-dark placeholder:text-gray-400 focus:border-forest-light focus:outline-none focus:ring-2 focus:ring-forest-light/30"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          className="relative rounded-full p-2 text-gray-500 hover:bg-cream hover:text-forest"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-gold" />
        </button>

        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-forest text-gold">
            <UserIcon className="h-5 w-5" />
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium leading-tight text-forest-dark">{user?.name ?? "Guest"}</p>
            <p className="text-xs leading-tight text-gray-400">{user?.role ?? ""}</p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-gray-500 transition-colors hover:bg-red-50 hover:text-red-600"
        >
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
}
