// @vitest-environment jsdom
import { createElement } from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../config', () => ({ API_URL: 'https://api.example.test' }));

import TextInputs from './TextInputs';

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem('kl_token', 'test-token');
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('TextInputs', () => {
  it('requires text before sending', () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    render(createElement(TextInputs));
    fireEvent.click(screen.getByRole('button', { name: 'Envoyer' }));
    expect(screen.getByText('Veuillez saisir au moins un événement.')).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('previews generated events and creates them only after confirmation', async () => {
    const event = {
      title: 'Fest-noz', description: 'Danse', locationUid: 42, locationName: 'Salle',
      timings: [{ begin: '2026-12-12T18:00:00+01:00', end: '2026-12-13T01:00:00+01:00' }],
    };
    const fetchMock = vi.fn<(url: string, init: RequestInit) => Promise<Response>>()
      .mockResolvedValueOnce(new Response(JSON.stringify({ success: true, count: 1, events: [event] })))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        success: true, created: 1,
        results: [{ title: 'Fest-noz', success: true, uid: 123, url: 'https://example.test/event' }],
      })));
    vi.stubGlobal('fetch', fetchMock);
    render(createElement(TextInputs));

    fireEvent.change(screen.getByPlaceholderText(/Décrivez un ou plusieurs événements/), {
      target: { value: 'Fest-noz à la salle' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Envoyer' }));
    expect(await screen.findByRole('heading', { name: 'Fest-noz' })).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe('https://api.example.test/text/inputs');

    fireEvent.click(screen.getByRole('button', { name: 'Créer sur OpenAgenda' }));
    expect(await screen.findByText('1/1 événement(s) créé(s) sur OpenAgenda.')).toBeTruthy();
    const [url, options] = fetchMock.mock.calls[1];
    expect(url).toBe('https://api.example.test/text/payload');
    expect(options.headers).toEqual({
      'Content-Type': 'application/json', Authorization: 'Bearer test-token',
    });
    expect(JSON.parse(String(options.body))).toEqual({ events: [event] });
  });

  it('displays API errors during analysis', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Analyse impossible' }), { status: 400 }),
    ));
    render(createElement(TextInputs));
    fireEvent.change(screen.getByPlaceholderText(/Décrivez un ou plusieurs événements/), {
      target: { value: 'Concert' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Envoyer' }));
    expect(await screen.findByText("Échec de l'analyse : Analyse impossible")).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Créer sur OpenAgenda' })).toBeNull();
  });
});
