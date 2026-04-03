import { getAccounts, getTransactions } from "@/actions/banking";
import { ArrowUpRight, ArrowDownLeft, Wallet, Activity } from "lucide-react";
import Link from "next/link";

export default async function DashboardPage() {
  const accountsData = await getAccounts();
  const transactionsData = await getTransactions();

  const accounts = accountsData || [];
  const transactions = transactionsData?.items || [];
  
  // Calculate total balance from all accounts
  const totalBalance = accounts.reduce((acc: number, cur: any) => acc + cur.balance_paise, 0) / 100;

  return (
    <div style={{ paddingBottom: "var(--space-12)" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-8)" }}>
        <div>
          <h1 style={{ fontSize: "32px", fontWeight: "bold" }}>Overview</h1>
          <p style={{ color: "var(--text-secondary)" }}>Your financial summary</p>
        </div>
        <Link href="/dashboard/transfer" className="btn-primary">
          Send Money <ArrowUpRight size={18} />
        </Link>
      </header>

      {/* Top Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "var(--space-6)", marginBottom: "var(--space-8)" }}>
        
        {/* Total Balance Card */}
        <div className="glass-panel" style={{ padding: "var(--space-6)", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: "-20px", right: "-20px", width: "100px", height: "100px", background: "var(--accent-primary)", filter: "blur(50px)", opacity: 0.3, borderRadius: "50%" }} />
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", marginBottom: "var(--space-4)" }}>
            <div style={{ padding: "8px", background: "rgba(255, 255, 255, 0.1)", borderRadius: "var(--radius-sm)" }}>
              <Wallet size={20} color="var(--accent-primary)" />
            </div>
            <span style={{ color: "var(--text-secondary)" }}>Total Balance</span>
          </div>
          <div style={{ fontSize: "42px", fontWeight: "bold", fontFamily: "monospace" }}>
            ${totalBalance.toFixed(2)}
          </div>
        </div>

        {/* Activity Card */}
        <div className="glass-panel" style={{ padding: "var(--space-6)", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: "-20px", right: "-20px", width: "100px", height: "100px", background: "var(--accent-secondary)", filter: "blur(50px)", opacity: 0.3, borderRadius: "50%" }} />
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", marginBottom: "var(--space-4)" }}>
            <div style={{ padding: "8px", background: "rgba(255, 255, 255, 0.1)", borderRadius: "var(--radius-sm)" }}>
              <Activity size={20} color="var(--accent-secondary)" />
            </div>
            <span style={{ color: "var(--text-secondary)" }}>Monthly Activity</span>
          </div>
          <div style={{ display: "flex", gap: "var(--space-4)" }}>
            <div>
              <div style={{ color: "var(--text-secondary)", fontSize: "14px", marginBottom: "4px" }}>In</div>
              <div style={{ color: "var(--accent-secondary)", fontWeight: "bold", fontSize: "20px" }}>+ $0.00</div>
            </div>
            <div>
               <div style={{ color: "var(--text-secondary)", fontSize: "14px", marginBottom: "4px" }}>Out</div>
              <div style={{ color: "var(--text-primary)", fontWeight: "bold", fontSize: "20px" }}>- $0.00</div>
            </div>
          </div>
        </div>
      </div>

      <h2>Accounts</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)", marginBottom: "var(--space-8)", marginTop: "var(--space-4)" }}>
        {accounts.length === 0 ? (
          <div className="glass-panel" style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--text-secondary)" }}>
            No accounts found.
          </div>
        ) : (
          accounts.map((acc: any) => (
             <div key={acc.id} className="glass-panel" style={{ padding: "var(--space-4)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: "bold" }}>{acc.account_type} Account</div>
                  <div style={{ color: "var(--text-secondary)", fontSize: "14px", fontFamily: "monospace" }}>{acc.account_number}</div>
                </div>
                <div style={{ fontSize: "20px", fontWeight: "bold", fontFamily: "monospace" }}>
                  ${(acc.balance_paise / 100).toFixed(2)}
                </div>
             </div>
          ))
        )}
      </div>

      {/* Transactions List */}
      <h2>Recent Transactions</h2>
      <div className="glass-panel" style={{ marginTop: "var(--space-4)", overflow: "hidden" }}>
        {transactions.length === 0 ? (
          <div style={{ padding: "var(--space-8)", textAlign: "center", color: "var(--text-secondary)" }}>
            No recent transactions
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column" }}>
            {transactions.map((tx: any, i: number) => {
              // Note: the backend /transactions endpoint returns a unified view. 
              // Without knowing user's account ID context, we'll just format based on whether it's a transfer.
              // We'll assume the amount is positive for simplification if we don't know the direction.
              const isDebit = tx.transaction_type === "transfer_out" || tx.transaction_type === "withdrawal";
              const amount = (tx.amount_paise / 100).toFixed(2);

              return (
                <div key={tx.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "var(--space-4)", borderBottom: i < transactions.length - 1 ? "1px solid var(--bg-glass-border)" : "none" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
                    <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: isDebit ? "rgba(255, 51, 102, 0.1)" : "rgba(0, 255, 187, 0.1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                      {isDebit ? <ArrowUpRight size={18} color="var(--accent-danger)" /> : <ArrowDownLeft size={18} color="var(--accent-secondary)" />}
                    </div>
                    <div>
                      <div style={{ fontWeight: "500" }}>{tx.transaction_type}</div>
                      <div style={{ color: "var(--text-secondary)", fontSize: "12px", fontFamily: "monospace" }}>{tx.reference_number || "REF"}</div>
                    </div>
                  </div>
                  <div style={{ fontWeight: "bold", color: isDebit ? "var(--text-primary)" : "var(--accent-secondary)", fontFamily: "monospace" }}>
                    {isDebit ? "-" : "+"}${amount}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
