import React, { useState, useRef, useEffect } from 'react';
import './MetaAccountsSelect.css';

interface MetaAccount {
  ad_account_id: string;
  name: string;
  status: string | number;
}

interface MetaAccountsSelectProps {
  metaAccounts: MetaAccount[];
  selectedMetaAccount: string;
  onSelectMetaAccount: (accountId: string) => void;
}

const MetaAccountsSelect: React.FC<MetaAccountsSelectProps> = ({ 
  metaAccounts, 
  selectedMetaAccount, 
  onSelectMetaAccount 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fonction pour nettoyer le nom en ne gardant que les lettres, chiffres, espaces et caractères courants
  const cleanDisplayName = (name: string): string => {
    if (!name) return '';
    // Garde seulement les lettres, chiffres, espaces, tirets, apostrophes et parenthèses
    return name.replace(/[^\w\s\-'()àáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ]/gi, '').trim();
  };



  // Filtrer les comptes basé sur le terme de recherche (utilise le nom nettoyé)
  const filteredAccounts = metaAccounts.filter(account =>
    account.name && cleanDisplayName(account.name).toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Fermer le dropdown si on clique à l'extérieur
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectAccount = (accountId: string) => {
    onSelectMetaAccount(accountId);
    setIsOpen(false);
    setSearchTerm('');
  };

  const selectedAccount = metaAccounts.find(a => a.ad_account_id === selectedMetaAccount);

  if (metaAccounts.length === 0) {
    return (
      <div>
        <h3>Comptes Meta Ads</h3>
        <p>Chargement des comptes Meta...</p>
      </div>
    );
  }

  return (
    <div className="meta-accounts-select-container">
      <h3 className="meta-accounts-select-title">Comptes Meta Ads</h3>
      <div ref={dropdownRef} className="meta-dropdown-container">
        {/* Bouton principal du dropdown */}
        <button
          className="meta-dropdown-button"
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className="meta-dropdown-button-text">
            {selectedAccount 
              ? cleanDisplayName(selectedAccount.name)
              : 'Cherche ton compte Meta'
            }
          </span>
          <span className={`meta-dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span>
        </button>

        {/* Dropdown avec searchbar */}
        {isOpen && (
          <div className="meta-dropdown-menu">
            {/* Searchbar */}
            <input
              type="text"
              className="meta-search-input"
              placeholder="Search for an Item..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />

            {/* Liste des comptes filtrés */}
            <div className="meta-account-list">
              {filteredAccounts.length > 0 ? (
                filteredAccounts.map((account) => (
                  <div
                    key={account.ad_account_id}
                    className={`meta-account-item ${account.ad_account_id === selectedMetaAccount ? 'selected' : ''}`}
                    onClick={() => handleSelectAccount(account.ad_account_id)}
                  >
                    <div className="meta-account-name">
                      {cleanDisplayName(account.name)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="meta-no-results">
                  Aucun compte trouvé
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetaAccountsSelect; 