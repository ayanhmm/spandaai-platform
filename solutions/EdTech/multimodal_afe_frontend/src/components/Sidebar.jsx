import { Link, useLocation } from 'react-router-dom';
import '../styles/Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <div 
        className={`sidebar-overlay ${isOpen ? 'active' : ''}`}
        onClick={onClose}
      />
      
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <span className="sidebar-title">Menu</span>
          <button className="close-btn" onClick={onClose}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <nav className="sidebar-nav">
          {/* Evaluation Page Link */}
          <Link 
            to="/evaluation_page" 
            className={`nav-item ${isActive('/evaluation_page') ? 'active' : ''}`}
            onClick={onClose}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            Evaluation Page
          </Link>

          {/* Review Page Link */}
          <Link 
            to="/review_page" 
            className={`nav-item ${isActive('/review_page') ? 'active' : ''}`}
            onClick={onClose}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Review Page
          </Link>

          {/* Upload Lectures Page Link */}
          <Link 
            to="/upload_lectures" 
            className={`nav-item ${isActive('/upload_lectures') ? 'active' : ''}`}
            onClick={onClose}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            Upload Lectures
          </Link>
        </nav>

        <div className="sidebar-footer">
          <p>Version 1.0.0</p>
          <p>© 2025 Spanda AI</p>
        </div>
      </div>
    </>
  );
};

export default Sidebar;