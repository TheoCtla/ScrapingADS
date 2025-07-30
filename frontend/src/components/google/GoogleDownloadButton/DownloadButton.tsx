import React from 'react';
import './DownloadButton.css';

interface DownloadButtonProps {
  loading: boolean;
  onClick: () => void | Promise<void>;
  disabled?: boolean;
}

export default function DownloadButton({ 
  loading, 
  onClick, 
  disabled = false 
}: DownloadButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
    >
      {loading ? 'Chargement...' : 'Télécharger les stats'}
    </button>
  );
} 