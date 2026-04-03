import Link from "next/link";
import { ArrowRight, ShieldCheck, Zap, Globe } from "lucide-react";

export default function LandingPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={{ padding: "var(--space-6) var(--space-12)", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--bg-glass-border)" }}>
        <h1 className="text-gradient" style={{ fontSize: "24px", fontWeight: "bold" }}>PayFast</h1>
        <div style={{ display: "flex", gap: "var(--space-4)" }}>
          <Link href="/login" className="btn-secondary">Login</Link>
          <Link href="/register" className="btn-primary">Get Started</Link>
        </div>
      </header>

      <main style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "var(--space-12)", maxWidth: "1200px", margin: "0 auto" }}>
        
        <div style={{ display: "inline-block", padding: "var(--space-2) var(--space-4)", borderRadius: "var(--radius-full)", background: "rgba(189, 0, 255, 0.1)", color: "var(--accent-primary)", fontSize: "14px", fontWeight: "600", marginBottom: "var(--space-6)" }}>
          🚀 The Future of Core Banking is Here
        </div>

        <h2 style={{ fontSize: "64px", fontWeight: "800", lineHeight: "1.1", marginBottom: "var(--space-6)" }}>
          High-Performance.<br />
          <span className="text-gradient">Zero Compromises.</span>
        </h2>
        
        <p style={{ fontSize: "20px", color: "var(--text-secondary)", maxWidth: "600px", marginBottom: "var(--space-8)" }}>
          Engineered natively on strictly asynchronous gateways, enforcing deterministic execution over rigorous financial systems.
        </p>

        <Link href="/register" className="btn-primary" style={{ padding: "var(--space-4) var(--space-8)", fontSize: "18px" }}>
          Launch Dashboard <ArrowRight style={{ marginLeft: "var(--space-2)" }} />
        </Link>

        {/* Feature Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-6)", marginTop: "var(--space-12)", width: "100%", textAlign: "left" }}>
          <div className="glass-panel" style={{ padding: "var(--space-6)" }}>
            <Zap size={32} color="var(--accent-secondary)" style={{ marginBottom: "var(--space-4)" }} />
            <h3 style={{ fontSize: "20px", marginBottom: "var(--space-2)" }}>Hyperfast Transfers</h3>
            <p style={{ color: "var(--text-secondary)" }}>Millisecond lock execution globally available right in the palm of your hand.</p>
          </div>
          <div className="glass-panel" style={{ padding: "var(--space-6)" }}>
            <ShieldCheck size={32} color="var(--accent-primary)" style={{ marginBottom: "var(--space-4)" }} />
            <h3 style={{ fontSize: "20px", marginBottom: "var(--space-2)" }}>Fraud Engine Signature</h3>
            <p style={{ color: "var(--text-secondary)" }}>Temporal bound verifications ensuring explicit double entry ledger checks natively.</p>
          </div>
          <div className="glass-panel" style={{ padding: "var(--space-6)" }}>
            <Globe size={32} color="#007bff" style={{ marginBottom: "var(--space-4)" }} />
            <h3 style={{ fontSize: "20px", marginBottom: "var(--space-2)" }}>Universal Scope</h3>
            <p style={{ color: "var(--text-secondary)" }}>WebHooks, APIs, completely unified in a single elite platform structure.</p>
          </div>
        </div>

      </main>
    </div>
  );
}
