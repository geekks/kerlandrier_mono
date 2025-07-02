import { API_URL } from "../config";

interface AuthResponse {
  success: boolean;
  access_token: string;
  token_type: string;
}

export const authenticate = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await fetch(`${API_URL}/auth`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('Authentication failed');
  }

  const data = await response.json();
  localStorage.setItem('kl_token', data.access_token);
  return data;
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem('kl_token');
};

export const logout = () => {
  localStorage.removeItem('kl_token');
};
