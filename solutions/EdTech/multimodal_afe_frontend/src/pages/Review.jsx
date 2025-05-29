import React, { useState, useEffect } from "react";
import {
  ThumbsUp,
  ThumbsDown,
  Download,
  Search,
  ChevronLeft,
  ChevronRight,
  Loader,
  XCircle,
  CheckCircle,
} from "lucide-react";
import "../styles/Review.css";
import Footer from "../components/Footer";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import axios from "axios";
import { jsPDF } from "jspdf";
import "jspdf-autotable";
import html2canvas from "html2canvas";
import { marked } from "marked";

const Review = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [courseId, setCourseId] = useState("");
  const [courseIdSuggestions, setCourseIdSuggestions] = useState([]);
  const [isCourseIdValid, setIsCourseIdValid] = useState(true);
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalEvaluations, setTotalEvaluations] = useState(0);
  const [itemsPerPage] = useState(10);
  // const apiUrl = window?.env?.REACT_APP_API_URL || "https://da.wilp-connect.net";
  const apiUrl = "http://localhost:8009";

  // Fetch course IDs on component mount
  useEffect(() => {
    fetchCourseIds();
  }, []);

  // Fetch evaluations when page changes or search term changes with a delay
  useEffect(() => {
    if (courseId && isCourseIdValid) {
      // Add a small delay to avoid too many requests while typing
      const delaySearch = setTimeout(() => {
        fetchEvaluations();
      }, 300);
      
      return () => clearTimeout(delaySearch);
    }
  }, [page, searchTerm, courseId]);

  // Function to fetch course ID suggestions
  const fetchCourseIds = async (searchText = '') => {
    try {
      const response = await axios.get(`${apiUrl}/afe/fetch-courseids`, {
        params: { search_text: searchText },
      });
      setCourseIdSuggestions(response.data.course_ids);
    } catch (err) {
      console.error('Error fetching Course IDs:', err);
    }
  };

  // Handle course ID input change
  const handleCourseIdChange = (e) => {
    const value = e.target.value;
    setCourseId(value);
    fetchCourseIds(value);
  };

  // Validate course ID when focus is lost
  const handleCourseIdBlur = () => {
    if (courseId && !courseIdSuggestions.includes(courseId)) {
      setIsCourseIdValid(false);
      setCourseId("");
      setEvaluations([]);
    } else {
      setIsCourseIdValid(true);
    }
  };

  // Fetch evaluations for selected course with pagination
  const fetchEvaluations = async () => {
    if (!courseId || !isCourseIdValid) return;

    setLoading(true);
    try {
      const response = await axios.get(`${apiUrl}/afe/api/get_paginated_evaluations`, {
        params: { 
          course_id: courseId,
          page: page,
          items_per_page: itemsPerPage,
          search: searchTerm.trim() // Send search term to backend
        },
      });
      
      setEvaluations(response.data.evaluations);
      setTotalPages(response.data.pagination.total_pages);
      setTotalEvaluations(response.data.pagination.total);
    } catch (error) {
      console.error("Error fetching evaluations:", error);
      alert("Failed to fetch evaluations");
    } finally {
      setLoading(false);
    }
  };

  // When a new course is selected, reset to page 1
  const handleFetchClick = () => {
    setPage(1);
    fetchEvaluations();
  };

  const downloadPDF = async (evaluation) => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 14;
    const maxWidth = pageWidth - (margin * 2);

    const greyTextColor = [50, 50, 50];
    const goldenYellowColor = [255, 204, 0];

    // Helper function to add text with automatic page breaks
    const addTextWithPageBreaks = (text, x, y, options = {}) => {
        const fontSize = options.fontSize || 11;
        const lineHeight = options.lineHeight || fontSize * 0.4;
        const maxLineWidth = options.maxWidth || maxWidth;
        
        doc.setFontSize(fontSize);
        const lines = doc.splitTextToSize(text, maxLineWidth);
        
        let currentY = y;
        
        for (let i = 0; i < lines.length; i++) {
            // Check if we need a new page (leave space for footer)
            if (currentY + lineHeight > pageHeight - 20) {
                doc.addPage();
                currentY = margin;
            }
            
            doc.text(lines[i], x, currentY);
            currentY += lineHeight;
        }
        
        return currentY;
    };

    // Title
    doc.setFontSize(24);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...greyTextColor);
    doc.text("Slide Evaluation Report", margin, 20);

    // Current Date
    const currentDate = new Date().toLocaleDateString();
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100);
    doc.text(`Date: ${currentDate}`, pageWidth - 20, 30, { align: 'right' });

    // Horizontal Line
    doc.setDrawColor(200);
    doc.line(10, 35, pageWidth - 10, 35);

    // Course and Lecture Info
    doc.setFontSize(16);
    doc.setTextColor(0);
    doc.text(`Course ID: ${courseId}`, margin, 50);
    doc.text(`Lecture ${evaluation.lecture_no}`, pageWidth - 20, 50, { align: 'right' });

    // Calculate normalized score - FIXED: Don't divide again, backend already provides averaged score
    const normalizedScore = evaluation.total_score ? evaluation.total_score.toFixed(2) : "N/A";
    doc.text(`Total Score: ${normalizedScore}/5`, margin, 65);

    // Criteria Evaluations Summary Table
    if (evaluation.criteria_scores) {
        const tableData = evaluation.criteria_scores.map((score) => {
            // Process feedback using marked
            const feedbackMarkdown = score.feedback || "No evaluation provided.";
            const feedbackHtml = marked(feedbackMarkdown);
            const feedbackText = feedbackHtml.replace(/<[^>]+>/g, ''); // Remove HTML tags

            // Truncate feedback for table view
            const truncatedFeedback = feedbackText.length > 200 ? 
                feedbackText.substring(0, 200) + "..." : feedbackText;

            const timeRange = score.time_range || "";
            return [score.criterion, timeRange, truncatedFeedback, score.score];
        });

        doc.setFontSize(14);
        doc.setTextColor(...greyTextColor);
        doc.text("Section Evaluations", margin, 80);

        doc.autoTable({
            startY: 85,
            head: [['Criterion', 'Time Range', 'Evaluation', 'Score']],
            body: tableData,
            theme: 'grid',
            styles: { 
                fontSize: 9, 
                cellPadding: 3, 
                halign: 'left',
                overflow: 'linebreak',
                cellWidth: 'wrap'
            },
            headStyles: { fillColor: [100, 100, 100], textColor: 255, fontStyle: 'bold' },
            bodyStyles: { fillColor: [245, 245, 245], textColor: 50 },
            alternateRowStyles: { fillColor: [255, 255, 255] },
            columnStyles: {
                0: { cellWidth: 25, halign: 'left' },
                1: { cellWidth: 30, halign: 'left' },
                2: { cellWidth: 100, halign: 'left', overflow: 'linebreak' },
                3: { cellWidth: 20, halign: 'center' }
            },
            margin: { left: margin, right: margin }
        });

        // Add detailed criteria content on separate pages
        evaluation.criteria_scores.forEach((score, index) => {
            const slideImages = score.slide_images || {};
            const slideNumbers = score.slide_numbers || [];
            
            // Add new page for each criterion detail
            doc.addPage();
            
            // Criterion header
            doc.setFontSize(18);
            doc.setFont("helvetica", "bold");
            doc.setTextColor(...goldenYellowColor);
            doc.text(score.criterion, margin, 20);
            
            // Time range and score
            doc.setFontSize(12);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(100);
            doc.text(`Time: ${score.time_range || ""}`, pageWidth - 20, 20, { align: 'right' });
            doc.text(`Score: ${score.score}/5`, pageWidth - 20, 30, { align: 'right' });
            
            // Horizontal divider
            doc.setDrawColor(200);
            doc.line(10, 35, pageWidth - 10, 35);
            
            // Positioning variables to track where to add content
            let yPosition = 45;
            
            // Add slide images if available
            if (slideNumbers.length > 0 && Object.keys(slideImages).length > 0) {
                // Add image heading
                doc.setFontSize(14);
                doc.setFont("helvetica", "bold");
                doc.setTextColor(...greyTextColor);
                doc.text("Slide Images:", margin, yPosition);
                yPosition += 10;
                
                // Calculate how many slides to show per row (max 2)
                const slidesPerRow = 2;
                const imgWidth = (pageWidth - 40) / slidesPerRow;
                const imgHeight = 70;
                
                // Group slides into rows
                for (let i = 0; i < slideNumbers.length; i += slidesPerRow) {
                    const rowSlides = slideNumbers.slice(i, i + slidesPerRow);
                    
                    // Check if we need a new page
                    if (yPosition + imgHeight + 20 > pageHeight - 30) {
                        doc.addPage();
                        yPosition = 20;
                    }
                    
                    // Add each slide in this row
                    rowSlides.forEach((slideNum, idx) => {
                        if (slideImages[slideNum]) {
                            try {
                                // Add slide number
                                doc.setFontSize(10);
                                doc.setFont("helvetica", "normal");
                                doc.text(`Slide ${slideNum}`, 20 + (idx * imgWidth), yPosition);
                                
                                // Add the image
                                const imgData = `data:image/jpeg;base64,${slideImages[slideNum]}`;
                                doc.addImage(imgData, 'JPEG', 20 + (idx * imgWidth), yPosition + 5, imgWidth - 10, imgHeight);
                            } catch (error) {
                                console.error(`Error adding slide ${slideNum} image to PDF:`, error);
                            }
                        }
                    });
                    
                    // Update position for next row
                    yPosition += imgHeight + 15;
                }
                
                // Add divider
                doc.setDrawColor(220);
                doc.line(10, yPosition - 5, pageWidth - 10, yPosition - 5);
                yPosition += 10;
            }
            
            // Evaluation section with proper text wrapping and page breaks
            // Check if we need a new page
            if (yPosition + 30 > pageHeight - 30) {
                doc.addPage();
                yPosition = 20;
            }
            
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.setTextColor(...greyTextColor);
            doc.text("Evaluation:", margin, yPosition);
            yPosition += 15;
            
            doc.setFontSize(11);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(50);
            
            // Process feedback with proper text handling
            const feedbackMarkdown = score.feedback || "No evaluation provided.";
            const feedbackHtml = marked(feedbackMarkdown);
            const feedbackText = feedbackHtml.replace(/<[^>]+>/g, ''); // Remove HTML tags
            
            // Add text with automatic page breaks
            yPosition = addTextWithPageBreaks(feedbackText, margin, yPosition, {
                fontSize: 11,
                lineHeight: 5,
                maxWidth: maxWidth
            });
        });
    }

    // Page footer with page numbers
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(14);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(...goldenYellowColor);
        doc.text("[", pageWidth - 37, 10);
        doc.text(".", pageWidth - 18, 10);
        doc.text("]", pageWidth - 11, 10);
        doc.setTextColor(...greyTextColor);
        doc.text("Spanda AI", pageWidth - 35, 10);
        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
    }

    // Save the PDF
    doc.save(`Evaluation_Report_${courseId}_Lecture_${evaluation.lecture_no}.pdf`);
  };

  // Function to handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    // Reset to page 1 when searching
    setPage(1);
  };

  return (
    <>
      <Header onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)} tag="Evaluation Review" />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <div className="table-container">
        <div className="table-header">
          <h2 className="header-title">Evaluation Review</h2>
          <div className="course-selection">
            <div className="form-group">
              <input
                type="text"
                value={courseId}
                onChange={handleCourseIdChange}
                onBlur={handleCourseIdBlur}
                className={`input-field ${!isCourseIdValid ? 'invalid-input' : ''}`}
                list="course-id-suggestions"
                placeholder="Search and select a Course ID"
              />
              <datalist id="course-id-suggestions">
                {courseIdSuggestions.map((id) => (
                  <option key={id} value={id} />
                ))}
              </datalist>
            </div>
            <button 
              className="fetch-button"
              onClick={handleFetchClick}
              disabled={!isCourseIdValid || loading}
            >
              {loading ? <Loader size={16} className="spinner" /> : "Fetch"}
            </button>
          </div>
          <div className="search-container">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search by Lecture Number..."
              value={searchTerm}
              onChange={handleSearch}
            />
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Lecture Number</th>
                <th>Total Score</th>
                <th>Feedback</th>
                <th>Report</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.map((evaluation) => {
                // FIXED: Don't divide again, backend already provides averaged score
                const normalizedScore = evaluation.total_score ? evaluation.total_score.toFixed(2) : "N/A";

                return (
                  <tr key={evaluation.lecture_no}>
                    <td>{evaluation.lecture_no}</td>
                    <td>{normalizedScore}/5</td>
                    <td>
                      <textarea
                        className="feedback-input"
                        value=""
                        readOnly
                      />
                    </td>
                    <td>
                      <button 
                        className="download-btn"
                        onClick={() => downloadPDF(evaluation)}
                      >
                        <Download size={16} /> Download
                      </button>
                    </td>
                  </tr>
                );
              })}
              {evaluations.length === 0 && !loading && (
                <tr>
                  <td colSpan="4" className="no-data-message">
                    No evaluations found
                  </td>
                </tr>
              )}
              {loading && (
                <tr>
                  <td colSpan="4" className="loading-message">
                    <Loader size={24} className="spinner" /> Loading...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="pagination-container">
          <button 
            className="pagination-btn" 
            disabled={page === 1 || loading} 
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <span className="page-number">
            Page {page} of {totalPages} ({totalEvaluations} total)
          </span>
          <button 
            className="pagination-btn" 
            disabled={page === totalPages || loading} 
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default Review;