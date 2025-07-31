import React, { useState, useRef, useEffect } from 'react';
import './GoogleCustomersSelect.css';

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
      <div className="customers-select-container">
        <h3 className="customers-select-title">Clients Google Ads</h3>
        <p className="customer-status">Chargement des clients Google...</p>
      </div>
    );
  }

  return (
    <div className="customers-select-container">
      <h3 className="customers-select-title">Clients Google Ads</h3>
      <div ref={dropdownRef} className="dropdown-container">
        {/* Bouton principal du dropdown */}
        <button
          className="dropdown-button"
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className="dropdown-button-text">
            {selectedCustomer 
              ? cleanDisplayName(selectedCustomer.name)
              : 'Cherche ton client'
            }
          </span>
          <span className={`dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span>
        </button>

        {/* Dropdown avec searchbar */}
        {isOpen && (
          <div className="dropdown-menu">
            {/* Searchbar */}
            <input
              type="text"
              className="search-input"
              placeholder="Search for an Item..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />

            {/* Liste des clients filtrés */}
            <div className="customer-list">
              {filteredCustomers.length > 0 ? (
                filteredCustomers.map((customer) => (
                  <div
                    key={customer.customer_id}
                    className={`customer-item ${customer.customer_id === selectedGoogleCustomer ? 'selected' : ''}`}
                    onClick={() => handleSelectCustomer(customer.customer_id)}
                  >
                    <div className="customer-name">
                      {cleanDisplayName(customer.name)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-results">
                  Aucun client trouvé
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <p className="customer-status">
        {selectedGoogleCustomer ? 
          `Client sélectionné: ${cleanDisplayName(selectedCustomer?.name || '')}` : 
          `${googleCustomers.length} clients disponibles`
        }
      </p>
    </div>
  );
};

export default GoogleCustomersSelect; 