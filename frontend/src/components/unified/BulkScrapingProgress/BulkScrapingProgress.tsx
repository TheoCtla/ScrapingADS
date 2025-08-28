import React from 'react';
import './BulkScrapingProgress.css';

interface BulkScrapingProgressProps {
  isVisible: boolean;
  currentClient: string;
  currentIndex: number;
  totalClients: number;
  isProcessing: boolean;
  onCancel: () => void;
  completedClients: string[];
  failedClients: { client: string; error: string }[];
}

const BulkScrapingProgress: React.FC<BulkScrapingProgressProps> = ({
  isVisible,
  currentClient,
  currentIndex,
  totalClients,
  isProcessing,
  onCancel,
  completedClients,
  failedClients
}) => {
  if (!isVisible) return null;

  const progress = totalClients > 0 ? (currentIndex / totalClients) * 100 : 0;
  const isComplete = currentIndex >= totalClients;

  return (
    <div className="bulk-scraping-progress">
      <div className="progress-header">
        <h3>Scraping en masse des clients</h3>
        <button 
          className="cancel-button"
          onClick={onCancel}
          disabled={!isProcessing || isComplete}
        >
          Annuler
        </button>
      </div>

      <div className="progress-stats">
        <div className="stat-item">
          <span className="stat-label">Progression:</span>
          <span className="stat-value">{currentIndex} / {totalClients}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Succès:</span>
          <span className="stat-value success">{completedClients.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Échecs:</span>
          <span className="stat-value error">{failedClients.length}</span>
        </div>
      </div>

      <div className="progress-bar-container">
        <div 
          className="progress-bar"
          style={{ width: `${progress}%` }}
        />
      </div>

      {isProcessing && currentClient && (
        <div className="current-client">
          <span className="processing-label">Traitement en cours:</span>
          <span className="client-name">{currentClient}</span>
        </div>
      )}

      {isComplete && (
        <div className="completion-summary">
          <h4>Résumé du traitement</h4>
          <div className="summary-stats">
            <div className="summary-item success">
              <span>✅ Succès: {completedClients.length}</span>
            </div>
            <div className="summary-item error">
              <span>❌ Échecs: {failedClients.length}</span>
            </div>
          </div>
          
          {failedClients.length > 0 && (
            <div className="failed-clients">
              <h5>Clients en échec:</h5>
              <ul>
                {failedClients.map((item, index) => (
                  <li key={index}>
                    <strong>{item.client}:</strong> {item.error}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BulkScrapingProgress;
