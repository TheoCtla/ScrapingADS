import React from 'react';
import './ReportHeader.css';

interface ReportHeaderProps {
  customerCount: number;
}

export default function ReportHeader({ customerCount }: ReportHeaderProps) {
  return (
    <div>
      <h1>SCRAPING <span style={{ color: '#dbbc32' }}>ADS</span></h1>
    </div>
  );
} 