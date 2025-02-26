import React,{ useState } from "react";
import "../styles/questionPaper.css";
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from "docx";
//import { DOMStandardFontDataFactory } from "pdfjs-dist/types/src/display/standard_fontdata_factory";
const API_BASE_URL = "http://localhost:8090/db";

const SelectedFilters = ({ filters, onEdit }) => (
  <div className="selected-filters">
    <div className="filters-row">
      <div className="filter-item">
        <span className="filter-label">Course ID:</span>
        <span className="filter-value">{filters.courseId}</span>
      </div>
      <div className="filter-item">
        <span className="filter-label">Question Type:</span>
        <span className="filter-value">{filters.questionType}</span>
      </div>
      <div className="filter-item">
        <span className="filter-label">Difficulty:</span>
        <span className="filter-value">{filters.difficultyLevel}</span>
      </div>
      <button className="edit-filters" onClick={onEdit}>
        Edit
      </button>
    </div>
    <div className="filters-row">
      <div className="filter-item">
        <span className="filter-label">Topic:</span>
        <span className="filter-value">{filters.topic}</span>
      </div>
    </div>
  </div>
);

const QuestionPaper = () => {
  const [formData, setFormData] = useState({
    courseId: "",
    topic: "Any Topic",
    questionType: "Any",
    difficultyLevel: "Any",
  });

  const [showTopicsDropdown, setShowTopicsDropdown] = useState(false);
  const [isTopicInputFocused, setIsTopicInputFocused] = useState(false);
  const [topicSearchText, setTopicSearchText] = useState("");
  const [filteredTopics, setFilteredTopics] = useState([]);
  const [fetchedQuestions, setFetchedQuestions] = useState([]);
  const [isQuestionsFetched, setIsQuestionsFetched] = useState(false);
  const [sectionMarks, setSectionMarks] = useState({});
  const [questionMarks, setQuestionMarks] = useState({});
  const [questionSections, setQuestionSections] = useState({});
  const [includePreviousYear, setIncludePreviousYear] = useState(false);
  const [previousYearQuestions, setPreviousYearQuestions] = useState([]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleTopicInputFocus = () => {
    setIsTopicInputFocused(true);
    setShowTopicsDropdown(true);
    setTopicSearchText("");
  };

  const handleTopicInputBlur = () => {
    setTimeout(() => {
      setIsTopicInputFocused(false);
      if (!formData.topic || formData.topic === "") {
        setFormData((prev) => ({ ...prev, topic: "Any Topic" }));
      }
      setShowTopicsDropdown(false);
    }, 200);
  };

  const calculateSectionTotal = (sectionType) => {
    const questions = questionSections[sectionType] || [];
    return {
      total: questions.reduce((sum, question) => sum + (questionMarks[question.id] || 0), 0),
      numQuestions: questions.length
    };
  };

  const handleTopicSearch = async (value) => {
    setTopicSearchText(value);
    if (!formData.courseId.trim()) {
      alert("Please enter a Course ID before searching for topics.");
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/fetch-topics?course_id=${formData.courseId}&search_text=${value}`
      );
      const data = await response.json();
      setFilteredTopics(["Any Topic", ...(data.topics || [])]); // Ensure "Any Topic" is always included
      setShowTopicsDropdown(true);
    } catch (err) {
      console.error("Error fetching topics:", err);
    }
  };

  const handleTopicSelect = (topicName) => {
    setFormData((prev) => ({ ...prev, topic: topicName })); // Update the formData with the selected topic
    setTopicSearchText(topicName); // Reflect the selected topic in the input field
    setShowTopicsDropdown(false); // Hide the dropdown after selection
    setIsTopicInputFocused(false); // Ensure the input loses its focused state
  };

  const handleQuestionMarksChange = (questionId, value) => {
    const numValue = parseInt(value) || 0;
    setQuestionMarks(prev => ({
      ...prev,
      [questionId]: numValue
    }));
  };

  const calculateGrandTotal = () => {
    return Object.keys(questionSections).reduce((total, section) => {
      return total + calculateSectionTotal(section).total;
    }, 0);
  };

  const handleFetchQuestions = async (e) => {
    e.preventDefault();
    console.log("Fetching questions...");
  
    if (!formData.courseId.trim()) {
      alert("Course ID is required!");
      return;
    }
  
    const params = new URLSearchParams({
      course_id: formData.courseId,
      ...(formData.topic !== "Any Topic" && { topic: formData.topic }),
      ...(formData.questionType !== "Any" && { question_type: formData.questionType }),
      ...(formData.difficultyLevel !== "Any" && { difficulty_level: formData.difficultyLevel }),
      include_previous_year: includePreviousYear,
    });
  
    try {
      const response = await fetch(`${API_BASE_URL}/fetch-questions?${params}`);
      const data = await response.json();
      console.log("Fetched data:", data); // Debugging line
  
      // Process fetched questions
      if (data.questions || data.previous_year_questions) {
        // Ensure all questions have images as arrays
        const processedQuestions = (data.questions || []).map((question) => ({
          ...question,
          question_images: question.question_images || [], // Ensure images are an array
        }));
  
        const processedPreviousYearQuestions = (data.previous_year_questions || []).map(
          (question) => ({
            ...question,
            question_images: question.question_images || [], // Ensure images are an array
          })
        );
  
        setFetchedQuestions(processedQuestions);
        setPreviousYearQuestions(processedPreviousYearQuestions);
        setIsQuestionsFetched(true);
      } else {
        setFetchedQuestions([]);
        setPreviousYearQuestions([]);
        alert("No questions found for the provided filters.");
      }
    } catch (err) {
      console.error("Error fetching questions:", err);
      alert("Failed to fetch questions. Please try again later.");
    }
  };
  


  const handleDownload = async () => {
    if (Object.keys(questionSections).length === 0) {
      alert("No questions selected for download!");
      return;
    }
  
    // Filter sections to include only those with questions
    const filteredSections = Object.keys(questionSections)
      .filter((section) => questionSections[section].length > 0)
      .reduce((acc, section) => {
        acc[section] = questionSections[section];
        return acc;
      }, {});
  
    // Ensure there is at least one section with questions
    if (Object.keys(filteredSections).length === 0) {
      alert("No questions selected for download!");
      return;
    }
  
    // Calculate grand total
    const grandTotal = calculateGrandTotal();
  
    // Create the DOCX document
    const doc = new Document({
      sections: [
        {
          children: [
            // Header Section
            new Paragraph({
              children: [
                new TextRun({
                  text: "Birla Institute of Technology & Science, Pilani",
                  bold: true,
                  size: 28,
                }),
              ],
              alignment: "center",
            }),
            new Paragraph({
              children: [
                new TextRun({
                  text: "Work-Integrated Learning Programmes Division",
                  bold: true,
                  size: 24,
                }),
              ],
              alignment: "center",
              spacing: { after: 400 },
            }),
            new Paragraph({
              text: "<Enter which semester>",
              bold: true,
              size: 24,
              alignment: "center",
            }),
            new Paragraph({
              text: "<Enter type of test>",
              bold: true,
              size: 24,
              alignment: "center",
              spacing: { after: 400 },
            }),
  
            // Total Marks
            new Paragraph({
              children: [
                new TextRun({
                  text: `Maximum Marks: ${grandTotal}`,
                  bold: true,
                  size: 24,
                }),
              ],
              alignment: "right",
              spacing: { after: 400 },
            }),
  
            // Metadata Section
            ...[
              "Course No.        : <Enter Course No.>",
              "Course Title      : <Enter Course Title>",
              "Nature of Exam    : <Enter Nature of Exam>",
              "Weightage         : <Enter Weightage>",
              "Duration         : <Enter Duration>",
              "Date of Exam      : <Enter Date>",
            ].map((text) =>
              new Paragraph({
                text,
                size: 22,
              })
            ),
  
            // Note Section
            new Paragraph({
              text: "Note:",
              bold: true,
              size: 22,
              spacing: { before: 400, after: 200 },
            }),
            ...[
              "Please follow all the Instructions to Candidates given on the cover page of the answer book.",
              "All parts of a question should be answered consecutively. Each answer should start from a fresh page.",
              "Assumptions made if any, should be stated clearly at the beginning of your answer.",
            ].map((text, index) =>
              new Paragraph({
                text: `${index + 1}. ${text}`,
                size: 20,
              })
            ),
  
            // Main Sections for Questions
            ...Object.keys(filteredSections).flatMap((section, index) => {
              const { total } = calculateSectionTotal(section);
              return [
                // Section Header with marks information
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `${index + 1}. ${section} (Total Marks: ${total})`,
                      bold: true,
                      size: 26,
                    }),
                  ],
                  spacing: { before: 400, after: 200 },
                }),
                // Questions in Section
                ...filteredSections[section].flatMap((question, questionIndex) => [
                  // Question Text with marks
                  new Paragraph({
                    children: [
                      new TextRun({
                        text: `Q.${questionIndex + 1}. `,
                        bold: true,
                        size: 20,
                      }),
                      new TextRun({
                        text: `[${questionMarks[question.id] || 0} Marks] `,
                        bold: true,
                        size: 20,
                      }),
                      new TextRun({
                        text: question.question_text,
                        size: 20,
                      }),
                    ],
                    spacing: { after: 100 },
                  }),
                  // MCQ Options (if any)
                  ...(question.question_type === "Multiple Choice Questions"
                    ? [
                        ...question.options.map((option, optionIndex) =>
                          new Paragraph({
                            text: `${String.fromCharCode(65 + optionIndex)}. ${option}`,
                            size: 20,
                            spacing: { after: 50 },
                          })
                        ),
                        new Paragraph({
                          text: "",
                          spacing: { after: 200 },
                        }),
                      ]
                    : [
                        new Paragraph({
                          text: "",
                          spacing: { after: 200 },
                        }),
                      ]),
                ]),
              ];
            }),
          ],
        },
      ],
    });
  
    try {
      // Generate and download the DOCX
      const blob = await Packer.toBlob(doc);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Question_Paper.docx";
      a.click();
    } catch (error) {
      console.error("Error generating Word document:", error);
      alert("Failed to generate Word document. Please check the console for details.");
    }
  };
  

  const handleQuestionSelect = (question) => {
    setQuestionSections((prev) => {
      const section = question.question_type;
  
      // Clone the current section or initialize it
      const updatedSection = prev[section] ? [...prev[section]] : [];
  
      // Check if the question already exists in the section
      const exists = updatedSection.find((q) => q.id === question.id);
  
      if (exists) {
        // If the question exists, remove it from the section
        const filteredSection = updatedSection.filter((q) => q.id !== question.id);
  
        // Remove the section entirely if no questions are left
        const updatedSections = { ...prev };
        if (filteredSection.length === 0) {
          delete updatedSections[section];
        } else {
          updatedSections[section] = filteredSection;
        }
  
        return updatedSections;
      } else {
        // If the question does not exist, add it to the section
        return {
          ...prev,
          [section]: [...updatedSection, question],
        };
      }
    });
  };
  
  

  const handleMarksChange = (section, value) => {
    const numValue = parseInt(value) || 0;
    setSectionMarks(prev => ({
      ...prev,
      [section]: numValue
    }));
  };

  const handleRemoveQuestion = async (questionId, isPreviousYear = false) => {
    const confirmRemoval = window.confirm(
      "Are you sure you want to remove this question? This action cannot be undone."
    );
    if (!confirmRemoval) return;
  
    try {
      // Determine the API endpoint based on the question type
      const endpoint = isPreviousYear
        ? `${API_BASE_URL}/remove-previous-year-question/${questionId}`
        : `${API_BASE_URL}/remove-question/${questionId}`;
  
      const response = await fetch(endpoint, {
        method: isPreviousYear ? "DELETE" : "PUT",
      });
  
      if (!response.ok) {
        throw new Error("Failed to remove question.");
      }
  
      // Update the left panel (fetchedQuestions)
      setFetchedQuestions((prev) => prev.filter((q) => q.id !== questionId));
  
      // Update the right panel (selectedQuestions)
      setQuestionSections((prev) => {
        const updatedSections = { ...prev };
        Object.keys(updatedSections).forEach((section) => {
          updatedSections[section] = updatedSections[section].filter(
            (q) => q.id !== questionId
          );
          // Remove empty sections
          if (updatedSections[section].length === 0) {
            delete updatedSections[section];
          }
        });
        return updatedSections;
      });
  
      alert("Question removed successfully.");
    } catch (err) {
      console.error(err);
      alert("Failed to remove the question. Please try again.");
    }
  };
  
   

  const isQuestionSelected = (questionId) => {
    return Object.values(questionSections).some((section) =>
      section.find((q) => q.id === questionId)
    );
  };

  const renderQuestions = () => {
    const hasFetchedQuestions = fetchedQuestions.length > 0;
    const hasPreviousYearQuestions = previousYearQuestions.length > 0;
  
    if (!hasFetchedQuestions && !hasPreviousYearQuestions) {
      return <div className="empty-state">No questions match the current filters.</div>;
    }
  
    return (
      <>
        {/* Current Questions */}
        {hasFetchedQuestions && (
          <>
            <h3 className="section-title">Current Questions</h3>
            {fetchedQuestions.map((question) => renderQuestion(question))}
          </>
        )}
  
        {/* Previous Year Questions */}
        {hasPreviousYearQuestions && (
          <>
            <h3 className="section-title">Previous Year Questions</h3>
            {previousYearQuestions.map((question) => renderQuestion(question,true))}
          </>
        )}
      </>
    );
  };
  

  const renderQuestion = (question, isPreviousYear = false) => (
    <div
      key={question.id}
      className={`question-item ${isQuestionSelected(question.id) ? "selected" : ""}`}
      onClick={() => handleQuestionSelect(question)} // Allow toggling selection
    >
      <div className="question-content">
        {/* Question Text */}
        <div className="question-text">{question.question_text}</div>
  
        {/* Display Multiple Images */}
        {question.question_images && question.question_images.length > 0 && (
          <div className="question-images">
            {question.question_images.map((image, index) => (
              <img
                key={index}
                src={`data:image/jpeg;base64,${image}`}
                alt={`Question Image ${index + 1}`}
                className="image-preview"
              />
            ))}
          </div>
        )}
  
        {/* MCQ Options */}
        {question.question_type === "Multiple Choice Questions" && question.options && (
          <ul className="options-list">
            {question.options.map((option, index) => (
              <li key={index} className="option-item">
                {String.fromCharCode(65 + index)}: {option}
              </li>
            ))}
          </ul>
        )}
  
        {/* Metadata Tags */}
        {question.metadata_tags && question.metadata_tags.length > 0 && (
          <div className="tags">
            {question.metadata_tags.map((tag, index) => (
              <div key={index} className="tag-item">
                {tag.label}: {tag.value}
              </div>
            ))}
          </div>
        )}
  
        {/* Remove Button */}
        <button
          className="remove-btn"
          onClick={(e) => {
            e.stopPropagation(); // Prevent triggering the select/deselect logic
            handleRemoveQuestion(question.id, isPreviousYear);
          }}
        >
          Remove Question from the Bank
        </button>
      </div>
    </div>
  );
  
  
  
  
  const renderSelectedQuestions = () => {
    if (Object.keys(questionSections).length === 0) {
      return <div className="empty-state">No questions selected</div>;
    }
  
    return (
      <>
        <div className="grand-total">Total Marks: {calculateGrandTotal()}</div>
        {Object.keys(questionSections).map((section) => {
          if (questionSections[section].length === 0) return null;
  
          const { total, numQuestions } = calculateSectionTotal(section);
  
          return (
            <div key={section} className="question-section">
              <div className="section-header">
                <h3 className="section-title">
                  {section} ({numQuestions} questions)
                </h3>
                <span className="total-marks">Section Total: {total} marks</span>
              </div>
              {questionSections[section].map((question, index) => (
                <div key={question.id} className="selected-question">
                  {/* Question Header with Marks Input */}
                  <div className="question-header">
                    <div className="question-number">{index + 1}.</div>
                    <div className="marks-input-container">
                      <input
                        type="number"
                        min="0"
                        value={questionMarks[question.id] || ""}
                        onChange={(e) =>
                          handleQuestionMarksChange(question.id, e.target.value)
                        }
                        className="marks-input"
                        placeholder="Marks"
                      />
                    </div>
                  </div>
  
                  {/* Question Text */}
                  <div className="question-text">{question.question_text}</div>
  
                  {/* MCQ Options for Normal Questions */}
                  {question.question_type === "Multiple Choice Questions" && question.options && (
                    <ul className="options-list">
                      {question.options.map((option, index) => (
                        <li key={index} className="option-item">
                          {String.fromCharCode(65 + index)}: {option}
                        </li>
                      ))}
                    </ul>
                  )}
  
                  {/* Images for Questions */}
                  {question.question_images && question.question_images.length > 0 && (
                    <div className="question-images">
                      {question.question_images.map((image, imgIndex) => (
                        <img
                          key={imgIndex}
                          src={`data:image/jpeg;base64,${image}`}
                          alt={`Question Image ${imgIndex + 1}`}
                          className="image-preview"
                        />
                      ))}
                    </div>
                  )}
  
                  {/* Metadata Tags */}
                  <div className="tags">
                    {question.metadata_tags.map((tag, tagIndex) => (
                      <div key={tagIndex} className="tag-item">
                        {tag.label}: {tag.value}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </>
    );
  };
  
  
  

  return (
    <div className="question-paper-container">
      <div className="left-panel">
  {!isQuestionsFetched ? (
    <form onSubmit={handleFetchQuestions} className="fetch-form">
      <h2 className="panel-title">Create Question Paper</h2>
      <div className="form-group">
        <label className="required-field">Course ID</label>
        <input
          type="text"
          name="courseId"
          value={formData.courseId}
          onChange={handleInputChange}
          className="input-field"
          placeholder="Enter Course ID"
          required
        />
      </div>
      <div className="form-group">
        <label>Topic</label>
        <div className="topic-search">
          <input
            type="text"
            value={isTopicInputFocused ? topicSearchText : formData.topic}
            onChange={(e) => handleTopicSearch(e.target.value)}
            onFocus={handleTopicInputFocus}
            onBlur={handleTopicInputBlur}
            className="input-field"
            placeholder="Search topics..."
          />
          {showTopicsDropdown && (
            <div className="topics-dropdown">
              {filteredTopics.length > 0 ? (
                filteredTopics.map((topic, index) => (
                  <div
                    key={index}
                    className="topic-option"
                    onClick={() => handleTopicSelect(topic)}
                  >
                    {topic}
                  </div>
                ))
              ) : (
                <div className="topic-option no-results">No matching topics found</div>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="form-group">
        <label>Question Type</label>
        <select
          name="questionType"
          value={formData.questionType}
          onChange={handleInputChange}
          className="select-field"
        >
          <option value="Any">Any</option>
          <option value="Multiple Choice Questions">Multiple Choice Questions</option>
          <option value="True/False">True/False</option>
          <option value="Fill in the blanks">Fill in the blanks</option>
          <option value="Short Answer">Short Answer</option>
          <option value="Essay">Essay</option>
        </select>
      </div>
      <div className="form-group">
        <label>Difficulty Level</label>
        <select
          name="difficultyLevel"
          value={formData.difficultyLevel}
          onChange={handleInputChange}
          className="select-field"
        >
          <option value="Any">Any</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
      </div>
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={includePreviousYear}
            onChange={(e) => setIncludePreviousYear(e.target.checked)}
          />
           Include Previous Year Questions
        </label>
      </div>
      <button type="submit" className="fetch-btn">
        Fetch Questions
      </button>
    </form>
  ) : (
    <div>
      <SelectedFilters filters={formData} onEdit={() => setIsQuestionsFetched(false)} />
      <div className="questions-list">
        <h2 className="panel-title">Available Questions</h2>
        {renderQuestions()} {/* Call the renderQuestions function here */}
      </div>
    </div>
  )}
</div>
      <div className="right-panel">
        <h2 className="panel-title">Question Paper</h2>
        {renderSelectedQuestions()}
        <button className="download-btn" onClick={handleDownload}>
          Download Question Paper
        </button>
      </div>
    </div>
  );
}
  
  
export default QuestionPaper;