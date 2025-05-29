import React, { useState,useRef,useEffect } from "react";
import * as pdfjs from 'pdfjs-dist';
import 'pdfjs-dist/build/pdf.worker.mjs';
import mammoth from "mammoth";
import "../styles/Evaluation.css";
import "../styles/Modal.css";
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import axios from 'axios';
import { faUpload } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import html2canvas from 'html2canvas';
import { faBrain, faChartLine, faStar, faLightbulb,faBolt,faAddressCard,faPhone,faTasks,faLock } from '@fortawesome/free-solid-svg-icons';
import { useDropzone } from 'react-dropzone';
import { CircularProgress, Typography, Box, IconButton, Button } from '@mui/material'; // Consolidated imports here
import DeleteIcon from '@mui/icons-material/Delete';
import { styled, width } from '@mui/system'; // Import styled from @mui/system
import Header from "../components/Header";
import Footer from "../components/Footer";
import Sidebar from '../components/Sidebar';
import { faFacebook, faTwitter, faLinkedin, faInstagram } from '@fortawesome/free-brands-svg-icons'; // Import social media icons

import Modal from "../components/Modal";
import { marked } from 'marked';
import {url} from '../utils/url';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.mjs',
  import.meta.url
).toString();
const iconList = [faBrain, faChartLine, faStar, faLightbulb,faBolt];

