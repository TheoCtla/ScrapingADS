import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReportHeader from './components/unified/ReportHeader/ReportHeader';
import GoogleCustomersSelect from './components/google/GoogleCustomersSelect/GoogleCustomersSelect';
import MetaAccountsSelect from './components/meta/MetaAccountsSelect/MetaAccountsSelect';
import DateRangePicker from './components/unified/DateRangePicker/DateRangePicker';
import MetricsSelector from './components/google/GoogleMetricsSelector/MetricsSelector';
import MetaMetricsSelector from './components/meta/MetaMetricsSelector/MetaMetricsSelector';
import UnifiedDownloadButton from './components/unified/UnifiedDownloadButton/UnifiedDownloadButton';

const App: React.FC = () => {
  // États Google Ads
  const [googleCustomers, setGoogleCustomers] = useState<{ customer_id: string; name: string; manager: boolean }[]>([]);
  const [selectedGoogleCustomer, setSelectedGoogleCustomer] = useState<string>('');

  // États Meta Ads
  const [metaAccounts, setMetaAccounts] = useState<{ ad_account_id: string; name: string; status: string }[]>([]);
  const [selectedMetaAccount, setSelectedMetaAccount] = useState<string>('');

  // États communs
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [sheetMonth, setSheetMonth] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [contactEnabled, setContactEnabled] = useState<boolean>(true);
  const [itineraireEnabled, setItineraireEnabled] = useState<boolean>(true);
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

  // Récupération des clients Google
  useEffect(() => {
    const fetchGoogleCustomers = async () => {
      try {
        console.log('🔄 Fetching Google customers...');
        const response = await axios.get('http://localhost:5050/list-customers', {
          withCredentials: true,
        });
        console.log('✅ Google response:', response.data);
        if (Array.isArray(response.data)) {
          setGoogleCustomers(response.data);
          console.log(`✅ Set ${response.data.length} Google customers`);
        } else {
          console.error('❌ Unexpected format:', response.data);
        }
      } catch (error: any) {
        console.error('❌ Error fetching Google customers:', error?.message || error);
        if (error?.response) {
          console.error('Response data:', error.response.data);
          console.error('Status:', error.response.status);
        } else if (error?.request) {
          console.error('Request made but no response received:', error.request);
        }
      }
    };
    fetchGoogleCustomers();
  }, []);

  // Récupération des comptes Meta
  useEffect(() => {
    const fetchMetaAccounts = async () => {
      try {
        console.log('🔄 Fetching Meta accounts...');
        const response = await axios.get('http://localhost:5050/list-meta-accounts', {
          withCredentials: true,
        });
        console.log('✅ Meta response:', response.data);
        if (Array.isArray(response.data)) {
          setMetaAccounts(response.data);
          console.log(`✅ Set ${response.data.length} Meta accounts`);
        } else {
          console.error('❌ Unexpected Meta format:', response.data);
        }
      } catch (error: any) {
        console.error('❌ Error fetching Meta accounts:', error?.message || error);
        if (error?.response) {
          console.error('Response data:', error.response.data);
          console.error('Status:', error.response.status);
        } else if (error?.request) {
          console.error('Request made but no response received:', error.request);
        }
      }
    };
    fetchMetaAccounts();
  }, []);

  // Gestionnaires pour Google Customers
  const handleSelectGoogleCustomer = (customerId: string) => {
    setSelectedGoogleCustomer(customerId);
  };

  // Gestionnaires pour Meta Accounts
  const handleSelectMetaAccount = (accountId: string) => {
    setSelectedMetaAccount(accountId);
  };




  const handleUnifiedDownload = async () => {
    console.log('🔧 DEBUG: handleUnifiedDownload appelée');
    console.log('🔧 DEBUG: selectedGoogleCustomer:', selectedGoogleCustomer);
    console.log('🔧 DEBUG: selectedMetaAccount:', selectedMetaAccount);
    console.log('🔧 DEBUG: startDate:', startDate);
    console.log('🔧 DEBUG: endDate:', endDate);
    console.log('🔧 DEBUG: selectedGoogleMetrics:', selectedGoogleMetrics);
    console.log('🔧 DEBUG: selectedMetaMetrics:', selectedMetaMetrics);
    
    // Déterminer le type d'envoi
    const hasGoogle = !!selectedGoogleCustomer;
    const hasMeta = !!selectedMetaAccount;
    let sendType = '';
    if (hasGoogle && hasMeta) {
      sendType = 'Google + Meta';
    } else if (hasGoogle) {
      sendType = 'Google uniquement';
    } else if (hasMeta) {
      sendType = 'Meta uniquement';
    } else {
      sendType = 'Aucun';
    }
    console.log(`🎯 Mode d'envoi: ${sendType}`);
    
    setLoading(true);
    try {
      const payload = {
        // Paramètres communs
        start_date: startDate,
        end_date: endDate,
        sheet_month: sheetMonth,
        contact: contactEnabled,
        itineraire: itineraireEnabled,
        
        // Paramètres Google Ads (tableau avec un seul élément si sélectionné)
        google_customers: selectedGoogleCustomer ? [selectedGoogleCustomer] : [],
        google_metrics: selectedGoogleMetrics.map((m: { value: string }) => m.value),
        
        // Paramètres Meta Ads (tableau avec un seul élément si sélectionné)
        meta_accounts: selectedMetaAccount ? [selectedMetaAccount] : [],
        meta_metrics: selectedMetaMetrics.map((m: { value: string }) => m.value),
      };
      
      console.log('🔧 DEBUG: payload unifié envoyé:', payload);
      
              const response = await axios.post('http://localhost:5050/export-unified-report', payload);

      console.log('🔧 DEBUG: response reçue:', response);

      if (response.data.success) {
        alert(`✅ Succès ! ${response.data.message}\n\n` +
              `Mises à jour réussies: ${response.data.successful_updates.length}\n` +
              `Échecs: ${response.data.failed_updates.length}`);
        
        console.log('✅ Mises à jour réussies:', response.data.successful_updates);
        if (response.data.failed_updates.length > 0) {
          console.log('⚠️ Échecs:', response.data.failed_updates);
        }
      } else {
        alert('❌ Erreur lors de l\'envoi au Google Sheet');
        console.error('❌ Response body:', response.data);
      }
      
      console.log('🔧 DEBUG: Envoi au Google Sheet terminé avec succès');
    } catch (error: any) {
      console.error('❌ ERROR: Error downloading unified report:', error);
      
      let errorMessage = 'Erreur inconnue lors de l\'envoi';
      
      if (error?.response) {
        console.error('❌ ERROR: Response data:', error.response.data);
        console.error('❌ ERROR: Response status:', error.response.status);
        
        // Afficher l'erreur spécifique du backend
        if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.status === 400) {
          errorMessage = 'Paramètres invalides. Vérifiez vos sélections.';
        } else if (error.response.status === 500) {
          errorMessage = 'Erreur serveur. Réessayez dans quelques instants.';
        }
      }
      
      alert(`❌ Erreur: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <ReportHeader customerCount={googleCustomers.length + metaAccounts.length} />
      
      <DateRangePicker 
        startDate={startDate}
        endDate={endDate}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
      />
      
      <div>
        <label htmlFor="sheet_month">
          📅 Mois pour le Google Sheet :
        </label>
        <input
          type="text"
          id="sheet_month"
          value={sheetMonth}
          onChange={(e) => setSheetMonth(e.target.value)}
          placeholder="Ex: juillet 2025"
        />
      </div>
      
      <div style={{ margin: '15px 0' }}>
        <span style={{ marginRight: '10px', fontWeight: 'bold' }}>Templates :</span>
        <button 
          onClick={handleCuisinistesToggle}
          style={{ marginRight: '10px', padding: '5px 10px' }}
        >
          Cuisinistes
        </button>
        <button 
          onClick={handleLitiersToggle}
          style={{ padding: '5px 10px' }}
        >
          Litiers
        </button>
      </div>
      
      <div style={{ margin: '20px 0', padding: '15px', border: '2px solid #4285f4', borderRadius: '8px' }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#4285f4' }}>🔵 SECTION GOOGLE ADS</h3>
        
        <GoogleCustomersSelect 
          googleCustomers={googleCustomers}
          selectedGoogleCustomer={selectedGoogleCustomer}
          onSelectGoogleCustomer={handleSelectGoogleCustomer}
        />
        
        <MetricsSelector 
          availableMetrics={availableGoogleMetrics}
          selectedMetrics={selectedGoogleMetrics}
          onMetricsChange={setSelectedGoogleMetrics}
        />
      </div>
      
      <div style={{ margin: '20px 0', padding: '15px', border: '2px solid #1877f2', borderRadius: '8px' }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#1877f2' }}>🔴 SECTION META ADS</h3>
        
        <MetaAccountsSelect 
          metaAccounts={metaAccounts}
          selectedMetaAccount={selectedMetaAccount}
          onSelectMetaAccount={handleSelectMetaAccount}
        />
        
        <MetaMetricsSelector 
          availableMetrics={availableMetaMetrics}
          selectedMetrics={selectedMetaMetrics}
          onMetricsChange={setSelectedMetaMetrics}
        />
      </div>
      
      <UnifiedDownloadButton 
        loading={loading}
        onClick={handleUnifiedDownload}
        hasGoogleSelection={!!selectedGoogleCustomer}
        hasMetaSelection={!!selectedMetaAccount}
      />
    </div>
  );
};

export default App;
