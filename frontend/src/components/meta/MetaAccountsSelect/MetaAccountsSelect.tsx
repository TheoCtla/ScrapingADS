import React, { useState, useRef, useEffect } from 'react';

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
        <h3>📘 Comptes Meta Ads</h3>
        <p>Chargement des comptes Meta...</p>
      </div>
    );
  }

  return (
    <div>
      <h3>📘 Comptes Meta Ads</h3>
      <div ref={dropdownRef} style={{ position: 'relative', width: '100%' }}>
        {/* Bouton principal du dropdown */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          style={{
            width: '100%',
            padding: '8px 12px',
            fontSize: '14px',
            textAlign: 'left',
            border: '1px solid #ccc',
            borderRadius: '4px',
            backgroundColor: 'white',
            cursor: 'pointer',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <span style={{ color: '#000' }}>
            {selectedAccount 
              ? cleanDisplayName(selectedAccount.name)
              : '-- Sélectionnez un compte Meta --'
            }
          </span>
          <span style={{ color: '#000' }}>{isOpen ? '▲' : '▼'}</span>
        </button>

        {/* Dropdown avec searchbar */}
        {isOpen && (
          <div style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderTop: 'none',
            borderRadius: '0 0 4px 4px',
            maxHeight: '300px',
            overflowY: 'auto',
            zIndex: 1000
          }}>
            {/* Searchbar */}
            <div style={{ padding: '8px' }}>
              <input
                type="text"
                placeholder="Search for an Item..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                autoFocus
              />
            </div>

            {/* Liste des comptes filtrés */}
            <div>
              {filteredAccounts.length > 0 ? (
                filteredAccounts.map((account) => (
                  <div
                    key={account.ad_account_id}
                    onClick={() => handleSelectAccount(account.ad_account_id)}
                    style={{
                      padding: '10px 12px',
                      cursor: 'pointer',
                      borderBottom: '1px solid #f0f0f0',
                      backgroundColor: account.ad_account_id === selectedMetaAccount ? '#e3f2fd' : 'white'
                    }}
                    onMouseEnter={(e) => {
                      if (account.ad_account_id !== selectedMetaAccount) {
                        e.currentTarget.style.backgroundColor = '#f5f5f5';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (account.ad_account_id !== selectedMetaAccount) {
                        e.currentTarget.style.backgroundColor = 'white';
                      }
                    }}
                  >
                                         <div style={{ fontWeight: '500', color: '#000' }}>
                       {cleanDisplayName(account.name)}
                     </div>
                  </div>
                ))
              ) : (
                <div style={{ padding: '12px', textAlign: 'center', color: '#000' }}>
                  Aucun compte trouvé
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <p style={{ color: '#000' }}>
        {selectedMetaAccount ? 
          `Compte sélectionné: ${cleanDisplayName(selectedAccount?.name || '')}` : 
          `${metaAccounts.length} comptes disponibles`
        }
      </p>
    </div>
  );
};

export default MetaAccountsSelect; 