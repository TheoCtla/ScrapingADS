import React from 'react';
import './ReportHeader.css';

interface ReportHeaderProps {
  customerCount: number;
}

export default function ReportHeader({ customerCount }: ReportHeaderProps) {
  return (
    <div>
      <h1>Google Ads Report</h1>
      <p>{customerCount} client(s) chargé(s)</p>
    </div>
  );
} 