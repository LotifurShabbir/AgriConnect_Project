import { Clock, PackageCheck, Truck } from "lucide-react";

const statusStyles = {
  Delivered: "bg-forest/10 text-forest",
  "In Transit": "bg-gold/20 text-gold-dark",
  Pending: "bg-gray-100 text-gray-500",
};

const statusIcons = { Delivered: PackageCheck, "In Transit": Truck, Pending: Clock };

const mockOrders = [
  { OrderID: 1042, OrderDate: "2026-08-15", Status: "Delivered", PaymentMethod: "Card", TotalAmount: 54.2 },
  { OrderID: 1041, OrderDate: "2026-08-14", Status: "In Transit", PaymentMethod: "Cash on Delivery", TotalAmount: 21.0 },
  { OrderID: 1040, OrderDate: "2026-08-12", Status: "Pending", PaymentMethod: "Card", TotalAmount: 88.5 },
];

export default function OrderHistory() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-forest-dark">Order History</h2>
        <p className="text-sm text-gray-500">
          Wire this table to{" "}
          <code className="rounded bg-cream px-1.5 py-0.5">GET /orders/customer/:id</code>.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-cream text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-5 py-3">Order ID</th>
              <th className="px-5 py-3">Date</th>
              <th className="px-5 py-3">Payment</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3 text-right">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {mockOrders.map((order) => {
              const Icon = statusIcons[order.Status];
              return (
                <tr key={order.OrderID} className="hover:bg-cream/60">
                  <td className="px-5 py-3 font-medium text-forest-dark">#{order.OrderID}</td>
                  <td className="px-5 py-3 text-gray-500">{order.OrderDate}</td>
                  <td className="px-5 py-3 text-gray-500">{order.PaymentMethod}</td>
                  <td className="px-5 py-3">
                    <span className={`badge ${statusStyles[order.Status]}`}>
                      <Icon className="h-3.5 w-3.5" />
                      {order.Status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-right font-medium text-forest-dark">
                    ${order.TotalAmount.toFixed(2)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
