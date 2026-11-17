// @vitest-environment jsdom
import { createElement } from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../config', () => ({ API_URL: 'https://api.example.test' }));

import Login from './Login';

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe('Login', () => {
  it('authenticates and logs out', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      success: true, access_token: 'test-token', token_type: 'Bearer',
    })));
    vi.stubGlobal('fetch', fetchMock);
    vi.spyOn(console, 'log').mockImplementation(() => {});
    render(createElement(Login));

    fireEvent.change(screen.getByPlaceholderText("Nom d'utilisateur"), { target: { value: 'alice' } });
    fireEvent.change(screen.getByPlaceholderText('Mot de passe'), { target: { value: 'password' } });
    fireEvent.click(screen.getByRole('button', { name: 'Connexion' }));

    const logoutButton = await screen.findByRole('button', { name: 'Se déconnecter' });
    expect(fetchMock).toHaveBeenCalledWith('https://api.example.test/auth', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ username: 'alice', password: 'password' }),
    }));
    expect(localStorage.getItem('kl_token')).toBe('test-token');
    fireEvent.click(logoutButton);
    expect(localStorage.getItem('kl_token')).toBeNull();
    expect(screen.getByRole('button', { name: 'Connexion' })).toBeTruthy();
  });

  it('keeps the login form visible when authentication fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 401 })));
    vi.spyOn(console, 'error').mockImplementation(() => {});
    render(createElement(Login));
    fireEvent.change(screen.getByPlaceholderText("Nom d'utilisateur"), { target: { value: 'alice' } });
    fireEvent.change(screen.getByPlaceholderText('Mot de passe'), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByRole('button', { name: 'Connexion' }));

    await waitFor(() => expect(console.error).toHaveBeenCalled());
    expect(localStorage.getItem('kl_token')).toBeNull();
    expect(screen.getByRole('button', { name: 'Connexion' })).toBeTruthy();
  });
});
