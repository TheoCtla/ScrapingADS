import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import './ClientSelector.css';

interface ClientSelectorProps {
  selectedClient: string;
  onSelectClient: (clientName: string) => void;
  onClientInfoChange: (clientInfo: any) => void;
  onAuthorizedClientsChange?: (clients: string[]) => void;
}


const ClientSelector: React.FC<ClientSelectorProps> = ({ 
  selectedClient, 
  onSelectClient,
  onClientInfoChange,
  onAuthorizedClientsChange
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [authorizedClients, setAuthorizedClients] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReminder, setShowReminder] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Charger la liste des clients autorisés au montage du composant
  useEffect(() => {
    const fetchAuthorizedClients = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/list-authorized-clients`, {
          withCredentials: true,
        });
        
        if (response.data && response.data.clients) {
          setAuthorizedClients(response.data.clients);
          // Notifier le parent de la liste des clients autorisés
          if (onAuthorizedClientsChange) {
            onAuthorizedClientsChange(response.data.clients);
          }
          console.log(`✅ ${response.data.count} clients autorisés chargés`);
        } else {
          throw new Error('Format de réponse invalide');
        }
      } catch (error: any) {
        console.error('❌ Erreur lors du chargement des clients autorisés:', error);
        setError('Erreur lors du chargement des clients');
        setAuthorizedClients([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAuthorizedClients();
  }, []);

  // Résoudre les informations du client sélectionné
  useEffect(() => {
    const resolveClientInfo = async () => {
      if (!selectedClient) {
        onClientInfoChange(null);
        return;
      }

      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/resolve-client`, {
          client_name: selectedClient
        }, {
          withCredentials: true,
        });

        if (response.data && response.data.client_info) {
          onClientInfoChange(response.data.client_info);
          console.log('✅ Informations client résolues:', response.data.client_info);
        }
      } catch (error: any) {
        console.error('❌ Erreur lors de la résolution du client:', error);
        onClientInfoChange(null);
      }
    };

    resolveClientInfo();
  }, [selectedClient, onClientInfoChange]);

  // Filtrer les clients basé sur le terme de recherche
  const filteredClients = authorizedClients.filter(client =>
    client.toLowerCase().includes(searchTerm.toLowerCase())
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

  const handleSelectClient = (clientName: string) => {
    onSelectClient(clientName);
    setIsOpen(false);
    setSearchTerm('');
    
    // Afficher le rappel pour Orgeval et Melun
    if (clientName === 'AvivA Orgeval' || clientName === 'AvivA Melun') {
      setShowReminder(true);
      setTimeout(() => {
        alert('⚠️ RAPPEL IMPORTANT ⚠️\n\nCommence par faire Orgeval et Melun à la main !\n\nAssurez-vous que les données sont correctes avant de continuer.');
        setShowReminder(false);
      }, 100);
    }
  };

  if (loading) {
    return (
      <div className="client-selector-container">
        <h3 className="client-selector-title">Sélection du Client</h3>
        <p className="client-status">Chargement des clients autorisés...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="client-selector-container">
        <h3 className="client-selector-title">Sélection du Client</h3>
        <p className="client-error">Erreur: {error}</p>
      </div>
    );
  }

  return (
    <div className="client-selector-container">
      <h3 className="client-selector-title">Sélection du Client</h3>
      
      {/* Alerte pour Orgeval et Melun */}
      {showReminder && (
        <div className="client-reminder-alert">
          ⚠️ RAPPEL : Commence par faire Orgeval et Melun à la main !
        </div>
      )}
      
      <div ref={dropdownRef} className="client-dropdown-container">
        {/* Bouton principal du dropdown */}
        <button
          className="client-dropdown-button"
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className="client-dropdown-button-text">
            {selectedClient || 'Sélectionnez un client'}
          </span>
          <span className={`client-dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span>
        </button>

        {/* Dropdown avec searchbar */}
        {isOpen && (
          <div className="client-dropdown-menu">
            {/* Searchbar */}
            <input
              type="text"
              className="client-search-input"
              placeholder="Rechercher un client..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />

            {/* Liste des clients filtrés */}
            <div className="client-list">
              {filteredClients.length > 0 ? (
                filteredClients.map((client) => (
                  <div
                    key={client}
                    className={`client-item ${client === selectedClient ? 'selected' : ''} ${
                      client === 'AvivA Orgeval' || client === 'AvivA Melun' ? 'priority-client' : ''
                    }`}
                    onClick={() => handleSelectClient(client)}
                  >
                    <div className="client-name">
                      {client}
                      {(client === 'AvivA Orgeval' || client === 'AvivA Melun') && (
                        <span className="priority-badge">⚠️ Manuel</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="client-no-results">
                  Aucun client trouvé
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClientSelector;
