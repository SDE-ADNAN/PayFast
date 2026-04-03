import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// For Android emulator pointing to localhost backend on host machine
const API_URL = Platform.OS === 'android' 
  ? 'http://10.0.2.2:8000' 
  : 'http://127.0.0.1:8000';

async function getAuthHeaders() {
  const token = await SecureStore.getItemAsync('token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
}

export async function loginApi(phone: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, password })
  });
  
  if (!res.ok) throw new Error('Login failed');
  const data = await res.json();
  await SecureStore.setItemAsync('token', data.access_token);
}

export async function registerApi(phone: string, fullName: string, password: string) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, full_name: fullName, password })
  });
  
  if (!res.ok) throw new Error('Registration failed');
  await loginApi(phone, password);
}

export async function getAccountsApi() {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_URL}/accounts`, { headers });
  if (!res.ok) throw new Error('Failed to fetch accounts');
  return await res.json();
}

export async function getTransactionsApi() {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_URL}/transactions`, { headers });
  if (!res.ok) throw new Error('Failed to fetch transactions');
  return await res.json();
}

export async function transferFundsApi(toAccountId: string, amountPaise: number, notes: string = '') {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_URL}/payments/transfer`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      to_account_id: toAccountId,
      amount_paise: amountPaise,
      notes
    })
  });
  
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || 'Transfer failed');
  }
}
