import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './components/HomePage/HomePage';
import ScrapingRapports from './components/ScrapingRapports/ScrapingRapports';
import ExportDrive from './components/ExportDrive/ExportDrive';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scraping-rapports" element={<ScrapingRapports />} />
        <Route path="/export-drive" element={<ExportDrive />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
