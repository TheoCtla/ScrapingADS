import React from 'react';
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
  
  const handleSelectAll = () => {
    const anySelected = selectedMetrics.length > 0;
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
    <div style={{ margin: '15px 0' }}>
      <h4 style={{ margin: '0 0 15px 0', color: '#4285f4' }}>📊 Métriques Google Ads</h4>
      <label style={{ display: 'block', marginBottom: '10px' }}>Choisissez les données à inclure :</label>
      <div style={{ marginBottom: '15px' }}>
        <button 
          onClick={handleSelectAll}
          style={{ marginRight: '10px', padding: '5px 10px' }}
        >
          {selectedMetrics.length > 0 ? 'Tout désélectionner' : 'Tout sélectionner'}
        </button>
      </div>

      {Object.entries(metricsByChannel).map(([channelLabel, metrics]) => (
        <div key={channelLabel}>
          <h3>{channelLabel}</h3>
          <div>
            {metrics.map((metric) => (
              <div key={metric.value}>
                <input
                  type="checkbox"
                  id={`metric-${metric.value}`}
                  checked={selectedMetrics.some(m => m.value === metric.value)}
                  onChange={() => handleMetricToggle(metric)}
                />
                <label htmlFor={`metric-${metric.value}`}>
                  {metric.label}
                </label>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
} 