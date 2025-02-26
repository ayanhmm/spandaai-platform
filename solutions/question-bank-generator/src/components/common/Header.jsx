import React from 'react';
import { useLocation } from 'react-router-dom';

const Header = ({ onMenuClick }) => {
  const location = useLocation();

  // Map the current route to the corresponding page title
  const pageTitles = {
    '/': 'Dashboard',
    '/question-bank': 'Question Bank Generator',
    '/question-paper': 'Question Paper Creator',
  };

  const pageTitle = pageTitles[location.pathname] || 'Spanda AI';

  return (
    <header className="app-header">
      {/* Left: Sidebar Button and Branding */}
      <div className="header-left">
        <button className="menu-btn" onClick={onMenuClick} aria-label="Menu">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <h2>
          <span className="highlight">[</span>
          <span className="text-white">Spanda</span>
          <span className="highlight">.</span>
          <span className="text-white">AI</span>
          <span className="highlight">]</span>
        </h2>
      </div>

      {/* Center: Page Title */}
      <div className="header-center">
        <h3 className="page-title">{pageTitle}</h3>
      </div>

      {/* Right: User Info and Logout */}
      <div className="header-right">
        <div className="user-info">
          <span className="user-name">Welcome, User</span>
        </div>
        <button className="logout-btn">
          <span>Logout</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </header>
  );
};

export default Header;
