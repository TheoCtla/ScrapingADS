import React from 'react';

interface UnifiedDownloadButtonProps {
  loading: boolean;
  onClick: () => void;
  hasGoogleSelection: boolean;
  hasMetaSelection: boolean;
}

const UnifiedDownloadButton: React.FC<UnifiedDownloadButtonProps> = ({ 
  loading, 
  onClick, 
  hasGoogleSelection, 
  hasMetaSelection 
}) => {
  const hasSelection = hasGoogleSelection || hasMetaSelection;
  const isDisabled = loading || !hasSelection;

  const getButtonText = () => {
    if (loading) {
      return '⏳ Envoi en cours...';
    }
    
    if (!hasSelection) {
      return '❌ Sélectionnez au moins un compte';
    }
    
    let platforms = [];
    if (hasGoogleSelection) platforms.push('Google');
    if (hasMetaSelection) platforms.push('Meta');
    
    return `📊 Envoyer au Google Sheet (${platforms.join(' + ')})`;
  };

  return (
    <div>
      <div>
        <div>
          <span>🔍 Google Ads: {hasGoogleSelection ? '✅' : '❌'}</span>
        </div>
        <div>
          <span>📘 Meta Ads: {hasMetaSelection ? '✅' : '❌'}</span>
        </div>
      </div>
      
      <button
        onClick={onClick}
        disabled={isDisabled}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: isDisabled ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isDisabled ? 'not-allowed' : 'pointer'
        }}
      >
        {getButtonText()}
      </button>
      
      {!hasSelection && (
        <p>
          💡 Sélectionnez au moins un compte Google ou Meta pour commencer
        </p>
      )}
    </div>
  );
};

export default UnifiedDownloadButton; 