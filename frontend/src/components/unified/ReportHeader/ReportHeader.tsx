import React from 'react';
import './ReportHeader.css';

interface ReportHeaderProps {
  customerCount: number;
}

export default function ReportHeader({ customerCount }: ReportHeaderProps) {
  return (
    <div>
      <h1>SCRAPING ADS</h1>
    </div>
  );
} 