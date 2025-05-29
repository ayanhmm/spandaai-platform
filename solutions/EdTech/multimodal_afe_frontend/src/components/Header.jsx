import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from 'react-router-dom';

import { FaSignOutAlt, FaUserShield } from 'react-icons/fa';
import '../styles/Header.css'
const Header = ({ onMenuClick ,tag }) => {
  const [isOpen, setIsOpen] = useState(false);

  const navigate = useNavigate(); // Get the navigate function
  const menuRef = useRef();

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
    console.log("Dropdown toggled:", !isOpen); 
  };

  const closeDropdown = (e) => {
    if (menuRef.current && !menuRef.current.contains(e.target)) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("click", closeDropdown);
    return () => {
      document.removeEventListener("click", closeDropdown);
    };
  }, []);

  const handleAssignRoleClick = () => {
    navigate('/'); // Navigate to the /assign-role route
  };


  return (
    <header className="app-header">
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
        <div className="brand">
          <span className="brand-text">Spanda AI</span>
          <span className="brand-subtitle">{tag}</span>
        </div>
      </div>

      <div className="header-right">
        <div className="user-info">
          <span className="user-name">Welcome, User</span>
        </div>
        {/* <div className="profile-container" ref={menuRef}>
          <div className="profile-logo" onClick={toggleDropdown}>
            <img  alt="Profile" className="profile-img" />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className={`dropdown-arrow ${isOpen ? "open" : ""}`}
            >
              <path d="M6 9l6 6 6-6"></path>
            </svg>
          </div>
          {isOpen && (
            <div className="dropdown-menu">
                     <button className="dropdown-btn">
                Logout<FaSignOutAlt className="icon" />
              </button>
              <button className="dropdown-btn" onClick={handleAssignRoleClick}>
                Assign Roles <FaUserShield className="icon" />
              </button>
            </div>
          )}
        </div> */}
      </div>
    </header>
  );
};

export default Header;
