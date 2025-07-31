import React, { useState } from 'react';
import './MetricsSelector.css';

interface Metric {
  label: string;
  value: string;
}

interface MetricsSelectorProps {
  availableMetrics: Metric[];
  selectedMetrics: Metric[];
  onMetricsChange: (metrics: Metric[]) => void;
}

export default function MetricsSelector({ 
  availableMetrics, 
  selectedMetrics, 
  onMetricsChange 
}: MetricsSelectorProps) {
  const [selectAllActive, setSelectAllActive] = useState(false);
  
  const handleSelectAll = () => {
    const anySelected = selectedMetrics.length > 0;
    setSelectAllActive(!anySelected);
    onMetricsChange(anySelected ? [] : [...availableMetrics]);
  };



  const handleMetricToggle = (metric: Metric) => {
    onMetricsChange(
      selectedMetrics.some(m => m.value === metric.value)
        ? selectedMetrics.filter(m => m.value !== metric.value)
        : [...selectedMetrics, metric]
    );
  };

  const metricsByChannel = {
    "Performance Max": availableMetrics.filter(metric =>
      metric.value.includes('perfmax')
    ),
    "Search": availableMetrics.filter(metric =>
      metric.value.includes('search')
    ),
    "Display": availableMetrics.filter(metric =>
      metric.value.includes('display')
    ),
    "Métriques globales": availableMetrics.filter(metric =>
      !metric.value.includes('perfmax') &&
      !metric.value.includes('search') &&
      !metric.value.includes('display')
    ),
  };

  return (
    <div className="metrics-selector-container">
      <h4 className="metrics-title">Métriques Google Ads</h4>
      <label className="metrics-description">Choisissez les données à inclure :</label>
      
      <button 
        className={`select-all-button ${selectAllActive ? 'selected' : ''}`}
        onClick={handleSelectAll}
      >
        {selectedMetrics.length > 0 ? 'Tout désélectionner' : 'Tout sélectionner'}
      </button>

      <div className="metrics-channels">
        {Object.entries(metricsByChannel).map(([channelLabel, metrics]) => (
          <div key={channelLabel} className="channel-group">
            <h3 className="channel-title">{channelLabel}</h3>
            <div className="metrics-grid">
              {metrics.map((metric) => (
                <div key={metric.value} className="metric-item">
                  <input
                    type="checkbox"
                    id={`metric-${metric.value}`}
                    className="metric-checkbox"
                    checked={selectedMetrics.some(m => m.value === metric.value)}
                    onChange={() => handleMetricToggle(metric)}
                  />
                  <label htmlFor={`metric-${metric.value}`} className="metric-label">
                    {metric.label}
                  </label>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 