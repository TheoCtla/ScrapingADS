import React from 'react';
import './UnifiedDownloadButton.css';

interface UnifiedDownloadButtonProps {
  loading: boolean;
  onClick: () => void;
  hasGoogleSelection: boolean;
  hasMetaSelection: boolean;
  onBulkScraping?: () => void;
  bulkScrapingLoading?: boolean;
  hasAuthorizedClients?: boolean;
  hasAnyMetrics?: boolean;
}

const UnifiedDownloadButton: React.FC<UnifiedDownloadButtonProps> = ({ 
  loading, 
  onClick, 
  hasGoogleSelection, 
  hasMetaSelection,
  onBulkScraping,
  bulkScrapingLoading = false,
  hasAuthorizedClients = false,
  hasAnyMetrics = false
}) => {
  const hasSelection = hasGoogleSelection || hasMetaSelection;
  const isDisabled = loading || !hasSelection;

  const getButtonText = () => {
    if (loading) {
      return 'Envoi en cours...';
    }
    
    if (!hasSelection) {
      return 'Sélectionne au moins un compte';
    }
    
    let platforms = [];
    if (hasGoogleSelection) platforms.push('Google');
    if (hasMetaSelection) platforms.push('Meta');
    
    return `Envoyer au Sheet (${platforms.join(' + ')})`;
  };

  return (
    <div className="unified-download-container">
      <div className="button-group">
        <button
          className="download-button"
          onClick={onClick}
          disabled={isDisabled}
        >
          {getButtonText()}
        </button>
        
        {hasAuthorizedClients && (
          <button
            className="bulk-scraping-button"
            onClick={onBulkScraping}
            disabled={bulkScrapingLoading || !hasAnyMetrics}
          >
            {bulkScrapingLoading ? 'Scraping en cours...' : 'Scraper tous les clients'}
          </button>
        )}
      </div>
      
      {!hasSelection && (
        <p className="help-text">
          Sélectionne au moins un compte Google ou Meta pour commencer
        </p>
      )}
    </div>
  );
};

export default UnifiedDownloadButton; 