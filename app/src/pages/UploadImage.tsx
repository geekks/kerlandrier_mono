import React, { useState } from 'react';
import { API_URL } from "../config";
import '../styles/uploadimage.css';

const UploadImage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [message, setMessage] = useState<string>('');
  const [eventDetails, setEventDetails] = useState<{ url: string, name: string, location: string, description: string, start: string, end: string } | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Veuillez sélectionner un fichier d\'abord.');
      return;
    }

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
        setMessage('Fichier téléchargé avec succès !');
        setEventDetails(data.event);
        console.log('Réponse de téléchargement :', data);
      } else {
        const errorData = await response.json();
        setMessage(`Échec du téléchargement du fichier: ${errorData.message}`);
      }
    } catch (error) {
      setMessage('Erreur lors du téléchargement du fichier.');
      console.error('Erreur :', error);
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
      <button className="upload-button" onClick={handleUpload}>Envoyer</button>
      {message && <p className="message">{message}</p>}
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
                <td className="event-details-label"><strong>Description :</strong></td>
                <td>{eventDetails.description}</td>
              </tr>
              <tr>
                <td className="event-details-label"><strong>Début :</strong></td>
                <td>{new Date(eventDetails.start).toLocaleString()}</td>
              </tr>
              <tr>
                <td className="event-details-label"><strong>Fin :</strong></td>
                <td>{new Date(eventDetails.end).toLocaleString()}</td>
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
