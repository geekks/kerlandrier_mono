import React, { useState } from 'react';
import { API_URL } from "../config";
import { getAccessToken } from '../services/authService';
import '../styles/uploadimage.css';
import '../styles/textInput.css';

interface DebugModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

const DebugModal: React.FC<DebugModalProps> = ({ open, title, onClose, children }) => {
  if (!open) return null;

  return (
    <div
      className="debug-modal-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        className="debug-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="debug-modal-title"
        tabIndex={-1}
        onKeyDown={(event) => {
          if (event.key === 'Escape') onClose();
        }}
      >
        <header className="debug-modal-header">
          <h2 id="debug-modal-title">{title}</h2>
          <button
            type="button"
            className="debug-modal-close"
            aria-label="Fermer"
            autoFocus
            onClick={onClose}
          >
            ×
          </button>
        </header>
        <div className="debug-modal-body">{children}</div>
      </section>
    </div>
  );
};

interface Timing {
  begin: string;
  end: string;
}

interface OpenAgendaEventPayload {
  title: string;
  summary?: string | null;
  description: string;
  longDescription?: string | null;
  keywords?: Record<string, string[]> | null;
  registration?: { type: string; value: string }[] | null;
  timings: Timing[];
  locationUid?: number | null;
}

interface TextInputsResponse {
  success: boolean;
  count: number;
  events: OpenAgendaEventPayload[];
}

interface CreationResult {
  title: string;
  success: boolean;
  uid?: number | string | null;
  url?: string | null;
  message?: string | null;
  openAgendaResponse?: {
    status_code?: number;
    body?: unknown;
    error?: string;
  };
}

interface TextPayloadResponse {
  success: boolean;
  created: number;
  results: CreationResult[];
}

interface DebugResponse {
  status: number | null;
  statusText: string;
  body: string;
}

