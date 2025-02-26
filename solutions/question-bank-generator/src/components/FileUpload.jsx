import { useState } from 'react';

const FileUpload = ({ onTextExtracted }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    try {
      // Mock file processing
      setTimeout(() => {
        const mockExtractedText = `Extracted text from ${file.name}`;
        onTextExtracted(mockExtractedText);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error processing file:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload">
      <label className="file-upload-btn">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        {isLoading ? 'Processing...' : 'Upload File'}
        <input
          type="file"
          accept=".txt,.pdf,.docx"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />
      </label>
    </div>
  );
};

export default FileUpload;