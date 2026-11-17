// @vitest-environment jsdom
import { createElement } from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../config', () => ({ API_URL: 'https://api.example.test' }));

import UploadImage from './UploadImage';

beforeEach(() => {
  localStorage.clear();
  Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: vi.fn(() => 'blob:test') });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('UploadImage', () => {
  it('rejects unsupported files without sending a request', () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    render(createElement(UploadImage));

    const file = new File(['test'], 'poster.txt', { type: 'text/plain' });
    fireEvent.change(screen.getByLabelText('Cliquez pour télécharger une image'), {
      target: { files: [file] },
    });
    expect(screen.getByText('Veuillez sélectionner une image au format JPG, JPEG ou PNG.')).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('uploads the selected image with the token and shows the returned event', async () => {
    localStorage.setItem('kl_token', 'test-token');
    const fetchMock = vi.fn<(url: string, init: RequestInit) => Promise<Response>>().mockResolvedValue(
      new Response(JSON.stringify({
        event: {
          name: 'Fest-noz', location: 'Espace Benoîte Groult', description: 'Danse',
          start: '2026-12-12T18:00:00+01:00', end: '2026-12-13T01:00:00+01:00',
          url: 'https://example.test/event',
        },
      })),
    );
    vi.stubGlobal('fetch', fetchMock);
    render(createElement(UploadImage));
    const file = new File(['poster'], 'poster.jpg', { type: 'image/jpeg' });
    fireEvent.change(screen.getByLabelText('Cliquez pour télécharger une image'), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Envoyer' }));

    expect(await screen.findByText('Fest-noz')).toBeTruthy();
    expect(screen.getByText('Espace Benoîte Groult')).toBeTruthy();
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe('https://api.example.test/image/upload');
    expect(options.headers).toEqual({ Authorization: 'Bearer test-token' });
    expect(options.body).toBeInstanceOf(FormData);
    expect((options.body as FormData).get('file')).toBe(file);
  });
});
