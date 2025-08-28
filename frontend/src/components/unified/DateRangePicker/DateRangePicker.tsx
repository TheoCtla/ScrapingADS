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
  
  // Fonction pour obtenir le mois précédent en français
  const getPreviousMonthInFrench = () => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    
    // Mois précédent
    const lastMonth = currentMonth === 0 ? 11 : currentMonth - 1;
    
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    
    return monthNames[lastMonth];
  };
  
  // Fonction pour convertir le mois français en anglais avec majuscule
  const convertMonthToEnglish = (input: string): string => {
    const frenchToEnglishMonths: { [key: string]: string } = {
      'janvier': 'January',
      'février': 'February',
      'mars': 'March',
      'avril': 'April',
      'mai': 'May',
      'juin': 'June',
      'juillet': 'July',
      'août': 'August',
      'septembre': 'September',
      'octobre': 'October',
      'novembre': 'November',
      'décembre': 'December'
    };

    let converted = input;
    const currentYear = new Date().getFullYear();
    
    // Chercher et remplacer chaque mois français
    for (const [french, english] of Object.entries(frenchToEnglishMonths)) {
      const regex = new RegExp(french, 'gi'); // 'gi' pour ignorer la casse
      if (regex.test(converted)) {
        // Si on trouve un mois français, le remplacer par le mois anglais + année
        converted = converted.replace(regex, english + ' ' + currentYear);
        break; // Sortir de la boucle après avoir trouvé et remplacé
      }
    }
    
    return converted;
  };

  const handleSheetMonthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    const convertedValue = convertMonthToEnglish(inputValue);
    onSheetMonthChange(convertedValue);
  };

  return (
    <div className="date-container">
      <div className="date-group">
        <label className="date-label" htmlFor="start_date">Date de début :</label>
        <input
          type="date"
          id="start_date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
        />
      </div>
      <div className="date-group">
        <label className="date-label" htmlFor="end_date">Date de fin :</label>
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
          onChange={handleSheetMonthChange}
          placeholder={`Ex: ${getPreviousMonthInFrench()} ${new Date().getFullYear()} ...`}
        />
      </div>
    </div>
  );
} 