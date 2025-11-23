import { useState, useEffect } from 'react';
import { agenticAPI } from '../services/api';
//import logo from './BCID_H_rgb_pos.png';
import logo from './ago_downloaded.png';

export function Header() {
  const [isConnected, setIsConnected] = useState(false);
  const [statusText, setStatusText] = useState('Checking connection...');

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await agenticAPI.healthCheck();
      setIsConnected(true);
      setStatusText(`Connected: ${response.service}`);
    } catch (error) {
      setIsConnected(false);
      setStatusText('Disconnected - Please start the backend server');
    }
  };

  return (
    <header className="bc-header">
      <div className="header-content">
        <img src={logo} alt="BC Government Logo" className="header-logo" />
        <div className="header-text">
          <h1>Agentic AI Assessment</h1>
          {/* <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span>{statusText}</span>
          </div> */}
        </div>
      </div>
    </header>
  );
}
