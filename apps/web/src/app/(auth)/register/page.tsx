"use client";

import { useFormStatus } from "react-dom";
import { useActionState } from "react";
import { registerAction } from "@/actions/auth";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Lock, Phone, User } from "lucide-react";

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending} className="btn-primary" style={{ width: "100%", marginTop: "var(--space-4)" }}>
      {pending ? (
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
          ⟳
        </motion.div>
      ) : (
        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          Create Account <ArrowRight size={18} />
        </span>
      )}
    </button>
  );
}

export default function RegisterPage() {
  const [state, formAction] = useActionState(registerAction, null);

  return (
    <div className="auth-container">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="glass-panel auth-card"
      >
        <div style={{ textAlign: "center", marginBottom: "var(--space-8)" }}>
          <div style={{ display: "inline-flex", padding: "12px", borderRadius: "var(--radius-full)", background: "rgba(0, 255, 187, 0.1)", marginBottom: "var(--space-4)" }}>
            <User size={32} color="var(--accent-secondary)" />
          </div>
          <h1 className="text-gradient">Join PayFast</h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "var(--space-2)" }}>
            The elite core banking platform.
          </p>
        </div>

        <form action={formAction} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
          <div>
            <label style={{ display: "block", marginBottom: "var(--space-2)", color: "var(--text-secondary)", fontSize: "14px" }}>
              Full Name
            </label>
            <div style={{ position: "relative" }}>
              <User size={18} color="var(--text-tertiary)" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <input type="text" name="full_name" placeholder="John Doe" style={{ paddingLeft: "40px" }} required />
            </div>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "var(--space-2)", color: "var(--text-secondary)", fontSize: "14px" }}>
              Phone Number
            </label>
            <div style={{ position: "relative" }}>
              <Phone size={18} color="var(--text-tertiary)" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <input type="tel" name="phone" placeholder="+1..." style={{ paddingLeft: "40px" }} required />
            </div>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "var(--space-2)", color: "var(--text-secondary)", fontSize: "14px" }}>
              Password
            </label>
            <div style={{ position: "relative" }}>
              <Lock size={18} color="var(--text-tertiary)" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <input type="password" name="password" placeholder="••••••••" style={{ paddingLeft: "40px" }} required minLength={6} />
            </div>
          </div>

          {state?.error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              style={{ padding: "12px", background: "rgba(255, 51, 102, 0.1)", borderLeft: "4px solid var(--accent-danger)", color: "var(--text-primary)", borderRadius: "var(--radius-sm)", fontSize: "14px" }}
            >
              {state.error}
            </motion.div>
          )}

          <SubmitButton />
        </form>

        <div style={{ textAlign: "center", marginTop: "var(--space-6)", color: "var(--text-secondary)", fontSize: "14px" }}>
          Already have an account? <Link href="/login" style={{ color: "var(--accent-secondary)", fontWeight: "500" }}>Sign in</Link>
        </div>
      </motion.div>
    </div>
  );
}
