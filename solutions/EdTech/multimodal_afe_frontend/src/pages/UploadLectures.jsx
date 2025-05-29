import React, { useState, useEffect } from "react";
import "../styles/UploadLectures.css";
import { FaFileUpload, FaGoogleDrive } from "react-icons/fa";
import { IoShareSocial } from "react-icons/io5";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import axios from "axios";

const UploadLectures = () => {
  const [courseId, setCourseId] = useState("");
  const [instructorName, setInstructorName] = useState("");
  const [yearSemester, setYearSemester] = useState("");
  const [uploadedVideos, setUploadedVideos] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [lectureNumbers, setLectureNumbers] = useState({});
  const [loading, setLoading] = useState(false);
  const [courseIdSuggestions, setCourseIdSuggestions] = useState([]);
  const [isCourseIdValid, setIsCourseIdValid] = useState(true);
  const [uploadProgress, setUploadProgress] = useState({});
  const [currentUploads, setCurrentUploads] = useState({});
  const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks
  // const apiUrl = window?.env?.REACT_APP_API_URL || "https://da.wilp-connect.net";
  const apiUrl = "http://localhost:8009";

  // Fetch course IDs on component mount
  useEffect(() => {
    fetchCourseIds();
  }, []);

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
    fetchCourseIds(value); // Fetch suggestions based on input
  };

  // Validate course ID when focus is lost
  const handleCourseIdBlur = () => {
    if (courseId && !courseIdSuggestions.includes(courseId)) {
      setIsCourseIdValid(false);
      setCourseId("");
    } else {
      setIsCourseIdValid(true);
      // Fetch instructor name if course ID is valid
      if (courseId) {
        fetchInstructorName(courseId);
      }
    }
  };

  // Fetch instructor name for selected course ID
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

  const uploadChunks = async (file, lectureNo) => {
    try {
      const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
      
      // Initialize upload session
      const formData = new FormData();
      formData.append('courseId', courseId);
      formData.append('instructorName', instructorName);
      formData.append('fileName', file.name);
      formData.append('totalChunks', totalChunks);
      formData.append('lectureNo', lectureNo);
      if (yearSemester) {
        formData.append('yearSemester', yearSemester);
      }

      const initResponse = await axios.post(`${apiUrl}/afe/init_chunked_upload`, formData);
      const sessionId = initResponse.data.session_id;

      // Upload chunks
      for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);

        const chunkFormData = new FormData();
        chunkFormData.append('session_id', sessionId);
        chunkFormData.append('chunk_number', i + 1);
        chunkFormData.append('chunk', chunk);

        await axios.post(`${apiUrl}/afe/upload_chunk`, chunkFormData, {
          onUploadProgress: (progressEvent) => {
            const percentComplete = Math.round(
              ((i * CHUNK_SIZE + progressEvent.loaded) / file.size) * 100
            );
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: percentComplete
            }));
          }
        });
      }

      return true;
    } catch (error) {
      console.error(`Error uploading file ${file.name}:`, error);
      throw error;
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!courseId || !instructorName) {
      alert("Course ID and Instructor Name are required before uploading videos.");
      return;
    }

    // Fetch existing lecture numbers from the backend
    const existingLecturesResponse = await fetch(`${apiUrl}/afe/get_existing_lectures?courseId=${courseId}`);
    const existingLectures = await existingLecturesResponse.json();
    let maxLectureNo = existingLectures.length > 0 ? Math.max(...existingLectures) : 0;

    setUploadProgress({});
    const newVideos = files.map((file, index) => {
      const lectureNo = maxLectureNo + index + 1;
      return {
        name: file.name,
        videoUrl: URL.createObjectURL(file),
        lectureNo,
        fileObject: file,
      };
    });

    setUploadedVideos([...uploadedVideos, ...newVideos]);

    // Store default lecture numbers
    const newLectureNumbers = {};
    newVideos.forEach((video) => {
      newLectureNumbers[video.name] = video.lectureNo;
    });

    setLectureNumbers((prev) => ({ ...prev, ...newLectureNumbers }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!courseId || !instructorName || uploadedVideos.length === 0) {
      alert("Please fill all fields and upload at least one video.");
      return;
    }

    setLoading(true);

    try {
      for (const video of uploadedVideos) {
        try {
          await uploadChunks(video.fileObject, lectureNumbers[video.name]);
        } catch (error) {
          console.error(`Failed to upload ${video.name}:`, error);
          alert(`Failed to upload ${video.name}. Please try again.`);
          setLoading(false);
          return;
        }
      }

      alert("Videos uploaded successfully!");
      setUploadedVideos([]);
      setCourseId("");
      setInstructorName("");
      setYearSemester("");
      setUploadProgress({});
    } catch (error) {
      console.error("Upload error:", error);
      alert("An error occurred while uploading.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)} tag="Upload Lectures" />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <main className="app-main">
        <div className="main-container">
          <h1 className="page-title">Upload Lecture Videos</h1>

          <div className="input-row">

<div className="form-group">
  <label htmlFor="courseId">Course ID</label>
  <div className="dropdown-container">
    <input
      type="text"
      id="courseId"
      placeholder="Search and select a Course ID"
      value={courseId}
      onChange={handleCourseIdChange}
      onBlur={handleCourseIdBlur}
      className={`input-field ${!isCourseIdValid ? 'invalid-input' : ''}`}
      list="course-id-suggestions"
      required
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
    <div className="error-message">
      Invalid Course ID. Please select a valid one.
    </div>
  )}
</div>
            <div className="form-group">
              <label htmlFor="instructorName">Instructor Name</label>
              <input
                type="text"
                id="instructorName"
                placeholder="Enter Instructor Name"
                value={instructorName}
                onChange={(e) => setInstructorName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="yearSemester">Year / Semester</label>
              <input
                type="text"
                id="yearSemester"
                placeholder="e.g., Fall 2025"
                value={yearSemester}
                onChange={(e) => setYearSemester(e.target.value)}
              />
            </div>
          </div>

          <div className="upload-options">
            <button className="upload-option">
              <FaFileUpload className="icon" />
              <span>Upload from Local System</span>
              <input
                type="file"
                accept="video/*"
                multiple
                className="file-input"
                onChange={handleFileUpload}
              />
            </button>
            <button className="upload-option" disabled>
              <FaGoogleDrive className="icon" />
              <span>Fetch from Google Drive</span>
            </button>
            <button className="upload-option" disabled>
              <IoShareSocial className="icon" />
              <span>Fetch from SharePoint</span>
            </button>
          </div>

          {uploadedVideos.length > 0 && (
            <div className="video-gallery">
              {uploadedVideos.map((video, index) => (
                <div key={index} className="video-card">
                  <video src={video.videoUrl} controls className="video-thumbnail"></video>
                  <div className="video-details">
                    <p className="video-name">{video.name}</p>
                    <label className="lecture-number-label">Lecture Number:</label>
                    <input
                      type="number"
                      min="1"
                      className="lecture-number-input"
                      value={lectureNumbers[video.name] || video.lectureNo}
                      onChange={(e) => {
                        setLectureNumbers({
                          ...lectureNumbers,
                          [video.name]: parseInt(e.target.value, 10),
                        });
                      }}
                    />
                    {uploadProgress[video.name] !== undefined && (
                      <div className="upload-progress">
                        <div 
                          className="progress-bar" 
                          style={{ width: `${uploadProgress[video.name]}%` }}
                        ></div>
                        <span>{uploadProgress[video.name]}%</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="submit-container">
            <button className="submit-button" onClick={handleSubmit} disabled={loading}>
              {loading ? (
                <>
                  <span className="loader"></span> Processing...
                </>
              ) : (
                "Submit"
              )}
            </button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default UploadLectures;