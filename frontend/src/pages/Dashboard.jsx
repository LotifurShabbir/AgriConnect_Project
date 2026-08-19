import { ClipboardList, DollarSign, Store, Truck } from "lucide-react";

const stats = [
  { label: "Active Shops", value: "24", icon: Store },
  { label: "Orders Today", value: "132", icon: ClipboardList },
  { label: "Deliveries In Transit", value: "18", icon: Truck },
  { label: "Revenue (This Month)", value: "$8,420", icon: DollarSign },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-forest-dark">Dashboard</h2>
        <p className="text-sm text-gray-500">Overview of AgriConnect activity.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <div key={label} className="card flex items-center gap-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-forest/10 text-forest">
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{label}</p>
              <p className="text-xl font-semibold text-forest-dark">{value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="mb-2 text-base font-semibold text-forest-dark">Getting started</h3>
        <p className="text-sm text-gray-500">
          Connect this dashboard to live data via{" "}
          <code className="rounded bg-cream px-1.5 py-0.5">src/api/client.js</code>.
        </p>
      </div>
    </div>
  );
}
