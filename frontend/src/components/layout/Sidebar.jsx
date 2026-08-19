import { ClipboardList, Leaf, LayoutDashboard, Store } from "lucide-react";
import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/shops", label: "Shops", icon: Store },
  { to: "/orders", label: "Orders", icon: ClipboardList },
];

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-20 flex w-64 flex-col bg-forest text-cream">
      <div className="flex items-center gap-2 px-6 py-6">
        <Leaf className="h-7 w-7 text-gold" />
        <span className="text-xl font-semibold tracking-wide text-white">AgriConnect</span>
      </div>

      <nav className="mt-4 flex-1 space-y-1 px-3">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-forest-light text-gold"
                  : "text-cream/80 hover:bg-forest-light hover:text-white"
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-forest-light px-6 py-4 text-xs text-cream/60">
        AgriConnect &middot; Eco-friendly commerce
      </div>
    </aside>
  );
}
