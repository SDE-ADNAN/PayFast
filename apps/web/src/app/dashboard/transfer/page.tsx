"use client";

import { useActionState } from "react";
import { transferFunds } from "@/actions/banking";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Send, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { useFormStatus } from "react-dom";

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending} className="btn-primary" style={{ width: "100%", marginTop: "var(--space-6)" }}>
      {pending ? (
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
          ⟳
        </motion.div>
      ) : (
        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          Send Money <Send size={18} />
        </span>
      )}
    </button>
  );
}

export default function TransferPage() {
  const [state, formAction] = useActionState(transferFunds, null);

  if (state?.success) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
        <motion.div 
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="glass-panel" 
          style={{ padding: "var(--space-8)", maxWidth: "400px", width: "100%", textAlign: "center" }}
        >
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            style={{ display: "inline-flex", padding: "16px", borderRadius: "50%", background: "rgba(0, 255, 187, 0.1)", marginBottom: "var(--space-4)" }}
          >
            <CheckCircle2 size={48} color="var(--accent-secondary)" />
          </motion.div>
          <h2 style={{ marginBottom: "var(--space-2)" }}>Transfer Successful</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "var(--space-6)" }}>
            Your funds have been securely sent.
          </p>
          <Link href="/dashboard" className="btn-secondary" style={{ width: "100%", display: "block" }}>
            Return to Dashboard
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto" }}>
      <header style={{ display: "flex", alignItems: "center", gap: "var(--space-4)", marginBottom: "var(--space-8)" }}>
        <Link href="/dashboard" style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "40px", height: "40px", borderRadius: "50%", background: "var(--bg-tertiary)" }}>
          <ArrowLeft size={20} />
        </Link>
        <h1 style={{ fontSize: "28px" }}>Send Funds</h1>
      </header>

      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="glass-panel" 
        style={{ padding: "var(--space-6)" }}
      >
        <form action={formAction} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
          <div>
            <label style={{ display: "block", marginBottom: "var(--space-2)", color: "var(--text-secondary)", fontSize: "14px" }}>
              Destination Account ID
            </label>
            <input type="text" name="to_account_id" placeholder="UUID format" required style={{ fontFamily: "monospace" }} />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "var(--space-2)", color: "var(--text-secondary)", fontSize: "14px" }}>
              Amount (Paise)
            </label>
            <div style={{ position: "relative" }}>
              <span style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }}>$</span>
              <input type="number" name="amount_paise" placeholder="1000" min="1" required style={{ paddingLeft: "30px", fontFamily: "monospace" }} />
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-tertiary)", marginTop: "4px" }}>Note: 100 paise = 1 Unit</p>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "var(--space-2)", color: "var(--text-secondary)", fontSize: "14px" }}>
              Notes (Optional)
            </label>
            <input type="text" name="notes" placeholder="e.g., Dinner split" />
          </div>

          <AnimatePresence>
            {state?.error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                style={{ padding: "12px", background: "rgba(255, 51, 102, 0.1)", borderLeft: "4px solid var(--accent-danger)", color: "var(--text-primary)", borderRadius: "var(--radius-sm)", fontSize: "14px" }}
              >
                {state.error}
              </motion.div>
            )}
          </AnimatePresence>

          <SubmitButton />
        </form>
      </motion.div>
    </div>
  );
}
