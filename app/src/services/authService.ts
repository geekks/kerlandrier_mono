interface AuthResponse {
  success: boolean;
  access_token: string;
  token_type: string;
}

export const authenticate = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await fetch('http://localhost:8001/auth', {
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
  localStorage.setItem('access_token', data.access_token);
  return data;
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

