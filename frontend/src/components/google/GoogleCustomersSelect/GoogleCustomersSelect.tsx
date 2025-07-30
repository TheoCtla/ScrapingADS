import React, { useState, useRef, useEffect } from 'react';

interface GoogleCustomer {
  customer_id: string;
  name: string;
  manager: boolean;
}

interface GoogleCustomersSelectProps {
  googleCustomers: GoogleCustomer[];
  selectedGoogleCustomer: string;
  onSelectGoogleCustomer: (customerId: string) => void;
}

const GoogleCustomersSelect: React.FC<GoogleCustomersSelectProps> = ({ 
  googleCustomers, 
  selectedGoogleCustomer, 
  onSelectGoogleCustomer 
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



  // Filtrer les clients basé sur le terme de recherche (utilise le nom nettoyé)
  const filteredCustomers = googleCustomers.filter(customer =>
    customer.name && cleanDisplayName(customer.name).toLowerCase().includes(searchTerm.toLowerCase())
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

  const handleSelectCustomer = (customerId: string) => {
    onSelectGoogleCustomer(customerId);
    setIsOpen(false);
    setSearchTerm('');
  };

  const selectedCustomer = googleCustomers.find(c => c.customer_id === selectedGoogleCustomer);

  if (googleCustomers.length === 0) {
    return (
      <div>
        <h3>🔍 Clients Google Ads</h3>
        <p>Chargement des clients Google...</p>
      </div>
    );
  }

  return (
    <div>
      <h3>🔍 Clients Google Ads</h3>
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
            {selectedCustomer 
              ? cleanDisplayName(selectedCustomer.name)
              : '-- Sélectionnez un client Google --'
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

            {/* Liste des clients filtrés */}
            <div>
              {filteredCustomers.length > 0 ? (
                filteredCustomers.map((customer) => (
                  <div
                    key={customer.customer_id}
                    onClick={() => handleSelectCustomer(customer.customer_id)}
                    style={{
                      padding: '10px 12px',
                      cursor: 'pointer',
                      borderBottom: '1px solid #f0f0f0',
                      backgroundColor: customer.customer_id === selectedGoogleCustomer ? '#e3f2fd' : 'white'
                    }}
                    onMouseEnter={(e) => {
                      if (customer.customer_id !== selectedGoogleCustomer) {
                        e.currentTarget.style.backgroundColor = '#f5f5f5';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (customer.customer_id !== selectedGoogleCustomer) {
                        e.currentTarget.style.backgroundColor = 'white';
                      }
                    }}
                  >
                                         <div style={{ fontWeight: '500', color: '#000' }}>
                       {cleanDisplayName(customer.name)}
                     </div>
                  </div>
                ))
              ) : (
                <div style={{ padding: '12px', textAlign: 'center', color: '#000' }}>
                  Aucun client trouvé
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <p style={{ color: '#000' }}>
        {selectedGoogleCustomer ? 
          `Client sélectionné: ${cleanDisplayName(selectedCustomer?.name || '')}` : 
          `${googleCustomers.length} clients disponibles`
        }
      </p>
    </div>
  );
};

export default GoogleCustomersSelect; 