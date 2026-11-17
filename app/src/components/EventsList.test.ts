import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import type { OpenAgendaEvent } from '../types/OpenAgenda';

vi.mock('../config', () => ({ OA_SLUG: 'test-agenda' }));

import { EventsList } from './EventsList';

const timing = { begin: '2026-12-12T18:00:00+01:00', end: '2026-12-13T01:00:00+01:00' };
const event: OpenAgendaEvent = {
  uid: '123',
  'uid-externe': '',
  slug: 'fest-noz',
  title: 'FEST NOZ',
  onlineAccessLink: '',
  registration: [],
  status: 0,
  keywords: ['danse'],
  dateRange: 'Samedi 12 décembre',
  location: { name: 'Espace Benoîte Groult', city: 'Quimperlé', description: '' },
  firstTiming: timing,
  nextTiming: timing,
  lastTiming: timing,
  longDescription: '',
  description: 'Musique et danse',
  keyword: '',
  timings: [timing],
};

describe('EventsList', () => {
  it('displays the event, venue and OpenAgenda contribution link', () => {
    const html = renderToStaticMarkup(createElement(EventsList, { events: [event], longEvents: false }));
    expect(html).toContain('Fest Noz');
    expect(html).toContain('Espace Benoîte Groult, Quimperlé');
    expect(html).toContain('https://openagenda.com/fr/test-agenda/contribute/event/123');
    expect(html).toContain('18:00');
    expect(html).toContain('#danse');
  });

  it('marks cancelled events and prefers the online link', () => {
    const html = renderToStaticMarkup(createElement(EventsList, {
      events: [{ ...event, status: 5, onlineAccessLink: 'https://example.test/stream' }],
      longEvents: false,
    }));
    expect(html).toContain('[ANNULE]');
    expect(html).toContain('href="https://example.test/stream"');
  });
});
