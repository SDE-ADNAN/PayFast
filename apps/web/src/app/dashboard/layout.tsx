import { ArrowLeftRight, CreditCard, LayoutDashboard, LogOut } from "lucide-react";
import Link from "next/link";
import { logoutAction } from "@/actions/auth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Sidebar */}
      <aside style={{ width: "260px", background: "var(--bg-secondary)", borderRight: "1px solid var(--bg-glass-border)", padding: "var(--space-6)", display: "flex", flexDirection: "column" }}>
        <div style={{ marginBottom: "var(--space-8)" }}>
          <h2 className="text-gradient" style={{ fontSize: "24px", fontWeight: "bold" }}>PayFast</h2>
        </div>
        
        <nav style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)", flex: 1 }}>
          <Link href="/dashboard" style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", padding: "var(--space-3)", borderRadius: "var(--radius-md)", background: "rgba(255, 255, 255, 0.05)" }}>
            <LayoutDashboard size={20} color="var(--accent-secondary)" />
            <span>Dashboard</span>
          </Link>
          <Link href="/dashboard/transfer" style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", padding: "var(--space-3)", borderRadius: "var(--radius-md)", transition: "background 0.2s" }} className="sidebar-link">
            <ArrowLeftRight size={20} color="var(--text-secondary)" />
            <span style={{ color: "var(--text-secondary)" }}>Transfer</span>
          </Link>
          <Link href="/dashboard" style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", padding: "var(--space-3)", borderRadius: "var(--radius-md)", transition: "background 0.2s" }}>
            <CreditCard size={20} color="var(--text-secondary)" />
            <span style={{ color: "var(--text-secondary)" }}>Cards</span>
          </Link>
        </nav>

        <form action={logoutAction}>
          <button type="submit" style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", color: "var(--text-secondary)", width: "100%", padding: "var(--space-3)", textAlign: "left" }}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </form>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, padding: "var(--space-8)", overflowY: "auto", position: "relative" }}>
        {children}
      </main>
    </div>
  );
}