const Evaluation = () => {
  const [file, setFile] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [showEvaluateButton, setShowEvaluateButton] = useState(false); // New state
  const [responseData, setResponseData] = useState(null);
  const [pdfContent, setPdfContent] = useState("");
  const [preAnalysisData, setPreAnalysisData] = useState(null);
  const [response, setResponse] = useState("");
  const [isEditable, setIsEditable] = useState(true);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isPreanalyzing, setIsPreanalyzing] = useState(false);
  const [selectedText, setSelectedText] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [responseloading, setResponseloading] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [userData, setUserData] = useState("");
  const [files, setFiles] = useState([]);
  const [progress, setProgress] = useState({});
  const [courseId, setCourseId] = useState("");
  const [instructorName, setInstructorName] = useState("");
  const [yearSemester, setYearSemester] = useState("");
  const [lectureNo, setLectureNo] = useState("");
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [courseIdSuggestions, setCourseIdSuggestions] = useState([]);
  const [isCourseIdValid, setIsCourseIdValid] = useState(true);
  const [availableLectures, setAvailableLectures] = useState([]);
  const [criteriaEvaluations, setCriteriaEvaluations] = useState({});
  //const sidebarRef = useRef(null); 
  const [analyzing, setAnalyzing] = useState(false);
  const [queueStatus, setQueueStatus] = useState({ queue: false, position: 0 });
  const [fileUrls, setFileUrls] = useState({});
  const [streamingActive, setStreamingActive] = useState(false);
  // const apiUrl = window.ENV?.VITE_API_BASE_URL || "https://da.wilp-connect.net";
  const apiUrl = "http://localhost:8009";
  const [startLecture, setStartLecture] = useState("");
  const [endLecture, setEndLecture] = useState("");
  const [currentJobId, setCurrentJobId] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const MAX_RECONNECT_ATTEMPTS = 20;
  const RECONNECT_INTERVAL = 30000;
  const POLLING_INTERVAL = 30000;
  const TRANSCRIPTION_TIMEOUT = 60 * 60 * 1000;

  useEffect(() => {
    fetchCourseIds();
  }, []);

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

  const handleCourseIdChange = (e) => {
    const value = e.target.value;
    setCourseId(value);
    fetchCourseIds(value); // Fetch suggestions based on input
    setLectureNo(""); // Reset lecture number when course changes
  };

  const handleCourseIdBlur = () => {
    if (courseId && !courseIdSuggestions.includes(courseId)) {
      setIsCourseIdValid(false);
      setCourseId("");
      setAvailableLectures([]);
    } else {
      setIsCourseIdValid(true);
      // Fetch instructor name and available lectures if course ID is valid
      if (courseId) {
        fetchInstructorName(courseId);
        fetchAvailableLectures(courseId);
      }
    }
  };

  const fetchInstructorName = async (selectedCourseId) => {
    try {
      const response = await axios.get(`${apiUrl}/afe/get_instructor`, {
        params: { courseId: selectedCourseId },
      });
      if (response.data.instructor_name) {
        setInstructorName(response.data.instructor_name);
      }
    } catch (err) {
      console.error('Error fetching instructor name:', err);
    }
  };

  const fetchAvailableLectures = async (selectedCourseId) => {
    try {
      const response = await axios.get(`${apiUrl}/afe/get_existing_lectures`, {
        params: { courseId: selectedCourseId },
      });
      if (response.data) {
        // Convert to array if it's not already
        const lectures = Array.isArray(response.data) ? response.data : 
                        (response.data.length > 0 ? JSON.parse(response.data) : []);
        setAvailableLectures(lectures);
      } else {
        setAvailableLectures([]);
      }
    } catch (err) {
      console.error('Error fetching lectures:', err);
      setAvailableLectures([]);
    }
  };
  
  useEffect(() => {
    const newFileUrls = {};
    files.forEach(file => {
      if (!fileUrls[file.id]) {
        newFileUrls[file.id] = URL.createObjectURL(file.file);
      }
    });
    setFileUrls(prevUrls => ({ ...prevUrls, ...newFileUrls }));

    // Clean up URLs when component unmounts
    return () => {
      Object.values(newFileUrls).forEach(url => URL.revokeObjectURL(url));
    };
  }, [files]);

  const getSessionId = () => {
    return sessionStorage.getItem("sessionId");
  };
  
  const setSessionId = (id) => {
    sessionStorage.setItem("sessionId", id); // Save sessionId to sessionStorage
  };
  
  const initializeSessionId = () => {
    const existingSessionId = getSessionId();
    if (!existingSessionId) {
      const newSessionId = generateSessionId(); // Function to generate a unique sessionId
      setSessionId(newSessionId);
      return newSessionId;
    }
    return existingSessionId;
  };
  
  // Utility to generate sessionId (if needed)
  const generateSessionId = () => {
    return `session-${Math.random().toString(36).substr(2, 9)}-${Date.now()}`;
  };
  

  // Reset analyzing state once the response is loaded
  if (response && analyzing) {
    setAnalyzing(false);
  }


  const downloadPDF = async () => {
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

      // Total Score and Lecture Number
      doc.setFontSize(16);
      doc.setTextColor(0);
      const normalizedScore = response?.total_score
          ? parseFloat(response.total_score).toFixed(2)
          : 'N/A';

      doc.text(`Total Score: ${normalizedScore}/5`, margin, 50);
      
      if (response?.lecture_no) {
          doc.text(`Lecture ${response.lecture_no}`, pageWidth - 20, 50, { align: 'right' });
      }

      // Slide Group Evaluations
      if (response?.criteria_evaluations) {
          const tableData = Object.keys(response.criteria_evaluations).map((groupKey) => {
              const evaluation = response.criteria_evaluations[groupKey];

              // Process feedback using marked
              const feedbackMarkdown = evaluation?.feedback || "No evaluation provided.";
              const feedbackHtml = marked(feedbackMarkdown);
              const feedbackText = feedbackHtml.replace(/<[^>]+>/g, ''); // Remove HTML tags

              const score = evaluation?.score !== undefined ? evaluation.score : "No score available.";
              const timeRange = evaluation?.time_range || ""; 
              const slideNumbers = evaluation?.slide_numbers || [];

              // Truncate feedback for table view
              const truncatedFeedback = feedbackText.length > 200 ? 
                  feedbackText.substring(0, 200) + "..." : feedbackText;

              return [groupKey, timeRange, truncatedFeedback, score];
          });

          doc.setFontSize(14);
          doc.setTextColor(...greyTextColor);
          doc.text("Section Evaluations", margin, 65);

          doc.autoTable({
              startY: 70,
              head: [['Section', 'Time Range', 'Evaluation', 'Score']],
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
          
          // Add detailed slide group content on separate pages
          Object.keys(response.criteria_evaluations).forEach((groupKey, index) => {
              const evaluation = response.criteria_evaluations[groupKey];
              const slideImages = evaluation.slide_images || {};
              const slideNumbers = evaluation.slide_numbers || [];
              
              // Add new page for each slide group detail
              doc.addPage();
              
              // Group header
              doc.setFontSize(18);
              doc.setFont("helvetica", "bold");
              doc.setTextColor(...goldenYellowColor);
              doc.text(groupKey, margin, 20);
              
              // Time range and score
              doc.setFontSize(12);
              doc.setFont("helvetica", "normal");
              doc.setTextColor(100);
              doc.text(`Time: ${evaluation.time_range || ""}`, pageWidth - 20, 20, { align: 'right' });
              doc.text(`Score: ${evaluation.score}/5`, pageWidth - 20, 30, { align: 'right' });
              
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
              const feedbackMarkdown = evaluation.feedback || "No evaluation provided.";
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

      // 🔹 Capture Both Graphs and Add on the Same Page
      const chartElements = document.querySelectorAll('.chart-container');

      if (chartElements.length >= 2) {
          const radarChartCanvas = await html2canvas(chartElements[0]);
          const barChartCanvas = await html2canvas(chartElements[1]);

          const radarImg = radarChartCanvas.toDataURL('image/png');
          const barImg = barChartCanvas.toDataURL('image/png');

          // Add new page for graphs
          doc.addPage();
          doc.setFontSize(16);
          doc.text("Slide Scores Visualization", margin, 20);

          // Calculate available space for charts
          const chartWidth = pageWidth - (margin * 2);
          const chartHeight = 80;

          // Check if both charts fit on one page
          if (40 + chartHeight * 2 + 20 < pageHeight - 30) {
              // Both charts fit on one page
              doc.addImage(radarImg, 'PNG', margin, 30, chartWidth, chartHeight);
              doc.addImage(barImg, 'PNG', margin, 30 + chartHeight + 10, chartWidth, chartHeight);
          } else {
              // Split charts across pages
              doc.addImage(radarImg, 'PNG', margin, 30, chartWidth, chartHeight);
              doc.addPage();
              doc.setFontSize(16);
              doc.text("Slide Scores Visualization (continued)", margin, 20);
              doc.addImage(barImg, 'PNG', margin, 30, chartWidth, chartHeight);
          }
      }

      // Save the PDF
      doc.save("Slide_Evaluation_Report.pdf");
  };

  const handleClickOutside = (event) => {
    const openBtn = document.getElementById('open-btn');
    if (openBtn && !openBtn.contains(event.target)) {
      setIsSidebarOpen(false);
    }
  };

  useEffect(() => {
    // Add event listener for clicks outside the sidebar
    document.addEventListener('mousedown', handleClickOutside);
    
    // Cleanup listener on component unmount
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    initializeSessionId();

    connectToNotificationWebSocket();
  }, []);
  
  const handleTextSelection = () => {
    if (isEditable) {
      const selection = window.getSelection();
      const selectedText = selection.toString();
      const anchorNode = selection.anchorNode;
  
      const isInCriteriaBox = anchorNode && (anchorNode.nodeType === 3
        ? anchorNode.parentNode.closest('.criteria-box')
        : anchorNode.closest('.criteria-box'));
  
      if (isInCriteriaBox && selectedText) {
        setSelectedText(selectedText);
      }
    }
  };
  

  const handleInputChange = (e) => {
    setFeedback(e.target.value);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedText("");
    
  };

  const onDrop = (acceptedFiles) => {
    const updatedFiles = acceptedFiles.map(file => {
        if (file.type !== 'application/pdf') {
            // If the file is not a PDF, show an alert and skip adding it
            alert('Only PDF files are accepted');
            return null; // return null or skip the file
        }

        return {
            file,
            id: Math.random(),
            progress: 0
        };
    }).filter(file => file !== null); // Remove null values (non-PDF files)

    // Only update the state if there are valid PDF files
    if (updatedFiles.length > 0) {
        setFiles(prevFiles => [...prevFiles, ...updatedFiles]);

        updatedFiles.forEach(file => {
            handleUpload({ target: { files: [file.file] } }); // Trigger parsing and content extraction
            uploadFile(file);
        });
    }
};


const handleUpload = async (e) => {
  const selectedFile = e.target.files[0];

  if (!selectedFile) {
    alert("Please select a file.");
    return;
  }

  setFile(selectedFile);

  if (!videoFile) { 
    setShowEvaluateButton(true); // Show evaluate button only if no video is uploaded
  }
};

const handleVideoUpload = (e) => {
  const selectedVideo = e.target.files[0];

  if (selectedVideo) {
    const url = URL.createObjectURL(selectedVideo);
    setVideoFile(selectedVideo);
    setVideoUrl(url);
    setShowEvaluateButton(true); // Ensure evaluate button is shown when a video is uploaded
  }
};

const removeVideo = () => {
  setVideoFile(null);
  setVideoUrl(null);
  
  if (file) {
    setShowEvaluateButton(true);  // Show evaluate button if a transcript exists
  } else {
    setShowEvaluateButton(false); // Hide evaluate button if no transcript exists
  }
};


const extractTextAndImages = async (file) => {
  setIsExtracting(true);
  const formData = new FormData();
  formData.append("file", file);

  const apiHost = `${apiUrl}/afe/api/extract_text_from_file`;  

  try {
    const response = await fetch(apiHost, { 
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to extract text and images");
    }

    return await response.json();
  } catch (error) {
    console.error("An error occurred:", error);
    throw error;  
  } finally {
    setIsExtracting(false);
  }
};


const preAnalyzeText = async (extractedData) => {
  setIsPreanalyzing(true);
  const thesisText = extractedData?.text || "";

  const apiHost = `${apiUrl}/afe/api/pre_analyze`; // Append the endpoint path

  try {
    const response = await fetch(apiHost, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transcript: thesisText,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to pre-analyze text");
    }

    return await response.json();
  } catch (error) {
    console.error("An error occurred during pre-analysis:", error);
    throw error; // Re-throw if further handling is needed
  } finally {
    setIsPreanalyzing(false);
  }
};


const uploadFile = (file) => {
    const formData = new FormData();
    formData.append('file', file.file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload'); // Change to your upload URL

    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const progressValue = (event.loaded / event.total) * 100;
            setProgress(prevProgress => ({
                ...prevProgress,
                [file.id]: progressValue
            }));
        }
    };

    xhr.onload = () => {
        if (xhr.status === 200) {
            console.log('Upload successful!');
        }
    };

    xhr.send(formData);
};

const { getRootProps: getTranscriptRootProps, getInputProps: getTranscriptInputProps } = useDropzone({ 
  onDrop, 
  accept: { 'application/pdf': ['.pdf'] } // Restrict to PDFs only for transcripts
});

const { getRootProps: getVideoRootProps, getInputProps: getVideoInputProps } = useDropzone({
  onDrop: (acceptedFiles) => {
    const selectedVideo = acceptedFiles[0];
    if (selectedVideo) {
      const url = URL.createObjectURL(selectedVideo);
      setVideoFile(selectedVideo);
      setVideoUrl(url);
      setShowEvaluateButton(true);
    }
  },
  accept: { 'video/mp4': ['.mp4'], 'video/mkv': ['.mkv'], 'video/avi': ['.avi'] } // Accept only video files
});

const removeFile = (id) => {
  setFiles(files.filter(file => file.id !== id));

  if (!videoFile) {
    setShowEvaluateButton(false); // Hide evaluate button if no video or transcript exists
  }
};


const postDataToBackend = async (postData) => {
  try {
    const response = await fetch(`${apiUrl}/afe/api/postUserData`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(postData),
    });

    if (response.ok) {
      console.log("Evaluation stored successfully.");
    } else {
      console.error("Failed to store evaluation.");
    }
  } catch (error) {
    console.error("Error posting evaluation data:", error);
  }
};

const extractAndPostData = (result) => {
  if (!result.criteria_evaluations || Object.keys(result.criteria_evaluations).length === 0) {
    alert("Evaluation data is missing.");
    return;
  }

  // Combine all slide group evaluations into a single response text
  const fullResponseText = Object.entries(result.criteria_evaluations)
    .map(([groupKey, evaluation]) => {
      // Count how many slides have images in this group
      const slideImages = evaluation.slide_images || {};
      const slideNumbers = evaluation.slide_numbers || [];
      const imageCount = Object.keys(slideImages).length;
      
      // Create image reference text
      const hasImageText = imageCount > 0 
        ? `[Includes ${imageCount} slide image${imageCount > 1 ? 's' : ''}]` 
        : '[No slide images]';
      
      // Create slide numbers text
      const slidesText = slideNumbers.length > 0
        ? `Slides ${slideNumbers.join(', ')}`
        : groupKey;
      
      return `${groupKey} [${evaluation.time_range || ''}] ${hasImageText}:\n${evaluation.feedback}\nScore: ${evaluation.score}/5\n\nSection Content: ${evaluation.slide_content || ''}\n`;
    })
    .join("\n---\n\n"); // Separator between groups

  const postData = {
    course_id: courseId,
    lecture_no: result.lecture_no,
    response: fullResponseText,
    total_score: result.total_score,
    scores: Object.entries(result.criteria_evaluations).map(([groupKey, evaluation]) => ({
      criterion: groupKey, // Store group key as criterion for database compatibility
      score: evaluation.score,
      feedback: evaluation.feedback,
      slide_content: evaluation.slide_content,
      slide_images: evaluation.slide_images || {}, // Include actual slide images
      slide_numbers: evaluation.slide_numbers || [], // Include actual slide numbers
      time_range: evaluation.time_range || "" // Include time range
    }))
  };

  postDataToBackend(postData);
};


const connectToNotificationWebSocket = () => {
    const notificationUrl = `${apiUrl.replace("http", "ws")}/afe/api/ws/notifications`;
    const notificationWebSocket = new WebSocket(notificationUrl);
  
    notificationWebSocket.onopen = () => {
      console.log("Connected to notification WebSocket");
      const sessionId = getSessionId();
      if (sessionId) {
        notificationWebSocket.send(sessionId);
      } else {
        console.warn("No sessionId available to send. Skipping.");
      }
    };
  
    notificationWebSocket.onmessage = (event) => {
      const notification = JSON.parse(event.data);
  
      if (notification.type === "reconnect" && notification.session_id) {
        console.log(`Reconnect notification received for session: ${notification.session_id}`);
        reconnectToProcessing(notification.session_id);
      }
    };
  
    notificationWebSocket.onclose = () => {
      console.log("Notification WebSocket closed.");
    };
  
    notificationWebSocket.onerror = (error) => {
      console.error("Error with notification WebSocket:", error);
    };
  };  


const handleWebSocketMessage = (response) => {
  switch (response.type) {
    case "job_status":
      setQueueStatus({ queue: false });
      setAnalyzing(true);
      setResponse((prev) => ({
        ...prev,
        status: response.data.status,
        current_lecture: response.data.current_lecture,
        message: `Processing Lecture ${response.data.current_lecture}...`
      }));
      break;

    case "queue_status":
      setQueueStatus({ queue: true });
      console.log("Request is queued. Waiting for processing to start...");
      if (response.data.session_id) {
        reconnectToProcessing(response.data.session_id);
      }
      break;

    case "transcription_start":
      setQueueStatus({ queue: false });
      setAnalyzing(true);
      setResponse((prev) => ({
        ...prev,
        status: "processing",
        message: `Transcribing Lecture ${response.data.lecture_no}...`
      }));
      break;

    case "new_lecture_start":
      // Clear previous results when starting a new lecture
      setResponse({
        status: "processing",
        message: `Starting Lecture ${response.data.lecture_no}...`,
        lecture_no: response.data.lecture_no,
        criteria_evaluations: {}
      });
      break;

    case "metadata":
      setQueueStatus({ queue: false });
      setIsExtracting(false);
      setIsPreanalyzing(false);
      setResponse((prev) => ({
        ...prev,
        status: "evaluating",
        lecture_no: response.data.lecture_no,
        name: response.data.name,
        degree: response.data.degree,
        topic: response.data.topic,
        criteria_evaluations: {},
        total_score: 0,
        isNewEvaluation: true
      }));
      break;

    case "criterion_start":
      const criterion = response.data.criterion;
      const rubricEntry = showRubric ? showRubric[criterion] : null;
      if (criterion) {
        setResponse((prev) => ({
          ...prev,
          status: "evaluating",
          lecture_no: response.data.lecture_no,
          criteria_evaluations: {
            ...prev.criteria_evaluations,
            [criterion]: {
              feedback: "",
              score: 0,
              slide_image: null,
              slide_content: "",
              time_range: "",
              criteria_explanation: rubricEntry?.criteria_explanation || "",
              criteria_output: rubricEntry?.criteria_output || "",
              score_explanation: rubricEntry?.score_explanation || "",
            },
          },
        }));
      }
      break;

    case "analysis_chunk":
      setQueueStatus({ queue: false });
      if (response.data.criterion) {
        setResponse((prev) => {
          const criterion = response.data.criterion;
          const newFeedback =
            (prev.criteria_evaluations[criterion]?.feedback || "") + response.data.chunk;
          return {
            ...prev,
            criteria_evaluations: {
              ...prev.criteria_evaluations,
              [criterion]: {
                ...(prev.criteria_evaluations?.[criterion] || {}),
                feedback: newFeedback,
              },
            },
          };
        });
      }
      break;

    case "criterion_complete":
      if (response.data.criterion) {
        setResponse((prev) => {
          const criterion = response.data.criterion;
          
          // Log received data to help debug
          console.log("Received criterion_complete data:", {
            criterion,
            slideImages: response.data.slide_images,
            slideNumbers: response.data.slide_numbers,
            hasSlideImages: !!response.data.slide_images && Object.keys(response.data.slide_images || {}).length > 0
          });
          
          // Make sure slide_images is at least an empty object if it's undefined
          const slideImages = response.data.slide_images || {};
          
          const updatedEvaluation = {
            ...(prev.criteria_evaluations?.[criterion] || {}),
            feedback: response.data.full_analysis || prev.criteria_evaluations?.[criterion]?.feedback || "",
            score: response.data.score,
            slide_images: slideImages,
            slide_content: prev.criteria_evaluations?.[criterion]?.slide_content || "",
            time_range: response.data.time_range || prev.criteria_evaluations?.[criterion]?.time_range || "",
            slide_numbers: response.data.slide_numbers || []
          };

          // Log the updated evaluation for debugging
          console.log(`Updated evaluation for ${criterion}:`, {
            hasSlideImages: Object.keys(updatedEvaluation.slide_images).length > 0,
            slideNumbers: updatedEvaluation.slide_numbers
          });

          const updatedEvaluations = {
            ...prev.criteria_evaluations,
            [criterion]: updatedEvaluation,
          };
          
          // Calculate new total score
          const criteriaCount = Object.keys(updatedEvaluations).length;
          const sumScores = Object.values(updatedEvaluations).reduce(
            (acc, evaluation) => acc + (evaluation.score || 0),
            0
          );
          const newTotalScore = criteriaCount > 0 ? sumScores / criteriaCount : 0;

          return {
            ...prev,
            criteria_evaluations: updatedEvaluations,
            total_score: newTotalScore,
          };
        });
      }
      break;

    case "complete":
      setResponse((prev) => {
        // Store evaluation in database
        if (prev?.isNewEvaluation && prev?.lecture_no) {  // Add check for lecture_no
          const postData = {
            course_id: courseId,
            lecture_no: parseInt(prev.lecture_no),  // Ensure lecture_no is included and is a number
            response: Object.entries(prev.criteria_evaluations)
              .map(([criterion, evaluation]) => `${criterion}:\n${evaluation.feedback}`)
              .join('\n\n'),
            total_score: prev.total_score,
            scores: Object.entries(prev.criteria_evaluations).map(([criterion, evaluation]) => ({
              criterion,
              score: evaluation.score,
              feedback: evaluation.feedback,
              slide_content: evaluation.slide_content || "",
              slide_images: evaluation.slide_images || {},
              slide_numbers: evaluation.slide_numbers || [],
              time_range: evaluation.time_range || ""
            }))
          };

          // Store evaluation in database
          fetch(`${apiUrl}/afe/api/postUserData`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData)
          })
          .then(response => {
            if (!response.ok) {
              throw new Error('Failed to store evaluation');
            }
            console.log(`Evaluation stored for lecture ${prev.lecture_no}`);
          })
          .catch(error => {
            console.error('Error storing evaluation:', error);
          });
        } else {
          console.warn('Missing lecture number or not a new evaluation, skipping database storage');
        }

        return {
          ...prev,
          evaluation_complete: true,
          isNewEvaluation: false
        };
      });
      setAnalyzing(false);
      break;

    case "error":
      alert(`Error: ${response.data.message}`);
      setAnalyzing(false);
      setQueueStatus({ queue: false });
      break;

    default:
      console.log("Unknown response type:", response.type);
  }
};

const connectToWebSocket = (job_id) => {
  const websocketUrl = `${apiUrl.replace("http", "ws")}/afe/api/ws/lecture_evaluation`;
  const websocket = new WebSocket(websocketUrl);
  let heartbeatInterval;

  websocket.onopen = () => {
    console.log('WebSocket connected, sending job_id');
    websocket.send(JSON.stringify({ job_id }));
    setReconnectAttempts(0);

    // Set up heartbeat to keep connection alive
    heartbeatInterval = setInterval(() => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ type: "heartbeat" }));
      }
    }, 25000); // Send heartbeat every 25 seconds
  };

  websocket.onmessage = (event) => {
    const response = JSON.parse(event.data);
    if (response.type !== "heartbeat") { // Ignore heartbeat responses
      handleWebSocketMessage(response);
    }
  };

  websocket.onclose = (event) => {
    console.log('WebSocket connection closed', event);
    clearInterval(heartbeatInterval); // Clear heartbeat interval
    
    if (currentJobId) {
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        console.log(`Attempting to reconnect... (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
        // Exponential backoff for reconnection attempts
        const backoffTime = Math.min(RECONNECT_INTERVAL * Math.pow(1.5, reconnectAttempts), 300000); // Max 5 minutes
        setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connectToWebSocket(currentJobId);
        }, backoffTime);
      } else {
        console.log('Max reconnection attempts reached, switching to polling');
        startJobStatusPolling(currentJobId);
      }
    }
  };

  websocket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  return () => {
    clearInterval(heartbeatInterval);
    if (websocket.readyState === WebSocket.OPEN) {
      websocket.close();
    }
  };
};

const startJobStatusPolling = async (job_id) => {
  let pollCount = 0;
  const startTime = Date.now();
  
  const pollInterval = setInterval(async () => {
    try {
      // Check if we've exceeded the total timeout
      if (Date.now() - startTime > TRANSCRIPTION_TIMEOUT) {
        clearInterval(pollInterval);
        alert("Evaluation process timed out. Please check the results page later.");
        setAnalyzing(false);
        setResponseloading(false);
        return;
      }

      const response = await fetch(`${apiUrl}/afe/api/job_status/${job_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch job status');
      }
      
      const jobStatus = await response.json();
      pollCount++;

      // Update UI with current status
      setResponse(prev => ({
        ...prev,
        status: jobStatus.status,
        message: `Processing Lecture ${jobStatus.current_lecture}...`,
        current_lecture: jobStatus.current_lecture
      }));

      if (jobStatus.status === "COMPLETED") {
        clearInterval(pollInterval);
        const evaluationResponse = await fetch(
          `${apiUrl}/afe/api/getEvaluation?course_id=${courseId}&lecture_no=${jobStatus.current_lecture}`
        );
        
        if (evaluationResponse.ok) {
          const data = await evaluationResponse.json();
          setResponse({
            lecture_no: jobStatus.current_lecture,
            total_score: data.total_score,
            criteria_evaluations: data.criteria_scores.reduce((acc, scoreData) => {
              acc[scoreData.criterion] = {
                feedback: scoreData.feedback,
                score: scoreData.score,
                slide_images: scoreData.slide_images || {},
                slide_numbers: scoreData.slide_numbers || [],
                time_range: scoreData.time_range || "",
                slide_content: scoreData.slide_content || ""
              };
              return acc;
            }, {}),
            status: "COMPLETED"
          });
        }
        setAnalyzing(false);
        setResponseloading(false);
      } else if (jobStatus.status === "FAILED") {
        clearInterval(pollInterval);
        alert(`Job failed: ${jobStatus.error_message}`);
        setAnalyzing(false);
        setResponseloading(false);
      } else if (jobStatus.status === "IN_PROGRESS") {
        // Update UI to show progress
        setResponse(prev => ({
          ...prev,
          message: `Processing Lecture ${jobStatus.current_lecture}... (Polling attempt: ${pollCount})`
        }));
      }
    } catch (error) {
      console.error('Error polling job status:', error);
      // Don't clear the interval on error, keep trying
    }
  }, POLLING_INTERVAL);

  // Store the interval ID for cleanup
  return () => clearInterval(pollInterval);
};

