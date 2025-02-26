import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import Footer from './components/common/Footer';
import HomePage from './pages/HomePage';
import QuestionBank from './pages/QuestionBank';
import QuestionPaper from './pages/QuestionPaper';
import './styles/App.css';
import './styles/questionPaper.css';  // Add this new import

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="app-container">
        <Header onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)} />
        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        
        <div className="main-wrapper">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/question-bank" element={<QuestionBank />} />
            <Route path="/question-paper" element={<QuestionPaper />} />
          </Routes>
        </div>

        <Footer />
      </div>
    </Router>
  );
}

export default App;