import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div className="home-container">
        <h1 className="home-title">Apps Tarmaac</h1>
        <p className="home-subtitle">Choisissez votre action</p>
        
        <div className="home-buttons">
          <button 
            className="home-btn home-btn-primary"
            onClick={() => navigate('/scraping-rapports')}
          >
            <span className="btn-text">Scraping Rapports</span>
            <span className="btn-description">Export vers Google Sheets</span>
          </button>
          
          <button 
            className="home-btn home-btn-secondary"
            onClick={() => navigate('/export-drive')}
          >
            <span className="btn-text">Campagne CSV</span>
            <span className="btn-description">Export vers Google Drive</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
