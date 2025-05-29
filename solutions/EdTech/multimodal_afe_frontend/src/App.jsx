import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Evaluation from "./pages/Evaluation";
import Review from "./pages/Review";
import UploadLectures from "./pages/UploadLectures"; // Import the new page

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/evaluation_page" element={<Evaluation />} />
      <Route path="/review_page" element={<Review />} />
      <Route path="/upload_lectures" element={<UploadLectures />} /> {/* New route */}
    </Routes>
  );
}

export default App;
