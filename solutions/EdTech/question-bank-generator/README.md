
# Question Bank Generation App

This is a **React + Vite** application designed for creating and managing question banks and question papers. It provides a user-friendly interface for educators and institutions to generate questions dynamically, filter based on metadata, and organize questions into sections.

---

## Features

### **1. Question Bank Generation**
- Generate questions dynamically by providing:
  - **Course ID** (mandatory)
  - Topic
  - Question Type (MCQ, Subjective, Fill in the blanks, True/False)
  - Difficulty Level
  - Context (optional)
- Dynamically search and select topics based on the entered Course ID.

### **2. Question Paper Creation**
- Fetch questions from the database based on filters like:
  - **Course ID** (mandatory)
  - Topic
  - Question Type
  - Difficulty Level
- Select questions to add them to a question paper.
- Organize selected questions into sections based on their types (e.g., MCQs, Subjective).
- View and manage the questions in a clean, categorized format.

### **3. Interactive UI**
- Live topic search with dropdown functionality.
- Visual indicators for selected questions.
- Fully responsive design for seamless usage across devices.

---

## Prerequisites

- **Node.js** (LTS version recommended)
- **npm** or **yarn** package manager

---

## Installation and Setup

### **1. Clone the Repository**
```bash
git clone https://github.com/spandaai/Question-Bank-Generator_frontend.git
cd Question-Bank-Generator_frontend
```

### **2. Install Dependencies**
Install all required dependencies using npm or yarn:
```bash
npm install
```

### **3. Start the Development Server**
Run the application locally:
```bash
npm run dev
```

This will start the Vite development server. Open your browser and navigate to `http://localhost:5173`.

---

## Folder Structure

```plaintext
.
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/           # Application pages (e.g., QuestionBank, QuestionPaper)
│   ├── styles/          # CSS files for styling
│   ├── utils/           # Utility functions for app logic
│   └── main.jsx         # App entry point
├── .eslintrc.cjs        # ESLint configuration
├── vite.config.js       # Vite configuration
└── README.md            # This file
```

---

## Technologies Used

- **React**: A JavaScript library for building user interfaces.
- **Vite**: A fast and optimized build tool for modern web development.
- **CSS**: Custom styling for enhanced UI/UX.
- **Fetch API**: To communicate with the backend API.

---

## Backend Integration

The app communicates with a **FastAPI** backend to fetch and manage questions. Ensure the backend server is running at `http://127.0.0.1:8000` to avoid connection issues.

---

## Running in Production

To build the application for production:
```bash
npm run build
```

Serve the production build:
```bash
npm run preview
```

---

## Running with Docker

### **Build Docker Image**
To build the Docker image for the app, run:
```bash
docker build -t question-bank-frontend .
```

### **Run Docker Container**
To start the app using Docker, run:
```bash
docker run -d -p 5173:80 --name question-bank-container question-bank-frontend
```

The app will be accessible at `http://localhost:5173`.

### **Stop and Remove Docker Container**
To stop and remove the container, run:
```bash
docker stop question-bank-container
docker rm question-bank-container
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.