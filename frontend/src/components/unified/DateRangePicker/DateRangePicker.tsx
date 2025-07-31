import React from 'react';
import './DateRangePicker.css';

interface DateRangePickerProps {
  startDate: string;
  endDate: string;
  sheetMonth: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onSheetMonthChange: (month: string) => void;
}

export default function DateRangePicker({
  startDate,
  endDate,
  sheetMonth,
  onStartDateChange,
  onEndDateChange,
  onSheetMonthChange
}: DateRangePickerProps) {
  return (
    <div className="date-container">
      <div className="date-group">
        <label className="date-label" htmlFor="start_date">Start Date :</label>
        <input
          type="date"
          id="start_date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
        />
      </div>
      <div className="date-group">
        <label className="date-label" htmlFor="end_date">End Date :</label>
        <input
          type="date"
          id="end_date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
        />
      </div>
      <div className="date-group">
        <label className="date-label" htmlFor="sheet_month">Mois pour le Sheet :</label>
        <input
          type="text"
          id="sheet_month"
          value={sheetMonth}
          onChange={(e) => onSheetMonthChange(e.target.value)}
          placeholder="Ex: juillet 2025 ..."
        />
      </div>
    </div>
  );
} 