import mammoth from 'mammoth';
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';

// Set the worker source to a CDN or a local file path
GlobalWorkerOptions.workerSrc = '//cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';


/**
 * Extract text from an uploaded file based on its type.
 * Supports .txt, .pdf, and .docx files.
 *
 * @param {File} file - The uploaded file
 * @returns {Promise<string>} - The extracted text as a string
 */
export const extractTextFromFile = async (file) => {
  const fileType = file.name.split('.').pop().toLowerCase();

  switch (fileType) {
    case 'txt':
      return extractFromTxt(file);
    case 'pdf':
      return extractFromPdf(file);
    case 'docx':
      return extractFromDocx(file);
    default:
      throw new Error('Unsupported file type. Please upload .txt, .pdf, or .docx files only.');
  }
};

/**
 * Extract text from a plain text file.
 * @param {File} file - The .txt file
 * @returns {Promise<string>} - The extracted text
 */
const extractFromTxt = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = () => reject(new Error('Error reading text file'));
    reader.readAsText(file);
  });
};


/**
 * Extract text from a PDF file using pdfjs-dist.
 * @param {File} file - The .pdf file
 * @returns {Promise<string>} - The extracted text
 */
const extractFromPdf = async (file) => {
  try {
    // Read the file as an ArrayBuffer
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await getDocument({ data: arrayBuffer }).promise;

    let fullText = '';
    console.log(`PDF Loaded: ${pdf.numPages} pages`);

    // Iterate through pages
    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
      const page = await pdf.getPage(pageNumber);
      const textContent = await page.getTextContent();

      // Extract text from the page
      const pageText = textContent.items.map((item) => item.str).join(' ');
      fullText += pageText + '\n';
    }

    console.log('Extracted Text:', fullText.trim());
    return fullText.trim();
  } catch (error) {
    console.error('Error extracting text from PDF:', error);
    throw new Error('Failed to extract text from PDF.');
  }
};

export default extractFromPdf;

/**
 * Extract text from a Word document using mammoth.
 * @param {File} file - The .docx file
 * @returns {Promise<string>} - The extracted text
 */
const extractFromDocx = async (file) => {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer });
    return result.value.trim();
  } catch (error) {
    throw new Error('Error extracting text from Word document');
  }
};