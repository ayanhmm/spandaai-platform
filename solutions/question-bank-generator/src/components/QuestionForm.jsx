import { useState } from 'react';

const QuestionForm = ({ onGenerate }) => {
  const [formData, setFormData] = useState({
    topic: '',
    context: '',
    questionType: 'MCQ',
    difficultyLevel: 'Medium',
    numberOfQuestions: 3,
    mcqOptionsCount: 4,
  });
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.topic && !formData.context) {
      setError('Please provide either a topic or context');
      return;
    }
    onGenerate(formData);
    setError('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="panel-title">Generate Questions</h2>
      
      <div className="form-group">
        <label>Topic</label>
        <input
          type="text"
          name="topic"
          value={formData.topic}
          onChange={handleInputChange}
          className="input-field"
          placeholder="Enter topic for question generation"
        />
      </div>

      <div className="form-group">
        <label>Or Provide Context</label>
        <textarea
          name="context"
          value={formData.context}
          onChange={handleInputChange}
          className="input-field context-area"
          placeholder="Paste your text here or upload a file..."
        />
        <button type="button" className="upload-btn">
          📎 Upload File
          <input
            type="file"
            accept=".txt,.pdf,.docx"
            style={{ display: 'none' }}
          />
        </button>
      </div>

      <div className="form-group">
        <label>Question Type</label>
        <select
          name="questionType"
          value={formData.questionType}
          onChange={handleInputChange}
          className="select-field"
        >
          <option value="MCQ">MCQ</option>
          <option value="Subjective">Subjective</option>
          <option value="Fill in the blanks">Fill in the blanks</option>
          <option value="True/False">True/False</option>
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
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
      </div>

      <div className="form-group">
        <label>Number of Questions</label>
        <select
          name="numberOfQuestions"
          value={formData.numberOfQuestions}
          onChange={handleInputChange}
          className="select-field"
        >
          {[1,2,3,4,5].map(num => (
            <option key={num} value={num}>{num}</option>
          ))}
        </select>
      </div>

      {formData.questionType === 'MCQ' && (
        <div className="form-group">
          <label>Number of Options</label>
          <select
            name="mcqOptionsCount"
            value={formData.mcqOptionsCount}
            onChange={handleInputChange}
            className="select-field"
          >
            {[2,3,4,5,6].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
      
      <button type="submit" className="generate-btn">
        Generate Questions
      </button>
    </form>
  );
};

export default QuestionForm;