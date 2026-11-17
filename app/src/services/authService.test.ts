import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('../config', () => ({ API_URL: 'https://api.example.test' }));

import { authenticate } from './authService';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('authenticate', () => {
  it('sends credentials to the configured API and stores the token', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      success: true,
      access_token: 'test-token',
      token_type: 'Bearer',
    })));
    const setItem = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('localStorage', { setItem });

    await authenticate('test-user', 'test-password');

    expect(fetchMock).toHaveBeenCalledWith('https://api.example.test/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'test-user', password: 'test-password' }),
    });
    expect(setItem).toHaveBeenCalledWith('kl_token', 'test-token');
  });

  it('does not store a token when authentication fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 401 })));
    const setItem = vi.fn();
    vi.stubGlobal('localStorage', { setItem });

    await expect(authenticate('test-user', 'wrong-password')).rejects.toThrow('Authentication failed');
    expect(setItem).not.toHaveBeenCalled();
  });
});