const handleEvaluate = async () => {
  if (!courseId || !startLecture || !endLecture) {
    alert("Course ID and Lecture Range are required.");
    return;
  }

  const start = parseInt(startLecture);
  const end = parseInt(endLecture);

  if (end < start) {
    alert("End lecture number cannot be less than start lecture number.");
    return;
  }

  // Clear the response box when starting a new evaluation
  setResponse(null);

  try {
    const folderExistsResponse = await fetch(`${apiUrl}/afe/check_course_folder?courseId=${courseId}`);
    const folderExists = await folderExistsResponse.json();

    if (!folderExists.exists) {
      alert("No videos found for this Course ID.");
      return;
    }

    // Process lectures one at a time
    for (let lectureNo = start; lectureNo <= end; lectureNo++) {
      setResponseloading(true);
      setAnalyzing(true);
      setQueueStatus({ queue: false });

      try {
        // Check for existing evaluation first
        const evaluationResponse = await fetch(
          `${apiUrl}/afe/api/getEvaluation?course_id=${courseId}&lecture_no=${lectureNo}`
        );
        
        if (evaluationResponse.ok) {
          const data = await evaluationResponse.json();
          console.log(`Lecture ${lectureNo} already evaluated. Displaying results...`);
          setResponse({
            lecture_no: lectureNo,
            total_score: data.total_score,
            criteria_evaluations: data.criteria_scores.reduce((acc, scoreData) => {
              acc[scoreData.criterion] = {
                feedback: scoreData.feedback,
                score: scoreData.score,
                slide_images: scoreData.slide_images || {},
                slide_numbers: scoreData.slide_numbers || [],
                time_range: scoreData.time_range || "",
                slide_content: scoreData.slide_content || ""
              };
              return acc;
            }, {}),
          });
          setResponseloading(false);
          setAnalyzing(false);
          continue;
        }

        // Start new evaluation job for this lecture
        const jobResponse = await fetch(`${apiUrl}/afe/api/start_lecture_evaluation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            course_id: courseId,
            start_lecture: lectureNo,
            end_lecture: lectureNo
          })
        });

        if (!jobResponse.ok) {
          throw new Error('Failed to create evaluation job');
        }

        const { job_id } = await jobResponse.json();
        setCurrentJobId(job_id);
        setReconnectAttempts(0);

        // Wait for this lecture to complete before moving to the next one
        await new Promise((resolve, reject) => {
          let cleanup = null;
          let isComplete = false;
          let pollInterval = null;

          const handleCompletion = () => {
            isComplete = true;
            if (cleanup) cleanup();
            if (pollInterval) clearInterval(pollInterval);
            setAnalyzing(false);  // Set analyzing to false only when truly complete
            setResponseloading(false);
            resolve();
          };

          const startPolling = () => {
            let pollCount = 0;
            const startTime = Date.now();

            pollInterval = setInterval(async () => {
              try {
                if (Date.now() - startTime > TRANSCRIPTION_TIMEOUT) {
                  clearInterval(pollInterval);
                  setAnalyzing(false);
                  setResponseloading(false);
                  reject(new Error("Evaluation process timed out"));
                  return;
                }

                const response = await fetch(`${apiUrl}/afe/api/job_status/${job_id}`);
                if (!response.ok) {
                  throw new Error('Failed to fetch job status');
                }

                const jobStatus = await response.json();
                pollCount++;

                setResponse(prev => ({
                  ...prev,
                  status: jobStatus.status,
                  message: `Processing Lecture ${jobStatus.current_lecture}... (Polling attempt: ${pollCount})`,
                  current_lecture: jobStatus.current_lecture
                }));

                if (jobStatus.status === "COMPLETED") {
                  const evaluationResponse = await fetch(
                    `${apiUrl}/afe/api/getEvaluation?course_id=${courseId}&lecture_no=${jobStatus.current_lecture}`
                  );

                  if (evaluationResponse.ok) {
                    const data = await evaluationResponse.json();
                    setResponse({
                      lecture_no: jobStatus.current_lecture,
                      total_score: data.total_score,
                      criteria_evaluations: data.criteria_scores.reduce((acc, scoreData) => {
                        acc[scoreData.criterion] = {
                          feedback: scoreData.feedback,
                          score: scoreData.score,
                          slide_images: scoreData.slide_images || {},
                          slide_numbers: scoreData.slide_numbers || [],
                          time_range: scoreData.time_range || "",
                          slide_content: scoreData.slide_content || ""
                        };
                        return acc;
                      }, {}),
                      status: "COMPLETED"
                    });
                    handleCompletion();
                  }
                } else if (jobStatus.status === "FAILED") {
                  setAnalyzing(false);
                  setResponseloading(false);
                  reject(new Error(jobStatus.error_message));
                }
              } catch (error) {
                console.error('Error polling job status:', error);
              }
            }, POLLING_INTERVAL);
          };

          // Set up WebSocket connection with reconnection logic
          const setupWebSocket = () => {
            const websocket = new WebSocket(`${apiUrl.replace("http", "ws")}/afe/api/ws/lecture_evaluation`);
            let heartbeatInterval;

            websocket.onopen = () => {
              console.log('WebSocket connected, sending job_id');
              websocket.send(JSON.stringify({ job_id }));
              
              // Set up heartbeat
              heartbeatInterval = setInterval(() => {
                if (websocket.readyState === WebSocket.OPEN) {
                  websocket.send(JSON.stringify({ type: "heartbeat" }));
                }
              }, 25000);
            };

            websocket.onmessage = (event) => {
              const response = JSON.parse(event.data);
              if (response.type !== "heartbeat") {
                handleWebSocketMessage(response);
                
                // Check for completion
                if (response.type === "complete") {
                  handleCompletion();
                }
              }
            };

            websocket.onclose = (event) => {
              console.log('WebSocket connection closed', event);
              clearInterval(heartbeatInterval);

              if (!isComplete) {
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                  const backoffTime = Math.min(RECONNECT_INTERVAL * Math.pow(1.5, reconnectAttempts), 300000);
                  setTimeout(() => {
                    setReconnectAttempts(prev => prev + 1);
                    if (!isComplete) setupWebSocket();
                  }, backoffTime);
                } else {
                  console.log('Max reconnection attempts reached, switching to polling');
                  startPolling();
                }
              }
            };

            websocket.onerror = (error) => {
              console.error('WebSocket error:', error);
            };

            // Return cleanup function
            return () => {
              clearInterval(heartbeatInterval);
              if (websocket.readyState === WebSocket.OPEN) {
                websocket.close();
              }
            };
          };

          // Start WebSocket connection
          cleanup = setupWebSocket();

          // Set timeout for the entire process
          setTimeout(() => {
            if (!isComplete) {
              setAnalyzing(false);
              setResponseloading(false);
              reject(new Error("Evaluation process timed out"));
            }
          }, TRANSCRIPTION_TIMEOUT);
        });

        // Clear states after completion
        setCurrentJobId(null);
        setReconnectAttempts(0);

      } catch (error) {
        console.error(`Error processing lecture ${lectureNo}:`, error);
        alert(`Failed to process lecture ${lectureNo}. Error: ${error.message}`);
        setResponseloading(false);
        setAnalyzing(false);
        break; // Stop processing if there's an error
      }
    }

  } catch (error) {
    console.error("Error:", error);
    alert("Failed to process the request.");
    setResponseloading(false);
    setAnalyzing(false);
  }
};

// Extract evaluation scores for graph visualization
const evaluationData = response?.criteria_evaluations 
  ? Object.keys(response.criteria_evaluations).map((criterion) => ({
      criterion: String(criterion), // Force conversion to a string
      score: response.criteria_evaluations[criterion]?.score || 0
    }))
  : [];

  return (
    <div className="main-container">
    <Header onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)} tag="Instructor Evaluation" />
    <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
    <div className="evaluator-container">
    {/* <Sidebar isActive={isSidebarActive} toggleSidebar={toggleSidebar} setSidebarActive={setIsSidebarActive}/> */}
      
    <div className="input-container">
      {/* Form Section - Dark Theme Layout */}
      <div style={{ 
        backgroundColor: '#34495e', 
        padding: '40px', 
        borderRadius: '12px', 
        marginBottom: '30px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        border: '1px solid #4a5f7a',
        maxWidth: '1400px',
        width: '95%',
        margin: '0 auto 30px auto'
      }}>
        <h2 style={{ 
          textAlign: 'center', 
          marginBottom: '30px', 
          color: '#ecf0f1',
          fontSize: '26px',
          fontWeight: '600'
        }}>
          Instructor Evaluation Setup
        </h2>
        
        {/* Single Row: All Fields */}
        <div style={{ display: 'flex', gap: '25px', marginBottom: '30px' }}>
          <div className="form-group" style={{ flex: '1' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '10px', 
              fontWeight: '500', 
              color: '#bdc3c7',
              fontSize: '15px'
            }}>
              Course ID
            </label>
            <div className="dropdown-container">
              <input
                type="text"
                value={courseId}
                onChange={handleCourseIdChange}
                onBlur={handleCourseIdBlur}
                className={`input-field ${!isCourseIdValid ? 'invalid-input' : ''}`}
                list="course-id-suggestions"
                required
                placeholder="Search Course ID"
                style={{
                  width: '100%',
                  padding: '15px 20px',
                  border: '2px solid #5a6c7d',
                  borderRadius: '8px',
                  fontSize: '15px',
                  transition: 'border-color 0.3s ease',
                  backgroundColor: '#2c3e50',
                  color: '#ecf0f1'
                }}
              />
              <datalist id="course-id-suggestions">
                {courseIdSuggestions.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </datalist>
            </div>
            {!isCourseIdValid && (
              <div className="error-message" style={{
                color: '#e74c3c',
                fontSize: '12px',
                marginTop: '5px'
              }}>
                Invalid Course ID. Please select a valid one.
              </div>
            )}
          </div>
          
          <div className="form-group" style={{ flex: '1' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '10px', 
              fontWeight: '500', 
              color: '#bdc3c7',
              fontSize: '15px'
            }}>
              Instructor Name
            </label>
            <input
              type="text"
              value={instructorName}
              onChange={(e) => setInstructorName(e.target.value)}
              required
              placeholder="Instructor Name"
              style={{
                width: '100%',
                padding: '15px 20px',
                border: '2px solid #5a6c7d',
                borderRadius: '8px',
                fontSize: '15px',
                transition: 'border-color 0.3s ease',
                backgroundColor: '#2c3e50',
                color: '#ecf0f1'
              }}
            />
          </div>
          
          <div className="form-group" style={{ flex: '1' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '10px', 
              fontWeight: '500', 
              color: '#bdc3c7',
              fontSize: '15px'
            }}>
              Year / Semester
            </label>
            <input
              type="text"
              value={yearSemester}
              onChange={(e) => setYearSemester(e.target.value)}
              placeholder="e.g., Fall 2025"
              style={{
                width: '100%',
                padding: '15px 20px',
                border: '2px solid #5a6c7d',
                borderRadius: '8px',
                fontSize: '15px',
                transition: 'border-color 0.3s ease',
                backgroundColor: '#2c3e50',
                color: '#ecf0f1'
              }}
            />
          </div>
          
          <div className="form-group" style={{ flex: '1' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '10px', 
              fontWeight: '500', 
              color: '#bdc3c7',
              fontSize: '15px'
            }}>
              Start Lecture
            </label>
            <input
              type="number"
              value={startLecture}
              onChange={(e) => setStartLecture(e.target.value)}
              required
              placeholder="Start"
              style={{
                width: '100%',
                padding: '15px 20px',
                border: '2px solid #5a6c7d',
                borderRadius: '8px',
                fontSize: '15px',
                transition: 'border-color 0.3s ease',
                backgroundColor: '#2c3e50',
                color: '#ecf0f1'
              }}
            />
          </div>
          
          <div className="form-group" style={{ flex: '1' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '10px', 
              fontWeight: '500', 
              color: '#bdc3c7',
              fontSize: '15px'
            }}>
              End Lecture
            </label>
            <input
              type="number"
              value={endLecture}
              onChange={(e) => setEndLecture(e.target.value)}
              required
              placeholder="End"
              style={{
                width: '100%',
                padding: '15px 20px',
                border: '2px solid #5a6c7d',
                borderRadius: '8px',
                fontSize: '15px',
                transition: 'border-color 0.3s ease',
                backgroundColor: '#2c3e50',
                color: '#ecf0f1'
              }}
            />
          </div>
        </div>

        {/* Evaluate Button */}
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <button
            className="evaluate-button"
            onClick={handleEvaluate}
            disabled={analyzing}
            style={{ 
              minWidth: '220px', 
              padding: '16px 36px',
              backgroundColor: analyzing ? '#7f8c8d' : '#3498db',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '17px',
              fontWeight: '600',
              cursor: analyzing ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(52, 152, 219, 0.3)'
            }}
            onMouseOver={(e) => {
              if (!analyzing) {
                e.target.style.backgroundColor = '#2980b9';
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 16px rgba(52, 152, 219, 0.4)';
              }
            }}
            onMouseOut={(e) => {
              if (!analyzing) {
                e.target.style.backgroundColor = '#3498db';
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 12px rgba(52, 152, 219, 0.3)';
              }
            }}
          >
            {analyzing ? (
              <>
                <FontAwesomeIcon icon={faCircleNotch} spin style={{ marginRight: '8px' }} />
                Processing...
              </>
            ) : (
              "Start Evaluation"
            )}
          </button>
        </div>
      </div>

      {selectedVideo && (
        <div className="video-info" style={{ 
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: '#27ae60',
          borderRadius: '8px',
          border: '1px solid #2ecc71'
        }}>
          <p style={{ margin: 0, color: '#fff', fontWeight: '500' }}>
            <strong>Selected Video:</strong> {selectedVideo}
          </p>
        </div>
      )}
    </div>

    <div className="response-container">
      <div style={{ width: '100%' }}>
        <div className="response-header" style={{
          backgroundColor: '#2c3e50',
          color: '#fff',
          padding: '20px 25px',
          borderRadius: '12px 12px 0 0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Evaluation Results</h2>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              onClick={downloadPDF} 
              className="download-button"
              style={{
                padding: '10px 20px',
                backgroundColor: '#f39c12',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.3s ease'
              }}
            >
              Download PDF
            </button>
            <button 
              onClick={() => setShowModal(true)} 
              disabled={!selectedText} 
              className="feedback-button"
              style={{
                padding: '10px 20px',
                backgroundColor: selectedText ? '#27ae60' : '#95a5a6',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: selectedText ? 'pointer' : 'not-allowed',
                transition: 'background-color 0.3s ease'
              }}
            >
              Send Feedback
            </button>
          </div>
        </div>

        <div
  className={`response-content ${queueStatus?.queue ? "queued" : ""} ${analyzing ? "processing" : ""}`}
  contentEditable={false}
  suppressContentEditableWarning={true}
  onMouseUp={handleTextSelection}
>
  {queueStatus?.queue ? (
    <p className="queue-status">
      Your request is queued. Please wait...
      <span className="loading-dots">
        <span className="dot">.</span>
        <span className="dot">.</span>
        <span className="dot">.</span>
      </span>
    </p>
  ) : analyzing || (response?.status === "processing") ? (
    <p className="analyzing-text">
      {response?.message || "Processing..."}
      <span className="loading-dots">
        <span className="dot">.</span>
        <span className="dot">.</span>
        <span className="dot">.</span>
      </span>
    </p>
  ) : response?.status === "evaluating" || response?.criteria_evaluations ? (
    <>
      <div className="total-score-box">
        <h3>
          Total Score: {response.total_score !== undefined 
            ? `${parseFloat(response.total_score).toFixed(2)}/5`
            : '-'}
        </h3>
        {response.lecture_no && (
          <h4>Lecture {response.lecture_no}</h4>
        )}
      </div>

      {evaluationData.length > 0 && (
        <div className="chart-container">
          <h3>Slide Evaluation Overview</h3>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={evaluationData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="criterion" tick={{ fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 5]} />
              <Radar name="Score" dataKey="score" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      {evaluationData.length > 0 && (
        <div className="chart-container">
          <h3>Slide Scores</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart 
              data={evaluationData} 
              margin={{ top: 20, right: 30, left: 20, bottom: 90 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="criterion" 
                tick={{ fontSize: 12, angle: -25, textAnchor: 'end', dy: 10 }}
                interval={0} 
              />
              <YAxis domain={[0, 5]} />
              <Tooltip />
              <Bar dataKey="score" fill="#F4BC1C" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="slides-container">
        {Object.keys(response.criteria_evaluations).map((groupKey, index) => {
          const evaluation = response.criteria_evaluations[groupKey];
          const slideNumbers = evaluation.slide_numbers || [];
          const slideImages = evaluation.slide_images || {};
          
          return (
            <div key={index} className="slide-group-box">
              <div className="slide-header">
                <h3>{groupKey}</h3>
                <span className="slide-time">{evaluation.time_range}</span>
                <span className="slide-score">Score: {evaluation.score}/5</span>
              </div>
              
              {Object.keys(slideImages).length > 0 && (
                <div className="slides-section">
                  <div className="slides-horizontal-scroll-header">
                    <h4>Slide Images</h4>
                    <div className="scroll-indicator">
                      <span>Scroll to view all slides</span>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 18L15 12L9 6" stroke="#F4BC1C" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" transform="rotate(90 12 12)"/>
                      </svg>
                    </div>
                  </div>
                  <div className="slides-horizontal-scroll">
                    <div className="slides-scroll-container">
                      {slideNumbers.map((slideNum, idx) => {
                        console.log(`Rendering slide ${slideNum}, has image: ${!!slideImages[slideNum]}`);
                        return slideImages[slideNum] ? (
                          <div key={idx} className="slide-image-container">
                            <p className="slide-number">Slide {slideNum}</p>
                            <img 
                              src={`data:image/jpeg;base64,${slideImages[slideNum]}`} 
                              alt={`Slide ${slideNum} image`}
                              className="slide-image"
                              onError={(e) => {
                                console.error(`Error loading slide image for Slide ${slideNum}:`, e);
                                e.target.src = "data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='150' viewBox='0 0 200 150'%3E%3Crect fill='%23CCCCCC' width='200' height='150'/%3E%3Ctext fill='%23333333' font-family='Arial,sans-serif' font-size='12' text-anchor='middle' x='100' y='75'%3EImage failed to load%3C/text%3E%3C/svg%3E";
                              }}
                            />
                          </div>
                        ) : (
                          <div key={idx} className="slide-image-container slide-image-missing">
                            <p className="slide-number">Slide {slideNum}</p>
                            <div className="slide-image-placeholder">
                              <p>No image available</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
              
              <div className="slide-evaluation">
                <h4>Evaluation:</h4>
                <div 
                  dangerouslySetInnerHTML={{
                    __html: marked(evaluation.feedback || 'No evaluation provided.'),
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </>
  ) : (
    <p className="default-message">Please enter Course ID and Lecture Range to begin evaluation.</p>
  )}
</div>

      </div>
    </div>

      <Modal 
        show={showModal} 
        onClose={closeModal} 
        selectedText={selectedText} 
        handleInputChange={handleInputChange} 
        feedback={feedback}
        loading={loading}
        setLoading={setLoading} 
        setShowModal={setShowModal}
        preAnalysisData={preAnalysisData}
      />
       
    </div>
    <footer className="footer">
    <div className="footer-content">
        <div className="branding">
        <h2><span className="highlight">[</span>  Spanda<span className="highlight">.</span>AI  <span className="highlight">]</span></h2>
            <p>Empowering insights and intelligence through AI-driven solutions.</p>
            <hr className="divider" />
        </div>
        
        <div className="footer-links">
            <h3>Quick Links</h3>
            <ul>
                <li><FontAwesomeIcon icon={faAddressCard} className="link-icon" /><a href="https://www.spanda.ai/about"> About Us</a></li>
                <li><FontAwesomeIcon icon={faTasks} className="link-icon" /><a href="https://www.spanda.ai/"> Services</a></li>
                <li><FontAwesomeIcon icon={faPhone} className="link-icon" /><a href="https://www.spanda.ai/contact"> Contact</a></li>
                <li><FontAwesomeIcon icon={faLock} className="link-icon" /><a href="https://www.spanda.ai/"> Privacy Policy</a></li>
            </ul>
            <hr className="divider" />
        </div>
        
        <div className="social-media">
            <h3>Connect with Us</h3>
            <div className="social-icons">
                <a href="https://www.facebook.com" target="_blank" rel="noopener noreferrer">
                    <FontAwesomeIcon icon={faFacebook} />
                </a>
                <a href="https://www.twitter.com" target="_blank" rel="noopener noreferrer">
                    <FontAwesomeIcon icon={faTwitter} />
                </a>
                <a href="https://www.linkedin.com/company/spandaAI" target="_blank" rel="noopener noreferrer">
                    <FontAwesomeIcon icon={faLinkedin} />
                </a>
                <a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer">
                    <FontAwesomeIcon icon={faInstagram} />
                </a>
            </div>
        </div>
    </div>
    
    <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} Spanda.AI. All Rights Reserved.</p>
    </div>
    </footer>


    </div>

  );
};


const formatFileSize = bytes => {
  if (bytes >= 1000000) return (bytes / 1000000).toFixed(2) + ' MB';
  return (bytes / 1000).toFixed(2) + ' KB';
};


export default Evaluation;