const formatDate = (iso: string): string =>
  new Date(iso).toLocaleString('fr-FR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

const TextInputs: React.FC = () => {
  const [text, setText] = useState('');
  const [message, setMessage] = useState<{ text: string; type: string }>({ text: '', type: 'info' });
  const [events, setEvents] = useState<OpenAgendaEventPayload[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [results, setResults] = useState<CreationResult[]>([]);
  const [debugPayload, setDebugPayload] = useState<OpenAgendaEventPayload | null>(null);
  const [debugResponse, setDebugResponse] = useState<DebugResponse | null>(null);
  const [isDebugResponseOpen, setIsDebugResponseOpen] = useState(false);

  const handleCreate = async () => {
    setResults([]);
    setDebugResponse(null);
    setIsDebugResponseOpen(false);
    setMessage({ text: '', type: 'info' });
    setIsCreating(true);
    try {
      const response = await fetch(`${API_URL}/text/payload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify({ events }),
      });
      const rawResponse = await response.text();
      setDebugResponse({
        status: response.status,
        statusText: response.statusText,
        body: rawResponse,
      });
      let responseData: unknown;
      try {
        responseData = JSON.parse(rawResponse);
      } catch {
        responseData = rawResponse;
      }

      if (response.ok) {
        const data = responseData as TextPayloadResponse;
        setResults(data.results);
        setMessage({
          text: `${data.created}/${data.results.length} événement(s) créé(s) sur OpenAgenda.`,
          type: data.success ? 'success' : 'error',
        });
      } else {
        const errorData = responseData as { detail?: unknown } | null;
        const detail = errorData && typeof errorData === 'object' ? errorData.detail : undefined;
        setMessage({
          text: `Échec de la création : ${typeof detail === 'string' ? detail : JSON.stringify(errorData)}`,
          type: 'error',
        });
      }
    } catch (error) {
      console.error('Erreur :', error);
      setDebugResponse({
        status: null,
        statusText: 'Erreur réseau',
        body: error instanceof Error ? error.message : String(error),
      });
      setMessage({ text: "Erreur lors de la création des événements.", type: 'error' });
    } finally {
      setIsCreating(false);
    }
  };

  const handleSubmit = async () => {
    if (!text.trim()) {
      setMessage({ text: 'Veuillez saisir au moins un événement.', type: 'error' });
      return;
    }
    setEvents([]);
    setResults([]);
    setMessage({ text: '', type: 'info' });
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/text/inputs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const data: TextInputsResponse = await response.json();
        setEvents(data.events);
        setMessage({ text: `${data.count} événement(s) généré(s) !`, type: 'success' });
      } else {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail;
        setMessage({
          text: `Échec de l'analyse : ${typeof detail === 'string' ? detail : JSON.stringify(errorData)}`,
          type: 'error',
        });
      }
    } catch (error) {
      console.error('Erreur :', error);
      setMessage({ text: "Erreur lors de l'envoi du texte.", type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={"Décrivez un ou plusieurs événements.\nSéparez-les avec une ligne contenant ---"}
          rows={12}
          style={{ width: '100%', boxSizing: 'border-box', padding: '0.5rem' }}
        />
      </div>
      {isLoading ? (
        <div className="loader-container">
          <img src="/loader.gif" alt="Chargement..." className="loader-image" />
        </div>
      ) : (
        <button className="upload-button" onClick={handleSubmit}>Envoyer</button>
      )}
      {message.text && <p className={`message ${message.type}`}>{message.text}</p>}
      {events.map((event, index) => (
        <div className="event-details" key={index}>
          <h2>{event.title}</h2>
          <table>
            <tbody>
              <tr>
                <td className="event-details-label"><strong>Desc. :</strong></td>
                <td>{event.description}</td>
              </tr>
              {event.timings.map((timing, i) => (
                <tr key={i}>
                  <td className="event-details-label event-date"><strong>{i === 0 ? 'Dates :' : ''}</strong></td>
                  <td className="event-date">{formatDate(timing.begin)} → {formatDate(timing.end)}</td>
                </tr>
              ))}
              <tr>
                <td className="event-details-label"><strong>Lieu (UID) :</strong></td>
                <td>{event.locationUid ?? '—'}</td>
              </tr>
              {event.keywords?.fr && (
                <tr>
                  <td className="event-details-label"><strong>Mots-clés :</strong></td>
                  <td>{event.keywords.fr.join(', ')}</td>
                </tr>
              )}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={2} className="debug-payload-cell">
                  <button
                    type="button"
                    className="debug-payload-button"
                    aria-label={`Afficher le payload brut de ${event.title}`}
                    onClick={() => setDebugPayload(event)}
                  >
                    debug
                  </button>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      ))}
      {events.length > 0 && results.length === 0 && (
        isCreating ? (
          <div className="loader-container">
            <img src="/loader.gif" alt="Chargement..." className="loader-image" />
          </div>
        ) : (
          <button className="upload-button" onClick={handleCreate}>Créer sur OpenAgenda</button>
        )
      )}
      {results.length > 0 && (
        <ul>
          {results.map((r, i) => (
            <li key={i}>
              {r.success ? '✅' : '❌'} {r.title}{' '}
              {r.success && r.url
                ? <a href={r.url} target="_blank" rel="noopener noreferrer">{r.url}</a>
                : r.message}
            </li>
          ))}
        </ul>
      )}
      {debugResponse && (
        <button
          type="button"
          className="debug-payload-button"
          onClick={() => setIsDebugResponseOpen(true)}
        >
          réponse API
        </button>
      )}
      <DebugModal
        open={debugPayload !== null}
        onClose={() => setDebugPayload(null)}
        title={`Payload brut${debugPayload ? ` — ${debugPayload.title}` : ''}`}
      >
        <pre className="debug-payload-content">
          {debugPayload ? JSON.stringify(debugPayload, null, 2) : ''}
        </pre>
      </DebugModal>
      <DebugModal
        open={isDebugResponseOpen && debugResponse !== null}
        onClose={() => setIsDebugResponseOpen(false)}
        title="Réponse OpenAgenda"
      >
        <pre className="debug-payload-content">
          {debugResponse
            ? `HTTP ${debugResponse.status ?? '—'} ${debugResponse.statusText}\n\n${debugResponse.body}`
            : ''}
        </pre>
      </DebugModal>
    </div>
  );
};

export default TextInputs;
