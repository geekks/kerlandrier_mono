// @vitest-environment jsdom
import { createElement } from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { OpenAgendaEvent } from '../types/OpenAgenda';

const kyMock = vi.hoisted(() => vi.fn());
vi.mock('ky', () => ({ default: kyMock }));
vi.mock('../config', () => ({
  defaultQuery: 'https://api.example.test/events',
  AREA_FILTERS: ['aven', 'cornouaille', 'bretagne'],
  OA_SLUG: 'test-agenda',
}));

import Home from './Home';

function event(uid: string, title: string, area: string, hour: string): OpenAgendaEvent {
  const timing = { begin: `2026-12-12T${hour}:00+01:00`, end: '2026-12-12T23:00:00+01:00' };
  return {
    uid, title, slug: uid, 'uid-externe': '', onlineAccessLink: '', registration: [],
    status: 0, keywords: [], dateRange: 'Samedi 12 décembre',
    location: { name: 'Salle', city: 'Quimperlé', description: area },
    firstTiming: timing, nextTiming: timing, lastTiming: timing,
    description: '', longDescription: '', keyword: '', timings: [timing],
  };
}

function renderHome() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(createElement(QueryClientProvider, { client },
    createElement(MemoryRouter, null, createElement(Home)),
  ));
}

afterEach(() => {
  cleanup();
  kyMock.mockReset();
});

describe('Home', () => {
  it('loads events, excludes duplicates and filters by area', async () => {
    const later = event('1', 'CONCERT', 'aven', '20:00');
    const earlier = event('2', 'FEST NOZ', 'cornouaille', '18:00');
    const duplicate = { ...event('3', 'DUPLICATA', 'aven', '19:00'), 'uid-externe': 'DUPLICATE' };
    kyMock.mockReturnValue({ json: async () => ({ total: 3, events: [later, earlier, duplicate] }) });
    renderHome();

    await screen.findByRole('heading', { name: 'Fest Noz' });
    const headings = screen.getAllByRole('heading', { level: 2 }).map((node) => node.textContent);
    expect(headings).toEqual(['Fest Noz', 'Concert']);
    expect(screen.queryByText('Duplicata')).toBeNull();
    expect(kyMock).toHaveBeenCalledWith('https://api.example.test/events');

    fireEvent.click(screen.getByRole('button', { name: 'AVEN' }));
    expect(screen.getByRole('heading', { name: 'Concert' })).toBeTruthy();
    expect(screen.queryByRole('heading', { name: 'Fest Noz' })).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'AVEN' }));
    expect(screen.getByRole('heading', { name: 'Fest Noz' })).toBeTruthy();
  });

  it('shows a loading error when events cannot be retrieved', async () => {
    kyMock.mockReturnValue({ json: async () => { throw new Error('API unavailable'); } });
    renderHome();
    expect(await screen.findByText(/Error: Error API unavailable/)).toBeTruthy();
  });
});
