import React from 'react';

interface MetaMetric {
  label: string;
  value: string;
}

interface MetaMetricsSelectorProps {
  availableMetrics: MetaMetric[];
  selectedMetrics: MetaMetric[];
  onMetricsChange: (metrics: MetaMetric[]) => void;
}

const MetaMetricsSelector: React.FC<MetaMetricsSelectorProps> = ({
  availableMetrics,
  selectedMetrics,
  onMetricsChange,
}) => {
  const handleSelectAll = () => {
    const anySelected = selectedMetrics.length > 0;
    onMetricsChange(anySelected ? [] : [...availableMetrics]);
  };

  const handleMetricToggle = (metric: MetaMetric) => {
    const isSelected = selectedMetrics.some(m => m.value === metric.value);
    
    if (isSelected) {
      // Désélectionner la métrique
      const updatedMetrics = selectedMetrics.filter(m => m.value !== metric.value);
      onMetricsChange(updatedMetrics);
    } else {
      // Sélectionner la métrique
      const updatedMetrics = [...selectedMetrics, metric];
      onMetricsChange(updatedMetrics);
    }
  };

  return (
    <div style={{ margin: '20px 0', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h4 style={{ margin: '0 0 15px 0', color: '#1877f2' }}>📊 Métriques Meta Ads</h4>
      <label style={{ display: 'block', marginBottom: '10px' }}>Choisissez les données à inclure :</label>
      <div style={{ marginBottom: '15px' }}>
        <button 
          onClick={handleSelectAll}
          style={{ marginRight: '10px', padding: '5px 10px' }}
        >
          {selectedMetrics.length > 0 ? 'Tout désélectionner' : 'Tout sélectionner'}
        </button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
        {availableMetrics.map((metric) => {
          const isSelected = selectedMetrics.some(m => m.value === metric.value);
          return (
            <div key={metric.value} style={{ display: 'flex', alignItems: 'center' }}>
              <input
                type="checkbox"
                id={`meta-${metric.value}`}
                checked={isSelected}
                onChange={() => handleMetricToggle(metric)}
                style={{ marginRight: '8px' }}
              />
              <label 
                htmlFor={`meta-${metric.value}`}
                style={{ 
                  cursor: 'pointer',
                  fontWeight: isSelected ? 'bold' : 'normal',
                  color: isSelected ? '#1877f2' : '#333'
                }}
              >
                {metric.label}
              </label>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MetaMetricsSelector; 