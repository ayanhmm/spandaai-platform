import { useState } from 'react';

const GeneratedQuestions = ({ questions, onQuestionUpdate }) => {
  const [editingId, setEditingId] = useState(null);

  const handleEdit = (id) => {
    if (editingId === id) {
      setEditingId(null);
    } else {
      setEditingId(id);
    }
  };

  if (questions.length === 0) {
    return (
      <div>
        <h2 className="panel-title">Generated Questions</h2>
        <p className="empty-message">No questions generated yet</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="panel-title">Generated Questions</h2>
      <div className="questions-container">
        {questions.map((question, index) => (
          <div key={question.id} className="question-item">
            <div className="question-number">
              {index + 1}/{questions.length}
            </div>
            
            <div className="question-box">
              <div className="question-content">
                {editingId === question.id ? (
                  <textarea
                    className="question-text editable"
                    value={question.text}
                    onChange={(e) => {
                      onQuestionUpdate(questions.map(q =>
                        q.id === question.id ? { ...q, text: e.target.value } : q
                      ));
                    }}
                  />
                ) : (
                  <div className="question-text">
                    {question.text}
                  </div>
                )}
              </div>
            </div>

            <div className="action-buttons">
              <button
                className="action-btn"
                onClick={() => handleEdit(question.id)}
              >
                {editingId === question.id ? 'Save' : 'Edit'}
              </button>
              <button className="action-btn">
                Generate Answer
              </button>
              <button className="action-btn">
                Add to Question Bank
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GeneratedQuestions;