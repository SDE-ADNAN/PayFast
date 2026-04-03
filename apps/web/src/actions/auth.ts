"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function loginAction(prevState: any, formData: FormData) {
  const phone = formData.get("phone");
  const password = formData.get("password");

  if (!phone || !password) {
    return { error: "Phone and password are required" };
  }

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || "Login failed" };
    }

    const data = await response.json();
    
    // Set cookie
    const cookieStore = await cookies();
    cookieStore.set("token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 3600, // 1 hour for MVP
      path: "/",
    });
  } catch (error) {
    return { error: "An unexpected error occurred" };
  }

  // Redirect on success
  redirect("/dashboard");
}

export async function registerAction(prevState: any, formData: FormData) {
  const phone = formData.get("phone");
  const fullName = formData.get("full_name");
  const password = formData.get("password");

  if (!phone || !fullName || !password) {
    return { error: "Phone, Full Name, and Password are required" };
  }

  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, full_name: fullName, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || "Registration failed" };
    }
  } catch (error) {
    return { error: "An unexpected error occurred" };
  }

  // Automatically login after registration
  return loginAction(prevState, formData);
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("token");
  redirect("/login");
}
