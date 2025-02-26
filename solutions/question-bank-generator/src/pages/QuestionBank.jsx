import { useEffect, useState, useRef } from "react";import axios from 'axios'; // Axios for API requests
import { extractTextFromFile } from '../utils/fileUtils';
import '../styles/questionBank.css';


const QUESTION_SERVICE_URL = "http://localhost:8090/db"
const GENERATION_SERVICE_URL = "http://localhost:8090"

const Notification = ({ message, type, onClose }) => {
  if (!message) return null;

  return (
    <div className={`notification ${type}`}>
      {message}
      <button className="close-btn" onClick={onClose}>&times;</button>
    </div>
  );
};

const QuestionBank = () => {
  const [formData, setFormData] = useState({
    courseId: '',
    examType: 'Any',
    topic: '',
    context: '',
    exampleQuestion: '', // Add this new state field
    questionType: 'Multiple Choice Questions',
    difficultyLevel: 'Medium',
    numberOfQuestions: 3,
    mcqOptionsCount: 4,
    questionFormat: 'Non-Numerical/Theoretical',
  });

  const [notification, setNotification] = useState({ message: '', type: '' }); // Notification state
  const [addedQuestionIds, setAddedQuestionIds] = useState(new Set());
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [fixedMetadata, setFixedMetadata] = useState(null);
  const [loadingQuestionIds, setLoadingQuestionIds] = useState(new Set());
  const [feedbackData, setFeedbackData] = useState({});
  const [fileStatuses, setFileStatuses] = useState([]);
  const [submittedFeedback, setSubmittedFeedback] = useState(new Set()); // To track which questions have submitted feedback
  const [courseIdSuggestions, setCourseIdSuggestions] = useState([]); // Course ID dropdown suggestions
  const [isCourseIdValid, setIsCourseIdValid] = useState(true);

  const fetchCourseIds = async (searchText = ''

  ) => {
    try {
      const response = await axios.get(`http://localhost:8090/db/fetch-courseids`, {
        params: { search_text: searchText },
      });
      setCourseIdSuggestions(response.data.course_ids);
    } catch (err) {
      console.error('Error fetching Course IDs:', err);
    }
  };

  useEffect(() => {
    fetchCourseIds();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
  
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  
    // Trigger Course ID suggestions fetching
    if (name === 'courseId') {
      fetchCourseIds(value); // Fetch suggestions based on input
    }
  };  

  const handleCourseIdBlur = () => {
    if (!courseIdSuggestions.includes(formData.courseId)) {
      setFormData((prev) => ({ ...prev, courseId: '' }));
      setIsCourseIdValid(false);
    } else {
      setIsCourseIdValid(true);
    }
  };

  const handleNotification = (message, type) => {
    setNotification({ message, type }); // Set notification with type
    setTimeout(() => setNotification({ message: '', type: '' }), 4000); // Clear after 4 seconds
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
  
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  
    // Validate file type
    if (!allowedTypes.includes(file.type)) {
      handleNotification('Unsupported file type. Please upload .pdf or .docx files only.', 'error');
      event.target.value = ''; // Reset the file input
      return;
    }
  
    setIsUploading(true); // Start the upload process
  
    try {
      const formData = new FormData();
      formData.append('file', file);
  
      // Call the API to process the file
      const response = await axios.post(`${GENERATION_SERVICE_URL}/api/extract_text_from_file_and_analyze_images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      // Extract the text and populate the context field
      const { text_and_image_analysis } = response.data;
      if (!text_and_image_analysis) {
        throw new Error('No text extracted from the file.');
      }
  
      setFormData((prev) => ({
        ...prev,
        context: text_and_image_analysis,
      }));
  
      handleNotification('File uploaded and processed successfully!', 'success');
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail || 'Error processing the uploaded file. Please try again.';
      handleNotification(errorMessage, 'error');
    } finally {
      setIsUploading(false); // End the upload process
      event.target.value = ''; // Reset the file input
    }
  };  
  
  // Add this after your other handler functions like handleAddToQuestionBank
const handleFeedbackSubmit = async (questionId) => {
  try {
    const question = generatedQuestions.find(q => q.id === questionId);
    const feedback = feedbackData[questionId];
    
    if (!feedback || !feedback.trim()) {
      handleNotification('Please enter feedback before submitting.', 'error');
      return;
    }

    // Prepare options array to individual option fields
    const optionsArray = question.options || [];
    const optionsObject = {};
    for (let i = 0; i < 6; i++) {
      optionsObject[`option_${i + 1}`] = optionsArray[i] || null;
    }

    const payload = {
      question_id: questionId,
      feedback_text: feedback,
      course_id: question.metadata.courseId,
      exam_type: question.metadata.examType,
      topic: question.metadata.topic,
      question_text: question.text,
      question_type: question.metadata.questionType,
      difficulty_level: question.metadata.difficulty,
      no_of_options: question.metadata.no_of_options,
      correct_answer: question.correctAnswer,
      ...optionsObject
    };

    await axios.post(`${QUESTION_SERVICE_URL}/add-feedback`, payload);
    
    // Mark feedback as submitted
    setSubmittedFeedback(prev => new Set([...prev, questionId]));
    
    // Clear the feedback input
    setFeedbackData(prev => ({
      ...prev,
      [questionId]: ''
    }));
    
    handleNotification('Feedback submitted successfully!', 'success');
  } catch (err) {
    console.error('Failed to submit feedback:', err);
    handleNotification('Failed to submit feedback.', 'error');
  }
};

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear any previous errors or generated questions
    setIsLoading(true);
    setError('');
    setGeneratedQuestions([]);
  
    try {
      // Prepare the payload for the API with exact field names matching the backend
      const payload = {
        topic: formData.topic,
        difficulty: formData.difficultyLevel,
        type_of_question: formData.questionType,
        no_of_questions: parseInt(formData.numberOfQuestions), // Ensure this is a number
        courseid: formData.courseId,
        context: formData.context || null,
        no_of_options: formData.questionType === 'Multiple Choice Questions' 
          ? parseInt(formData.mcqOptionsCount) // Ensure this is a number
          : null,
        numericality: formData.questionFormat,
        few_shot: formData.exampleQuestion
      };
  
      // Make the API call
      const response = await axios.post(
        `${GENERATION_SERVICE_URL}/api/questions_generation`,
        payload
      );
  
      // Extract questions from the API response
      const { questions } = response.data;
  
      // Take a snapshot of the current metadata
      const metadataSnapshot = {
        topic: formData.topic,
        difficulty: formData.difficultyLevel,
        questionType: formData.questionType,
        courseId: formData.courseId,
        examType: formData.examType,
        context: formData.context,
        numericality: formData.questionFormat,
        few_shot: formData.exampleQuestion,
        no_of_options: formData.questionType === 'Multiple Choice Questions'
          ? parseInt(formData.mcqOptionsCount)
          : null,
      };
  
      // Format the questions with metadata and additional details
      const formattedQuestions = questions.map((q, index) => ({
        id: index + 1,
        text: q.question,
        originalText: q.question,
        correctAnswer: q.key_points || q.correct_answer || "",
        options: q.options || [],
        originalOptionsCount: q.options?.length || 0,
        metadata: metadataSnapshot,
        isEditable: false,
        isAnswerVisible: false,
        hasAnswer: !!(q.key_points || q.correct_answer),
      }));
  
      // Update the state with the formatted questions
      setGeneratedQuestions(formattedQuestions);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Error generating questions. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleGenerateAnswer = async (id) => {
    // Mark the question as loading
    setLoadingQuestionIds((prev) => new Set(prev).add(id));
  
    const questionToGenerate = generatedQuestions.find((q) => q.id === id);
  
    if (!questionToGenerate) {
      console.error("Question not found!");
      setLoadingQuestionIds((prev) => {
        const updated = new Set(prev);
        updated.delete(id); // Remove loading state
        return updated;
      });
      return;
    }
  
    try {
      // Use the metadata snapshot stored for the question
      const questionMetadata = questionToGenerate.metadata;
  
      // Prepare the payload using the question's metadata
      const payload = {
        question: questionToGenerate.text,
        type_of_question: questionMetadata.questionType, // Use stored metadata
        context: questionMetadata.context || null, // Use stored context
        no_of_options: questionToGenerate.options?.length || questionMetadata.no_of_options || null, // Use stored option count
        courseid: questionMetadata.courseId
      };
  
      // Make the API call
      const response = await axios.post(
        `${GENERATION_SERVICE_URL}/api/answers_generation`,
        payload
      );
  
      const { questions } = response.data;
  
      if (questions && questions.length > 0) {
        const updatedQuestion = questions[0]; // Assume only one question is returned
  
        // Determine whether to use `key_points` or `correct_answer`
        const correctAnswer =
          questionMetadata.questionType === "Essay"
            ? updatedQuestion.key_points
            : updatedQuestion.correct_answer;
  
        // Update the state with the new question, options, and correct answer
        setGeneratedQuestions((prev) =>
          prev.map((q) =>
            q.id === id
              ? {
                  ...q,
                  text: updatedQuestion.question || q.text, // Updated question text
                  correctAnswer: correctAnswer || "", // Updated correct answer or key points
                  options: updatedQuestion.options || [], // Updated options for MCQs
                  isAnswerVisible: true, // Show the answer by default
                  hasAnswer: true, // Mark as having a valid answer
                }
              : q
          )
        );
      } else {
        console.error("No valid questions returned from backend.");
      }
    } catch (err) {
      console.error("Error generating answer:", err.message);
      handleNotification("Failed to generate answer. Please try again.", "error");
    } finally {
      // Remove the question from the loading state
      setLoadingQuestionIds((prev) => {
        const updated = new Set(prev);
        updated.delete(id); // Remove loading state
        return updated;
      });
    }
  };
  
  
  
  
  const handleToggleAnswerVisibility = (id) => {
    setGeneratedQuestions((prev) =>
      prev.map((q) =>
        q.id === id ? { ...q, isAnswerVisible: !q.isAnswerVisible } : q
      )
    );
  };  
  
  
  const handleAddToQuestionBank = async (question) => {
    const questionMetadata = question.metadata;
  
    try {
      const payload = {
        course_id: questionMetadata.courseId,
        exam_type: questionMetadata.examType,
        topic: questionMetadata.topic,
        question_text: question.text,
        question_type: questionMetadata.questionType,
        difficulty_level: questionMetadata.difficulty,
        no_of_options: questionMetadata.no_of_options || null,
        correct_answer: question.correctAnswer,
        options: question.options || null,
      };
  
      await axios.post(`${QUESTION_SERVICE_URL}/add-question`, payload);
  
      // Mark the question as "Added"
      setAddedQuestionIds((prev) => new Set([...prev, question.id]));
      handleNotification('Question added to the question bank!', 'success');
  
      // Revert the button to its original state after 2 seconds
      setTimeout(() => {
        setAddedQuestionIds((prev) => {
          const updated = new Set(prev);
          updated.delete(question.id); // Remove the question ID from the "Added" set
          return updated;
        });
      }, 2000); // Adjust timeout duration as needed
    } catch (err) {
      console.error('Failed to add question:', err.message);
      handleNotification('Failed to add question to the database.', 'error');
    }
  };

  const handleNewFileSelection = (e) => {
    const files = Array.from(e.target.files); // Convert FileList to an array
    const newFiles = files.map((file) => ({
      file, // The actual file object
      name: file.name, // File name
      status: 'Pending', // Default status for each file
    }));
  
    // Add the new files to the existing list
    setFileStatuses((prev) => [...prev, ...newFiles]);
  
    // Clear the file input value to allow re-selection of the same file if needed
    e.target.value = '';
  };
  
  
  const ingestFiles = async () => {
    if (!formData.courseId.trim()) {
      // Use the existing notification system to show the error
      handleNotification('Please enter Course ID before ingesting files.', 'error');
      return;
    }
  
    const updatedStatuses = [...fileStatuses]; // Clone current file statuses
  
    const formDataToSend = new FormData();
    formDataToSend.append('courseid', formData.courseId);
  
    updatedStatuses.forEach((fileStatus) => {
      if (fileStatus.status === 'Pending') {
        formDataToSend.append('files', fileStatus.file); // Append files
      }
    });
  
    try {
      const response = await axios.post(
        `${GENERATION_SERVICE_URL}/api/ingest_files/`,
        formDataToSend,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );
  
      // Update statuses based on response
      if (response.status === 200 && response.data.results) {
        const resultMap = response.data.results.reduce((acc, r) => {
          acc[r.filename] = r.status;
          return acc;
        }, {});
  
        updatedStatuses.forEach((fileStatus) => {
          if (resultMap[fileStatus.name]) {
            fileStatus.status = resultMap[fileStatus.name];
          }
        });
        
        //
      } else {
        updatedStatuses.forEach((fileStatus) => {
          if (fileStatus.status === 'Pending') {
            fileStatus.status = 'Failed';
          }
        });
      }
    } catch (error) {
      console.error('Error during file ingestion:', error);
      updatedStatuses.forEach((fileStatus) => {
        if (fileStatus.status === 'Pending') {
          fileStatus.status = 'Failed';
        }
      });
    } finally {
      setFileStatuses(updatedStatuses); // Update statuses
    }
  };  
  
  
  
  const handleEdit = (id) => {
    setGeneratedQuestions((prev) =>
      prev.map((q) => {
        if (q.id === id) {
          if (q.isEditable) {
            // On Save, check for changes
            if (q.text.trim() !== q.originalText.trim()) {
              // Question text has changed
              return {
                ...q,
                isEditable: false,
                originalText: q.text, // Update original text
                correctAnswer: "", // Clear the old answer
                options: [], // Clear old options for MCQs
                isAnswerVisible: false, // Hide answer
                hasAnswer: false, // Mark as needing answer generation
              };
            } else {
              // No changes made
              return { ...q, isEditable: false };
            }
          }
          // Enter edit mode
          return { ...q, isEditable: true };
        }
        return q;
      })
    );
  };
    
  

  return (
    <div className="question-bank-container">
      <Notification
        message={notification.message}
        type={notification.type}
        onClose={() => setNotification({ message: '', type: '' })} // Close the notification
      />
      {/* Left Panel */}
<div className="input-panel">
  <h2 className="panel-title">Generate Questions</h2>
  <form onSubmit={handleSubmit}>
    <div className="metadata-grid">
      <div className="form-group">
        <label className="required-field">Course ID</label>
        <div className="dropdown-container">
          <input
            type="text"
            name="courseId"
            value={formData.courseId}
            onChange={handleInputChange}
            onBlur={handleCourseIdBlur}
            placeholder="Search and select a Course ID"
            className={`input-field ${isCourseIdValid ? '' : 'invalid'}`}
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
        <label>Exam Type</label>
        <select
          name="examType"
          value={formData.examType}
          onChange={handleInputChange}
          className="select-field"
        >
          <option value="Any">Any</option>
          <option value="Mid-semester">Mid-semester</option>
          <option value="Comprehensive">Comprehensive</option>
          <option value="Quiz">Quiz</option>
        </select>
      </div>
    </div>

    <div className="form-group">
      <label className="required-field">Topic</label>
      <input
        type="text"
        name="topic"
        value={formData.topic}
        onChange={handleInputChange}
        placeholder="Enter topic for question generation"
        className="input-field"
        required
      />
    </div>

    <div className="metadata-grid">
      <div className="form-group">
        <label className="required-field">Question Format</label>
        <select
          name="questionFormat"
          value={formData.questionFormat}
          onChange={handleInputChange}
          className="select-field"
        >
          <option value="Non-Numerical/Theoretical">
            Non-Numerical / Theoretical
          </option>
          <option value="Numerical/Coding">Numerical / Coding</option>
        </select>
      </div>
    </div>

    <div className="metadata-grid">
      <div className="form-group">
        <label className="required-field">Question Type</label>
        <select
          name="questionType"
          value={formData.questionType}
          onChange={handleInputChange}
          className="select-field"
          required
        >
          <option value="Multiple Choice Questions">
            Multiple Choice Questions
          </option>
          <option value="True/False">True/False</option>
          <option value="Fill in the blanks">Fill in the blanks</option>
          <option value="Short Answer">Short Answer</option>
          <option value="Essay">Essay</option>
        </select>
      </div>

      <div className="form-group">
        <label className="required-field">Difficulty Level</label>
        <select
          name="difficultyLevel"
          value={formData.difficultyLevel}
          onChange={handleInputChange}
          className="select-field"
          required
        >
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
      </div>

      <div className="form-group">
        <label className="required-field">Number of Questions</label>
        <select
          name="numberOfQuestions"
          value={formData.numberOfQuestions}
          onChange={handleInputChange}
          className="select-field"
          required
        >
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
            <option key={num} value={num}>
              {num}
            </option>
          ))}
        </select>
      </div>

      {formData.questionType === 'Multiple Choice Questions' && (
        <div className="form-group">
          <label className="required-field">Number of Options</label>
          <select
            name="mcqOptionsCount"
            value={formData.mcqOptionsCount}
            onChange={handleInputChange}
            className="select-field"
            required
          >
            {[2, 3, 4, 5, 6].map((num) => (
              <option key={num} value={num}>
                {num}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>

    <div className="form-group">
      <label>
        Example Question <span className="optional-label">(Optional)</span>
      </label>
      <textarea
        name="exampleQuestion"
        value={formData.exampleQuestion}
        onChange={handleInputChange}
        placeholder="Enter an example question to guide the generation..."
        className="input-field context-area"
      />
    </div>

    <div className="new-file-upload-section">
      <h3>Upload and Ingest Files</h3>
      <div className="file-controls">
        <label className="add-files-label">
          Add Files
          <input
  type="file"
  multiple
  accept=".pdf,.docx,.pptx,.txt,.doc"
  onChange={handleNewFileSelection}
  className="file-input"
/>
        </label>
        <button
          type="button"
          className="clear-files-button"
          onClick={() => setFileStatuses([])}
        >
          Clear Files
        </button>
      </div>

      <div className="file-list">
        {fileStatuses.map((file, index) => (
          <div key={index} className="file-item">
            <span>{file.name}</span>
            <span
              className={`file-status ${file.status.toLowerCase()}`}
            >
              {file.status}
            </span>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={ingestFiles}
        className="process-files-button"
        disabled={
          fileStatuses.length === 0 ||
          !fileStatuses.some((file) => file.status === 'Pending')
        }
      >
        Ingest Files
      </button>
    </div>

    {error && <div className="error-message">{error}</div>}

    <button
      type="submit"
      className={`generate-btn ${isLoading ? 'disabled' : ''}`}
      disabled={isLoading}
    >
      {isLoading ? 'Generating Questions...' : 'Generate Questions'}
    </button>
  </form>
</div>

      {/* Right Panel */}
      <div className="output-panel">
  <h2 className="panel-title">Generated Questions</h2>
  {generatedQuestions.length > 0 ? (
    generatedQuestions.map((question, index) => (
      <div key={question.id} className="question-item">
        <div className="question-content">
          <div className="question-number">
            {index + 1}/{generatedQuestions.length}
          </div>

          {question.isEditable ? (
            <div
              contentEditable
              className="question-text editable-question"
              suppressContentEditableWarning
              onBlur={(e) =>
                setGeneratedQuestions((prev) =>
                  prev.map((q) =>
                    q.id === question.id ? { ...q, text: e.target.textContent } : q
                  )
                )
              }
            >
              {question.text}
            </div>
          ) : (
            <div className="question-text">{question.text}</div>
          )}

{question.options && question.options.length > 0 && (
  <div className="options">
    <strong>Options:</strong>
    <div className="options-list">
      {question.options.map((option, i) => (
        <div key={i} className="option-item">
          <span>
            {String.fromCharCode(65 + i)}) {/* A), B), C), etc. */}
          </span>{' '}
          {option}
        </div>
      ))}
    </div>
  </div>
)}

{question.isAnswerVisible && (
  <div className="correct-answer-box">
    <strong>Correct Answer:</strong> {question.correctAnswer}
  </div>
)}


        </div>

        <div className="action-buttons">
          <button
            className="action-btn"
            onClick={() => handleEdit(question.id)}
          >
            {question.isEditable ? 'Save' : 'Edit'}
          </button>
          <button
            className={`action-btn ${loadingQuestionIds.has(question.id) ? 'disabled' : ''}`}
            onClick={() => {
              if (loadingQuestionIds.has(question.id)) return; // Prevent interaction if loading
              if (!question.hasAnswer) {
                handleGenerateAnswer(question.id); // Trigger the backend call
              } else {
                handleToggleAnswerVisibility(question.id); // Handle view/hide toggling
              }
            }}
          >
            {loadingQuestionIds.has(question.id)
              ? 'Generating Answer...'
              : question.isAnswerVisible
              ? 'Hide Answer'
              : question.hasAnswer
              ? 'View Answer'
              : 'Generate Answer'}
          </button>

          <button
            className={`action-btn ${addedQuestionIds.has(question.id) ? 'added' : ''}`}
            onClick={() => handleAddToQuestionBank(question)}
            disabled={addedQuestionIds.has(question.id)}
          >
            {addedQuestionIds.has(question.id) ? '✔ Added' : 'Add to Question Bank'}
          </button>
        </div>
        {!submittedFeedback.has(question.id) && (  // Only show if feedback hasn't been submitted
    <div className="feedback-section">
      <div className="feedback-input-container">
        <textarea
          className="feedback-input"
          placeholder="Provide feedback for this question (optional)"
          value={feedbackData[question.id] || ''}
          onChange={(e) => 
            setFeedbackData(prev => ({
              ...prev,
              [question.id]: e.target.value
            }))
          }
        />
        {feedbackData[question.id]?.trim() && (
          <button
            className="feedback-submit-btn"
            onClick={() => handleFeedbackSubmit(question.id)}
          >
            Submit Feedback
          </button>
        )}
      </div>
    </div>
  )}
      </div>
    ))
  ) : (
    <div className="empty-state">No questions generated yet</div>
  )}
</div>


  </div>
  );
};

export default QuestionBank;