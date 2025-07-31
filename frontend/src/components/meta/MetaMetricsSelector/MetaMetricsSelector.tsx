import React, { useState } from 'react';
import './MetaMetricsSelector.css';

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
  const [selectAllActive, setSelectAllActive] = useState(false);
  
  const handleSelectAll = () => {
    const anySelected = selectedMetrics.length > 0;
    setSelectAllActive(!anySelected);
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
    <div className="meta-metrics-selector">
      <h4 className="meta-metrics-title">Métriques Meta Ads</h4>
      <div className="meta-metrics-header">
        <label className="meta-metrics-description">Choisissez les données à inclure :</label>
        
        <button 
          className={`meta-select-all-button ${selectAllActive ? 'selected' : ''}`}
          onClick={handleSelectAll}
        >
          {selectedMetrics.length > 0 ? 'Tout désélectionner' : 'Tout sélectionner'}
        </button>
      </div>
      
      <div className="meta-metrics-grid">
        {availableMetrics.map((metric) => {
          const isSelected = selectedMetrics.some(m => m.value === metric.value);
          return (
            <div key={metric.value} className="meta-metric-item">
              <input
                type="checkbox"
                id={`meta-${metric.value}`}
                className="meta-metric-checkbox"
                checked={isSelected}
                onChange={() => handleMetricToggle(metric)}
              />
              <label 
                htmlFor={`meta-${metric.value}`}
                className="meta-metric-label"
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