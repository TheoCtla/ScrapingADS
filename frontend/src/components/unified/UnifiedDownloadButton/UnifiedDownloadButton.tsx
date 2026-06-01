import React from 'react';
import './UnifiedDownloadButton.css';

interface UnifiedDownloadButtonProps {
  loading: boolean;
  onClick: () => void;
  hasGoogleSelection: boolean;
  hasMetaSelection: boolean;
  hasAnalyticsSelection?: boolean;
  onBulkScraping?: () => void;
  bulkScrapingLoading?: boolean;
  hasAuthorizedClients?: boolean;
  hasAnyMetrics?: boolean;
  onGenerateReports?: () => void;
  generateReportsLoading?: boolean;
}

const UnifiedDownloadButton: React.FC<UnifiedDownloadButtonProps> = ({
  loading,
  onClick,
  hasGoogleSelection,
  hasMetaSelection,
  hasAnalyticsSelection = false,
  onBulkScraping,
  bulkScrapingLoading = false,
  hasAuthorizedClients = false,
  hasAnyMetrics = false,
  onGenerateReports,
  generateReportsLoading = false
}) => {
  const hasSelection = hasGoogleSelection || hasMetaSelection || hasAnalyticsSelection;
  const isDisabled = loading || !hasSelection;

  const getButtonText = () => {
    if (loading) {
      return 'Envoi en cours...';
    }

    if (!hasSelection) {
      return 'Sélectionne au moins un compte';
    }

    const platforms: string[] = [];
    if (hasGoogleSelection) platforms.push('Google');
    if (hasMetaSelection) platforms.push('Meta');
    if (hasAnalyticsSelection) platforms.push('Analytics');

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
        {onGenerateReports && (
          <button
            className="generate-reports-button"
            onClick={onGenerateReports}
            disabled={generateReportsLoading}
          >
            {generateReportsLoading ? 'Génération en cours...' : 'Générer tous les rapports PPTX'}
          </button>
        )}
      </div>
      
      {!hasSelection && (
        <p className="help-text">
          Sélectionne au moins un compte Google, Meta ou Analytics pour commencer
        </p>
      )}
    </div>
  );
};

export default UnifiedDownloadButton; 