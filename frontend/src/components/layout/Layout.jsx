import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-cream">
      <Sidebar />
      <div className="flex min-h-screen flex-col pl-64">
        <Navbar />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
