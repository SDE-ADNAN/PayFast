"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function getAuthHeaders() {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  if (!token) redirect("/login");
  return {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function getAccounts() {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/accounts`, {
      method: "GET",
      headers,
      cache: "no-store",
    });

    if (!response.ok) {
      if (response.status === 401) redirect("/login");
      return null;
    }

    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function getTransactions() {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/transactions`, {
      method: "GET",
      headers,
      cache: "no-store",
    });

    if (!response.ok) {
      return { items: [] };
    }

    return await response.json();
  } catch (error) {
    return { items: [] };
  }
}

export async function transferFunds(prevState: any, formData: FormData) {
  const to_account_id = formData.get("to_account_id");
  const amount_paise = formData.get("amount_paise");
  const notes = formData.get("notes") || "";

  if (!to_account_id || !amount_paise) {
    return { error: "Destination Account and Amount are required" };
  }

  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/payments/transfer`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        to_account_id: to_account_id as string,
        amount_paise: parseInt(amount_paise as string, 10),
        notes: notes as string,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || "Transfer failed" };
    }

    return { success: true };
  } catch (error) {
    return { error: "An unexpected error occurred" };
  }
}

