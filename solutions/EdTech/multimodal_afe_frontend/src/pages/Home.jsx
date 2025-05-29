import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faVideo, 
  faUsers, 
  faStar, 
  faBookOpen, 
  faArrowRight 
} from '@fortawesome/free-solid-svg-icons';
import '../styles/Home.css';
import Footer from '../components/Footer';
function Home() {

const navigate = useNavigate();

  const handleGetstarted = () => {
    navigate('/evaluation_page');
  };

    return (
        <div className="landing-container">
          {/* Hero Section */}
          <header className="hero">
            <nav className="navbar">
              <div className="logo">InstructorEval</div>
              <div className="nav-links">
                <button className="nav-button">Features</button>
                <button className="nav-button">About</button>
                <button className="nav-button">Contact</button>
                <button className="cta-button">Sign In</button>
              </div>
            </nav>
            
            <div className="hero-content">
              <div className="hero-text">
                <h1>Evaluate Instructors with Confidence</h1>
                <p>
                  Comprehensive analytics and insights for video tutorials and student engagement. 
                  Make data-driven decisions to improve educational content.
                </p>
                <button className="cta-button" onClick={handleGetstarted}>
                Start Evaluating <FontAwesomeIcon icon={faArrowRight} className="arrow-icon" />
                </button>
              </div>
              <div className="feature-grid-container">
                <div className="feature-grid">
                  <div className="feature-card">
                    <FontAwesomeIcon icon={faVideo} className="feature-icon" />
                    <h3>Video Analysis</h3>
                    <p>Deep insights into content quality and delivery</p>
                  </div>
                  <div className="feature-card">
                    <FontAwesomeIcon icon={faUsers} className="feature-icon" />
                    <h3>Engagement Metrics</h3>
                    <p>Track student interaction and participation</p>
                  </div>
                  <div className="feature-card">
                    <FontAwesomeIcon icon={faStar} className="feature-icon" />
                    <h3>Performance Rating</h3>
                    <p>Comprehensive instructor scoring system</p>
                  </div>
                  <div className="feature-card">
                    <FontAwesomeIcon icon={faBookOpen} className="feature-icon" />
                    <h3>Learning Analytics</h3>
                    <p>Measure educational effectiveness</p>
                  </div>
                </div>
              </div>
            </div>
          </header>
    
          {/* Features Section */}
          <section className="features-section">
            <h2>Why Choose InstructorEval?</h2>
            <div className="features-grid">
              <div className="feature-box">
                <div className="icon-container">
                  <FontAwesomeIcon icon={faVideo} className="icon" />
                </div>
                <h3>Video Content Analysis</h3>
                <p>
                  Advanced algorithms analyze teaching style, content clarity, and presentation quality
                  to provide actionable insights.
                </p>
              </div>
              <div className="feature-box">
                <div className="icon-container">
                  <FontAwesomeIcon icon={faUsers} className="icon" />
                </div>
                <h3>Student Engagement Tracking</h3>
                <p>
                  Monitor student participation, questions asked, and interaction patterns
                  to measure teaching effectiveness.
                </p>
              </div>
              <div className="feature-box">
                <div className="icon-container">
                  <FontAwesomeIcon icon={faStar} className="icon" />
                </div>
                <h3>Performance Metrics</h3>
                <p>
                  Comprehensive scoring system based on multiple factors to provide
                  fair and accurate instructor evaluations.
                </p>
              </div>
            </div>
          </section>
    
          {/* CTA Section */}
          <section className="cta-section">
            <h2>Ready to Transform Your Educational Assessment?</h2>
            <p>
              Join thousands of educational institutions using InstructorEval to improve
              their teaching quality and student outcomes.
            </p>
            <button className="cta-button">Get Started Now</button>
          </section>
          <Footer></Footer>
        </div>
    );
}

export default Home
