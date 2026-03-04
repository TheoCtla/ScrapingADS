import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import ReportHeader from '../unified/ReportHeader/ReportHeader';
import ClientSelector from '../unified/ClientSelector/ClientSelector';
import DateRangePicker from '../unified/DateRangePicker/DateRangePicker';
import MetricsSelector from '../google/GoogleMetricsSelector/MetricsSelector';
import MetaMetricsSelector from '../meta/MetaMetricsSelector/MetaMetricsSelector';
import UnifiedDownloadButton from '../unified/UnifiedDownloadButton/UnifiedDownloadButton';
import BulkScrapingProgress from '../unified/BulkScrapingProgress/BulkScrapingProgress';
import SuccessModal from '../SuccessModal/SuccessModal';
import { QUOTA_CONFIG, getRetryDelay, isQuotaError } from '../../config/quotas';
import '../../App.css';

const ScrapingRapports: React.FC = () => {
  // Fonction pour calculer les dates du mois précédent
  const getLastMonthDates = () => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    
    // Mois précédent
    const lastMonth = currentMonth === 0 ? 11 : currentMonth - 1;
    const lastMonthYear = currentMonth === 0 ? currentYear - 1 : currentYear;
    
    // Premier jour du mois précédent (1er du mois)
    const firstDay = new Date(lastMonthYear, lastMonth, 1);
    
    // Dernier jour du mois précédent (dernier jour du mois)
    const lastDay = new Date(lastMonthYear, lastMonth + 1, 0);
    
    // Format YYYY-MM-DD pour les inputs date
    const formatDate = (date: Date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    
    return {
      startDate: formatDate(firstDay),
      endDate: formatDate(lastDay)
    };
  };

  // État du client sélectionné (NOUVEAU)
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [clientInfo, setClientInfo] = useState<any>(null);
  
  // État pour la modal de succès
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successData, setSuccessData] = useState({
    message: '',
    successfulUpdates: 0,
    failedUpdates: 0
  });
  
  // État pour le scraping en masse
  const [authorizedClients, setAuthorizedClients] = useState<string[]>([]);
  const [filteredClients, setFilteredClients] = useState<string[]>([]);
  const [bulkScrapingState, setBulkScrapingState] = useState({
    isProcessing: false,
    currentIndex: 0,
    currentClient: '',
    completedClients: [] as string[],
    failedClients: [] as { client: string; error: string }[],
    shouldCancel: false
  });
  const bulkScrapingRef = useRef(bulkScrapingState);
  bulkScrapingRef.current = bulkScrapingState;

  // États communs - initialisés avec les dates du mois précédent
  const lastMonthDates = getLastMonthDates();
  const [startDate, setStartDate] = useState<string>(lastMonthDates.startDate);
  const [endDate, setEndDate] = useState<string>(lastMonthDates.endDate);
  
  // Fonction pour obtenir le nom du mois précédent en anglais
  const getLastMonthName = () => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    
    // Mois précédent
    const lastMonth = currentMonth === 0 ? 11 : currentMonth - 1;
    const lastMonthYear = currentMonth === 0 ? currentYear - 1 : currentYear;
    
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    return `${monthNames[lastMonth]} ${lastMonthYear}`;
  };
  
  const [sheetMonth, setSheetMonth] = useState<string>(getLastMonthName());
  const [loading, setLoading] = useState<boolean>(false);
  const [contactEnabled, setContactEnabled] = useState<boolean>(true);
  const [itineraireEnabled, setItineraireEnabled] = useState<boolean>(true);
  const [cuisinistesSelected, setCuisinistesSelected] = useState<boolean>(false);
  const [litiersSelected, setLitiersSelected] = useState<boolean>(false);
  // Liste des métriques Google Ads personnalisées par canal
  const [availableGoogleMetrics, setAvailableGoogleMetrics] = useState<{ label: string; value: string }[]>([
    // Métriques Perfmax
    { label: "Clics Perfmax", value: "metrics.clicks_perfmax" },
    { label: "Impressions Perfmax", value: "metrics.impressions_perfmax" },
    { label: "CPC Perfmax", value: "metrics.average_cpc_perfmax" },
    { label: "Coût Perfmax", value: "metrics.cost_perfmax" },

    // Métriques Search
    { label: "Clics Search", value: "metrics.clicks_search" },
    { label: "Impressions Search", value: "metrics.impressions_search" },
    { label: "CPC Search", value: "metrics.average_cpc_search" },
    { label: "Coût Search", value: "metrics.cost_search" },

    // Métriques Display
    { label: "Clics Display", value: "metrics.clicks_display" },
    { label: "Impressions Display", value: "metrics.impressions_display" },
    { label: "CPC Display", value: "metrics.average_cpc_display" },
    { label: "Coût Display", value: "metrics.cost_display" },

    // Métriques globales
    { label: "Coût total", value: "metrics.cost_micros" },
    { label: "Total Clics", value: "metrics.total_clicks" },
    { label: "CTR", value: "metrics.ctr" },
    { label: "Impressions totales", value: "metrics.impressions" },
    { label: "CPC moyen", value: "metrics.average_cpc" },
    
    // Métriques de conversion (Objectifs)
    { label: "Contact", value: "metrics.conversions" },
    { label: "Appels téléphoniques", value: "metrics.phone_calls" }
    // { label: "Itinéraires", value: "metrics.store_visits" } // Supprimé car non supporté par l'API
  ]);
  // Métriques Google sélectionnées par l'utilisateur
  const [selectedGoogleMetrics, setSelectedGoogleMetrics] = useState<{ label: string; value: string }[]>([]);

  // Liste des métriques Meta Ads (basées sur le screenshot)
  const [availableMetaMetrics, setAvailableMetaMetrics] = useState<{ label: string; value: string }[]>([
    { label: "Clics Meta", value: "meta.clicks" },
    { label: "Impressions Meta", value: "meta.impressions" },
    { label: "CTR Meta", value: "meta.ctr" },
    { label: "CPL Meta", value: "meta.cpl" },
    { label: "CPC Meta", value: "meta.cpc" },
    { label: "Cout Meta ADS", value: "meta.spend" },
    { label: "Contact Meta", value: "meta.contact" },
    { label: "Recherche de lieux", value: "meta.recherche_lieux" },
  ]);
  // Métriques Meta sélectionnées par l'utilisateur
  const [selectedMetaMetrics, setSelectedMetaMetrics] = useState<{ label: string; value: string }[]>([]);

  // Fonctions pour les boutons Cuisinistes et Litiers
  const handleCuisinistesToggle = () => {
    setCuisinistesSelected(!cuisinistesSelected);
    
    // Toggle : ajoute ou retire les métriques Search sans toucher aux autres
    const group = availableGoogleMetrics.filter(metric =>
      /search/i.test(metric.label)
    );
    const groupValues = group.map(m => m.value);
    const allInGroupSelected =
      groupValues.length > 0 &&
      groupValues.every(v => selectedGoogleMetrics.some(s => s.value === v));
    
    // Métriques Meta pour le template Cuisinistes
    const metaGroup = availableMetaMetrics.filter(metric =>
      ['meta.impressions', 'meta.clicks', 'meta.ctr', 'meta.cpl', 'meta.cpc'].includes(metric.value)
    );
    const metaGroupValues = metaGroup.map(m => m.value);
    const allMetaInGroupSelected =
      metaGroupValues.length > 0 &&
      metaGroupValues.every(v => selectedMetaMetrics.some(s => s.value === v));
    
    if (allInGroupSelected && allMetaInGroupSelected) {
      // Retirer les groupes Google et Meta
      setSelectedGoogleMetrics(
        selectedGoogleMetrics.filter(m => !groupValues.includes(m.value))
      );
      setSelectedMetaMetrics(
        selectedMetaMetrics.filter(m => !metaGroupValues.includes(m.value))
      );
    } else {
      // Ajouter les groupes Google et Meta, sans dupliquer
      const existingGoogleValues = selectedGoogleMetrics.map(m => m.value);
      const toAddGoogle = group.filter(m => !existingGoogleValues.includes(m.value));
      setSelectedGoogleMetrics([...selectedGoogleMetrics, ...toAddGoogle]);
      
      const existingMetaValues = selectedMetaMetrics.map(m => m.value);
      const toAddMeta = metaGroup.filter(m => !existingMetaValues.includes(m.value));
      setSelectedMetaMetrics([...selectedMetaMetrics, ...toAddMeta]);
    }
  };

  const handleLitiersToggle = () => {
    setLitiersSelected(!litiersSelected);
    
    // Toggle : ajoute ou retire les métriques Litiers sans toucher aux autres
    const group = availableGoogleMetrics.filter(metric =>
      ["metrics.clicks_search", "metrics.clicks_perfmax", "metrics.clicks_display", "metrics.impressions"].includes(metric.value)
    );
    const groupValues = group.map(m => m.value);
    const allInGroupSelected =
      groupValues.length > 0 &&
      groupValues.every(v => selectedGoogleMetrics.some(s => s.value === v));
    
    // Métriques Meta pour le template Litiers
    const metaGroup = availableMetaMetrics.filter(metric =>
      ['meta.impressions', 'meta.clicks', 'meta.cpc'].includes(metric.value)
    );
    const metaGroupValues = metaGroup.map(m => m.value);
    const allMetaInGroupSelected =
      metaGroupValues.length > 0 &&
      metaGroupValues.every(v => selectedMetaMetrics.some(s => s.value === v));
    
    if (allInGroupSelected && allMetaInGroupSelected) {
      // Retirer les groupes Google et Meta
      setSelectedGoogleMetrics(
        selectedGoogleMetrics.filter(m => !groupValues.includes(m.value))
      );
      setSelectedMetaMetrics(
        selectedMetaMetrics.filter(m => !metaGroupValues.includes(m.value))
      );
    } else {
      // Ajouter les groupes Google et Meta, sans dupliquer
      const existingGoogleValues = selectedGoogleMetrics.map(m => m.value);
      const toAddGoogle = group.filter(m => !existingGoogleValues.includes(m.value));
      setSelectedGoogleMetrics([...selectedGoogleMetrics, ...toAddGoogle]);
      
      const existingMetaValues = selectedMetaMetrics.map(m => m.value);
      const toAddMeta = metaGroup.filter(m => !existingMetaValues.includes(m.value));
      setSelectedMetaMetrics([...selectedMetaMetrics, ...toAddMeta]);
    }
  };

  // Gestionnaire pour la sélection de client (NOUVEAU)
  const handleSelectClient = (clientName: string) => {
    setSelectedClient(clientName);
  };

  // Gestionnaire pour les informations client (NOUVEAU)
  const handleClientInfoChange = useCallback((info: any) => {
    setClientInfo(info);
  }, []);


  // Gestionnaire pour la liste des clients autorisés
  const handleAuthorizedClientsChange = (clients: string[]) => {
    setAuthorizedClients(clients);
    setFilteredClients(clients); // Initialiser avec tous les clients
  };

  // Fonction pour obtenir les clients filtrés de la searchbar
  const getFilteredClientsFromSearchbar = async (searchTerm: string = '') => {
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5050'}/list-filtered-clients`, {
        search_term: searchTerm
      }, {
        withCredentials: true,
      });
      
      if (response.data && response.data.clients) {
        return response.data.clients;
      }
      return [];
    } catch (error) {
      console.error('❌ Erreur lors de la récupération des clients filtrés:', error);
      return authorizedClients; // Fallback vers la liste complète
    }
  };




  const handleUnifiedDownload = async () => {
    if (!selectedClient) {
      alert('Veuillez sélectionner un client');
      return;
    }
    
    // Déterminer le type d'envoi basé sur les plateformes disponibles
    const hasGoogle = clientInfo?.google_ads?.configured && selectedGoogleMetrics.length > 0;
    const hasMeta = clientInfo?.meta_ads?.configured && selectedMetaMetrics.length > 0;
    let sendType = '';
    if (hasGoogle && hasMeta) {
      sendType = 'Google + Meta';
    } else if (hasGoogle) {
      sendType = 'Google uniquement';
    } else if (hasMeta) {
      sendType = 'Meta uniquement';
    } else {
      sendType = 'Aucune plateforme configurée';
    }
    
    if (sendType === 'Aucune plateforme configurée') {
      alert('Aucune plateforme configurée pour ce client ou aucune métrique sélectionnée');
      return;
    }
    
    setLoading(true);
    try {
      const payload = {
        // Paramètres communs
        start_date: startDate,
        end_date: endDate,
        sheet_month: sheetMonth,
        contact: contactEnabled,
        itineraire: itineraireEnabled,
        
        // NOUVEAU: Client sélectionné
        selected_client: selectedClient,
        
        // Paramètres Google Ads
        google_metrics: selectedGoogleMetrics.map((m: { value: string }) => m.value),
        
        // Paramètres Meta Ads
        meta_metrics: selectedMetaMetrics.map((m: { value: string }) => m.value),
      };
      
      
              const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5050'}/export-unified-report`, payload);


      if (response.data.success) {
        // Afficher la belle popup au lieu de l'alerte
        setSuccessData({
          message: response.data.message,
          successfulUpdates: response.data.successful_updates.length,
          failedUpdates: response.data.failed_updates.length
        });
        setShowSuccessModal(true);
        
        if (response.data.failed_updates.length > 0) {
          console.log('Échecs:', response.data.failed_updates);
        }
      } else {
        alert('Erreur lors de l\'envoi au Google Sheet');
        console.error('Response body:', response.data);
      }
      
    } catch (error: any) {
              console.error('ERROR: Error downloading unified report:', error);
      
      let errorMessage = 'Erreur inconnue lors de l\'envoi';
      
      if (error?.response) {
        console.error('ERROR: Response data:', error.response.data);
                  console.error('ERROR: Response status:', error.response.status);
        
        // Afficher l'erreur spécifique du backend
        if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.status === 400) {
          errorMessage = 'Paramètres invalides. Vérifiez vos sélections.';
        } else if (error.response.status === 500) {
          errorMessage = 'Erreur serveur. Réessayez dans quelques instants.';
        }
      }
      
              alert(`Erreur: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour capturer le contexte UI actuel
  const captureUIContext = () => {
    return {
      startDate,
      endDate,
      sheetMonth,
      contactEnabled,
      itineraireEnabled,
      selectedGoogleMetrics: selectedGoogleMetrics.map((m: { value: string }) => m.value),
      selectedMetaMetrics: selectedMetaMetrics.map((m: { value: string }) => m.value),
    };
  };

  // Fonction pour traiter un client individuel (réutilise la logique existante)
  const processSingleClient = async (clientName: string, context: any) => {
    try {
      
      const payload = {
        // Paramètres communs
        start_date: context.startDate,
        end_date: context.endDate,
        sheet_month: context.sheetMonth,
        contact: context.contactEnabled,
        itineraire: context.itineraireEnabled,
        
        // Client sélectionné
        selected_client: clientName,
        
        // Paramètres Google Ads
        google_metrics: context.selectedGoogleMetrics,
        
        // Paramètres Meta Ads
        meta_metrics: context.selectedMetaMetrics,
      };
      
      console.log(`📤 Envoi du payload pour ${clientName}:`, payload);
      
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5050'}/export-unified-report`, payload);
      
      if (response.data.success) {
        console.log(`✅ Succès pour ${clientName}:`, response.data.message);
        return { success: true, message: response.data.message };
      } else {
        console.error(`❌ Échec pour ${clientName}:`, response.data);
        return { success: false, error: 'Réponse d\'erreur du serveur' };
      }
      
    } catch (error: any) {
      console.error(`❌ Erreur pour ${clientName}:`, error);
      
      let errorMessage = 'Erreur inconnue';
      let isQuotaErrorFlag = false;
      
      if (error?.response?.data?.error) {
        errorMessage = error.response.data.error;
        isQuotaErrorFlag = isQuotaError(errorMessage);
      } else if (error?.response?.status === 429) {
        errorMessage = 'Quota dépassé (429)';
        isQuotaErrorFlag = true;
      } else if (error?.response?.status === 400) {
        errorMessage = 'Paramètres invalides';
      } else if (error?.response?.status === 500) {
        errorMessage = 'Erreur serveur';
      } else if (error?.message) {
        errorMessage = error.message;
        isQuotaErrorFlag = isQuotaError(errorMessage);
      }
      
      return { 
        success: false, 
        error: errorMessage,
        isQuotaError: isQuotaErrorFlag
      };
    }
  };

  // Fonction principale de scraping en masse
  const handleBulkScraping = async () => {
    if (bulkScrapingState.isProcessing) {
      console.log('⚠️ Scraping en masse déjà en cours');
      return;
    }

    // Obtenir les clients filtrés de la searchbar (actuellement tous les clients)
    const clientsToProcess = await getFilteredClientsFromSearchbar();
    
    if (clientsToProcess.length === 0) {
      alert('Aucun client disponible pour le traitement');
      return;
    }

    // Vérifier qu'au moins une métrique est sélectionnée
    const hasGoogleMetrics = selectedGoogleMetrics.length > 0;
    const hasMetaMetrics = selectedMetaMetrics.length > 0;
    
    if (!hasGoogleMetrics && !hasMetaMetrics) {
      alert('Veuillez sélectionner au moins une métrique Google ou Meta');
      return;
    }

    // Capturer le contexte UI actuel (immutable)
    const uiContext = captureUIContext();
    console.log('📸 Contexte UI capturé:', uiContext);

    // Initialiser l'état de scraping
    setBulkScrapingState({
      isProcessing: true,
      currentIndex: 0,
      currentClient: '',
      completedClients: [],
      failedClients: [],
      shouldCancel: false
    });

    try {
      // Traitement séquentiel de chaque client
      for (let i = 0; i < clientsToProcess.length; i++) {
        const clientName = clientsToProcess[i];
        
        // Vérifier si l'annulation a été demandée
        if (bulkScrapingRef.current.shouldCancel) {
          console.log('🛑 Scraping annulé par l\'utilisateur');
          break;
        }

        // Mettre à jour l'état de progression
        setBulkScrapingState(prev => ({
          ...prev,
          currentIndex: i,
          currentClient: clientName
        }));

        console.log(`🔄 Traitement ${i + 1}/${clientsToProcess.length}: ${clientName}`);

        // Traiter le client avec retry et gestion des quotas
        let result = null;
        const maxRetries = QUOTA_CONFIG.MAX_RETRIES;
        
        for (let retry = 0; retry <= maxRetries; retry++) {
          if (retry > 0) {
            console.log(`🔄 Retry ${retry}/${maxRetries} pour ${clientName}`);
            
            // Utiliser la configuration pour les délais de retry
            const delay = getRetryDelay(retry - 1, result?.isQuotaError || false);
            const delaySeconds = Math.round(delay / 1000);
            
            if (result?.isQuotaError) {
              console.log(`⏳ Quota dépassé, attente de ${delaySeconds}s`);
            } else {
              console.log(`⏳ Attente backoff: ${delaySeconds}s`);
            }
            
            await new Promise(resolve => setTimeout(resolve, delay));
          }
          
          result = await processSingleClient(clientName, uiContext);
          
          if (result.success) {
            break;
          }
          
          // Si c'est le dernier retry, on garde l'erreur
          if (retry === maxRetries) {
            console.log(`❌ Échec définitif pour ${clientName} après ${maxRetries + 1} tentatives`);
          }
        }

        // Mettre à jour les résultats
        if (result && result.success) {
          setBulkScrapingState(prev => ({
            ...prev,
            completedClients: [...prev.completedClients, clientName]
          }));
        } else {
          setBulkScrapingState(prev => ({
            ...prev,
            failedClients: [...prev.failedClients, {
              client: clientName,
              error: result?.error || 'Erreur inconnue'
            }]
          }));
        }

        // Pause entre les clients pour respecter les quotas Google Sheets
        if (i < clientsToProcess.length - 1) {
          const delay = QUOTA_CONFIG.DELAY_BETWEEN_CLIENTS;
          const delaySeconds = Math.round(delay / 1000);
          console.log(`⏳ Pause de ${delaySeconds}s entre les clients pour respecter les quotas`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }

      // Finaliser le traitement
      const finalState = bulkScrapingRef.current;
      console.log('✅ Scraping en masse terminé');
      console.log(`📊 Résultats: ${finalState.completedClients.length} succès, ${finalState.failedClients.length} échecs`);

      // Afficher un résumé
      const message = `Scraping terminé!\n\n` +
        `✅ Succès: ${finalState.completedClients.length}\n` +
        `❌ Échecs: ${finalState.failedClients.length}`;
      
      alert(message);

    } catch (error) {
      console.error('❌ Erreur lors du scraping en masse:', error);
      alert('Erreur lors du scraping en masse: ' + (error as Error).message);
    } finally {
      // Finaliser l'état
      setBulkScrapingState(prev => ({
        ...prev,
        isProcessing: false,
        shouldCancel: false
      }));
    }
  };

  // Fonction d'annulation
  const handleCancelBulkScraping = () => {
    console.log('🛑 Demande d\'annulation du scraping en masse');
    setBulkScrapingState(prev => ({
      ...prev,
      shouldCancel: true
    }));
  };

  return (
    <div>
      
      <ReportHeader customerCount={1} />
      
      <DateRangePicker 
        startDate={startDate}
        endDate={endDate}
        sheetMonth={sheetMonth}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
        onSheetMonthChange={setSheetMonth}
      />
      
     {/* <div className="templates-section">
        <span className="templates-label">Templates :</span>
        <button 
          className={`template-button ${cuisinistesSelected ? 'selected' : ''}`}
          onClick={handleCuisinistesToggle}
        >
          Cuisinistes
        </button>
        <button 
          className={`template-button ${litiersSelected ? 'selected' : ''}`}
          onClick={handleLitiersToggle}
        >
          Litiers
        </button>
      </div> */}
      
      {/* NOUVEAU: Sélecteur de client unifié */}
      <div style={{ margin: '20px 0' }}>
        <ClientSelector 
          selectedClient={selectedClient}
          onSelectClient={handleSelectClient}
          onClientInfoChange={handleClientInfoChange}
          onAuthorizedClientsChange={handleAuthorizedClientsChange}
        />
      </div>
      
      {/* Affichage des informations du client sélectionné */}
      {clientInfo && (
        <div style={{ margin: '20px 0', padding: '15px', backgroundColor: '#0a0a0a', border: '2px solid #dbbc32' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#dbbc32', fontFamily: 'Allerta Stencil, sans-serif' }}>INFORMATIONS DU CLIENT</h4>
          <div style={{ display: 'flex', gap: '20px', fontSize: '14px' }}>
            <div>
              <strong>Google Ads:</strong> {clientInfo.google_ads.configured ? 'Configuré' : 'Non configuré'}
            </div>
            <div>
              <strong>Meta Ads:</strong> {clientInfo.meta_ads.configured ? 'Configuré' : 'Non configuré'}
            </div>
          </div>
        </div>
      )}
      
      <div style={{ display: 'flex', gap: '20px', margin: '20px 0' }}>
        <div style={{ flex: 2, padding: '15px', border: '2px solid #dbbc32'}}>
          <h3 style={{ margin: '0 0 2px 0', color: '#dbbc32' }}>SECTION GOOGLE ADS</h3>
          
          <MetricsSelector 
            availableMetrics={availableGoogleMetrics}
            selectedMetrics={selectedGoogleMetrics}
            onMetricsChange={setSelectedGoogleMetrics}
          />
        </div>
        
        <div style={{ flex: 1, padding: '15px', border: '2px solid #dbbc32', maxWidth: '500px' }}>
          <h3 style={{ margin: '0 0 2px 0', color: '#dbbc32' }}>SECTION META ADS</h3>
          
          <MetaMetricsSelector 
            availableMetrics={availableMetaMetrics}
            selectedMetrics={selectedMetaMetrics}
            onMetricsChange={setSelectedMetaMetrics}
          />
        </div>
      </div>
      
      
      {/* Avertissement Sud Gazon */}
      <div style={{ margin: '0 0 20px 0', padding: '10px', backgroundColor: '#3d1a1a', border: '1px solid #ff4444', color: '#ffaaaa', fontSize: '14px', borderRadius: '4px' }}>
        ⚠️ <strong>ATTENTION SUD GAZON :</strong> Traitement MANUEL requis pour la partie META ADS (pas d'accès API).
      </div>

      <UnifiedDownloadButton 
        loading={loading}
        onClick={handleUnifiedDownload}
        hasGoogleSelection={clientInfo?.google_ads?.configured && selectedGoogleMetrics.length > 0}
        hasMetaSelection={clientInfo?.meta_ads?.configured && selectedMetaMetrics.length > 0}
        onBulkScraping={handleBulkScraping}
        bulkScrapingLoading={bulkScrapingState.isProcessing}
        hasAuthorizedClients={authorizedClients.length > 0}
        hasAnyMetrics={selectedGoogleMetrics.length > 0 || selectedMetaMetrics.length > 0}
      />
      
      {/* Composant de progression pour le scraping en masse */}
      <BulkScrapingProgress
        isVisible={bulkScrapingState.isProcessing || bulkScrapingState.completedClients.length > 0 || bulkScrapingState.failedClients.length > 0}
        currentClient={bulkScrapingState.currentClient}
        currentIndex={bulkScrapingState.currentIndex}
        totalClients={filteredClients.length}
        isProcessing={bulkScrapingState.isProcessing}
        onCancel={handleCancelBulkScraping}
        completedClients={bulkScrapingState.completedClients}
        failedClients={bulkScrapingState.failedClients}
      />
      
      {/* Modal de succès */}
      <SuccessModal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        message={successData.message}
        successfulUpdates={successData.successfulUpdates}
        failedUpdates={successData.failedUpdates}
      />
    </div>
  );
};

export default ScrapingRapports;
