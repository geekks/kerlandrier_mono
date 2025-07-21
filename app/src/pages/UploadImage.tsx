import React, { useState } from 'react';
import { API_URL } from "../config";
import '../styles/uploadimage.css';

const UploadImage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string, type: string }>({ text: '', type: 'info' });
  const [eventDetails, setEventDetails] = useState<{ url: string, name: string, location: string, description: string, start: string, end: string } | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setErrorDetails(null);
    setEventDetails(null);
    setMessage({text:'', type:'info'});
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      const validExtensions = ['.jpg', '.jpeg', '.png'];
      const fileName = selectedFile.name.toLowerCase();
      const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
      const maxSize = 5 * 1024 * 1024; // 5 MB in bytes
      if (selectedFile.size > maxSize) {
        setFile(null);
        setPreview(null);
        setMessage({text:"L'image doit faire moins de 5 Mo.", type: 'error'});
        return;
      }
      if (!validTypes.includes(selectedFile.type) || !hasValidExtension) {
        setFile(null);
        setPreview(null);
        setMessage({ text: "Veuillez sélectionner une image au format JPG, JPEG ou PNG.", type: 'error' });
        return;
      }
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
    }
    
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ text: 'Veuillez sélectionner un fichier d\'abord.', type: 'error' });
      return;
    }

    setErrorDetails(null);
    setEventDetails(null);
    setMessage({ text: '', type: 'info' });
    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('kl_token');
      const response = await fetch(`${API_URL}/image/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({ text: 'Image analysée et envoyée au KL avec succès !', type: 'success' });
        setEventDetails(data.event);
      } else {
        const errorData = await response.json();
        console.error('Erreur lors de l\'envoi du fichier:', JSON.stringify(errorData));
        const lines = errorData["detail"]["infos"] ?
          errorData["detail"]["infos"].join('</li><li>') :
          JSON.stringify(errorData);
        setErrorDetails(`<p> Échec du téléchargement du fichier:</p> 
          <ul>
            <li>
              ${lines}
              </li>
          </ul>`);
      }
    } catch (error) {
      setMessage({ text: 'Erreur lors de l\'envoi du fichier.', type: 'error' });
      console.error('Erreur :',JSON.stringify( error));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <input
          type="file"
          id="fileInput"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <label htmlFor="fileInput" className="upload-label">
          {preview ? (
            <img src={preview} alt="Aperçu" className="preview-image" />
          ) : (
            <div className="upload-placeholder">Cliquez pour télécharger une image</div>
          )}
        </label>
      </div>
      {isLoading ? (
        <div className="loader-container">
          <img src="/loader.gif" alt="Chargement..." className="loader-image" />
        </div>
      ) : (
        <button className="upload-button" onClick={handleUpload}>Envoyer</button>
      )}
      {message.text && <p className={`message ${message.type}`}>{message.text}</p>}
      {errorDetails && <p className="error-details" dangerouslySetInnerHTML={{ __html: errorDetails }}></p>}
      {eventDetails && (
        <div className="event-details">
          <h2>Détails de l'événement créé :</h2>
          <table>
            <tbody>
              <tr>
                <td className="event-details-label"><strong>Nom :</strong></td>
                <td>{eventDetails.name}</td>
              </tr>
              <tr>
                <td className="event-details-label"><strong>Lieu :</strong></td>
                <td>{eventDetails.location}</td>
              </tr>
              <tr>
                <td className="event-details-label"><strong>Desc. :</strong></td>
                <td>{eventDetails.description}</td>
              </tr>
              <tr>
                <td className="event-details-label event-date"><strong>Début :</strong></td>
                <td className="event-date">
                  {new Date(eventDetails.start).toLocaleDateString('fr-FR', {
                  weekday: 'long',
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric'
                  })} - {new Date(eventDetails.start).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', hour12: false }).replace(':', 'h')}
                </td>
              </tr>
              <tr>
                <td className="event-details-label event-date"><strong>Fin :</strong></td>
                <td className="event-date">
                  {new Date(eventDetails.end).toLocaleDateString('fr-FR', {
                  weekday: 'long',
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric'
                  })} - {new Date(eventDetails.end).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', hour12: false }).replace(':', 'h')}
                </td>
              </tr>
              <tr>
                <td className="event-details-label"><strong>URL :</strong></td>
                <td><a href={eventDetails.url} target="_blank" rel="noopener noreferrer">{eventDetails.url}</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default UploadImage;
