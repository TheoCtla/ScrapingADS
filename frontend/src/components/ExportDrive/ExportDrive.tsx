import React, { useState } from 'react';
import axios from 'axios';
import ClientSelector from '../unified/ClientSelector/ClientSelector';
import './ExportDrive.css';

interface ExportedFile {
  platform: string;
  campaign: string;
  type: string;
  id: string;
  name: string;
  link: string;
}

const ExportDrive: React.FC = () => {
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [exportedFiles, setExportedFiles] = useState<ExportedFile[]>([]);
  const [error, setError] = useState<string>('');
  const [clientFolderId, setClientFolderId] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  const handleExport = async () => {
    if (!selectedClient) {
      setError('Veuillez sélectionner un client');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');
    setLogs([]);
    setExportedFiles([]);
    setClientFolderId('');

    addLog('Début de l\'export créatif...');
    addLog(`Client: ${selectedClient}`);
    addLog('Récupération des campagnes actives au jour J');

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5050';
      
      const response = await axios.post(`${apiUrl}/export-to-drive`, {
        client_name: selectedClient
      });

      if (response.data.success) {
        addLog(`✅ ${response.data.message}`);
        setExportedFiles(response.data.files || []);
        
        if (response.data.client_folder_id) {
          setClientFolderId(response.data.client_folder_id);
        }

        // Grouper les fichiers par campagne pour un meilleur affichage
        const filesByType = response.data.files.reduce((acc: any, file: ExportedFile) => {
          const key = `${file.platform} - ${file.campaign}`;
          if (!acc[key]) acc[key] = [];
          acc[key].push(file);
          return acc;
        }, {});
        
        Object.entries(filesByType).forEach(([key, files]: [string, any]) => {
          const csvCount = files.filter((f: ExportedFile) => f.type === 'csv').length;
          const imageCount = files.filter((f: ExportedFile) => f.type === 'image').length;
          const videoCount = files.filter((f: ExportedFile) => f.type === 'video').length;
          
          addLog(`  📁 ${key}: ${csvCount} CSV, ${imageCount} images, ${videoCount} vidéos`);
        });
        
        setSuccessMessage('Export réalisé avec succès !');
        addLog('🎉 Export terminé avec succès!');
      } else {
        throw new Error(response.data.error || 'Erreur inconnue');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Erreur lors de l\'export';
      setError(errorMessage);
      addLog(`❌ Erreur: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  return (
    <div className="export-drive-page">
      <div className="export-drive-container">
        <h1 className="export-title">Export Campagnes vers Google Drive</h1>
        <p className="export-subtitle"></p>

        <div className="export-form">
          {/* Client Selector */}
          <div className="form-group">
            <label className="form-label">Client</label>
            <ClientSelector
              selectedClient={selectedClient}
              onSelectClient={setSelectedClient}
              onClientInfoChange={() => {}}
            />
          </div>

          {/* Export Button */}
          <button
            className="export-btn"
            onClick={handleExport}
            disabled={loading || !selectedClient}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Export en cours...
              </>
            ) : (
              <>
                Lancer l'export créatif
              </>
            )}
          </button>
          
          {/* Success Message & Drive Link */}
          {successMessage && (
            <div className="success-container">
              <div className="success-message">
                {successMessage}
              </div>
              {clientFolderId && (
                <a 
                  href={`https://drive.google.com/drive/folders/${clientFolderId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="drive-link-btn"
                >
                  Accéder au dossier Drive
                </a>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>

        {/* Logs Section */}
        {/*
        {logs.length > 0 && (
          <div className="logs-section">
            <h3 className="logs-title">Logs de progression</h3>
            <div className="logs-container">
              {logs.map((log, index) => (
                <div key={index} className="log-entry">
                  {log}
                </div>
              ))}
            </div>
          </div>
        )}
        */}

        {/* Exported Files Section */}
        {/*
        {exportedFiles.length > 0 && (
          <div className="files-section">
            <h3 className="files-title">Fichiers exportés ({exportedFiles.length})</h3>
            <div className="files-grid">
              {exportedFiles.map((file, index) => (
                <div key={index} className="file-card">
                  <div className="file-type-badge">{file.type.toUpperCase()}</div>
                  <div className="file-platform">{file.platform}</div>
                  <div className="file-campaign">{file.campaign}</div>
                  <div className="file-name">{file.name}</div>
                  <a
                    href={file.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="file-link"
                  >
                    Ouvrir dans Drive →
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
        */}
      </div>
    </div>
  );
};

export default ExportDrive;
