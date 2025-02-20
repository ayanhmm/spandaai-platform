import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
    const [prompt, setPrompt] = useState("");
    const [model, setModel] = useState("");
    const [modelOne, setModelOne] = useState("");
    const [dataset, setDataset] = useState("");
    const [isRunning, setIsRunning] = useState(false);
    const [evaluationComplete, setEvaluationComplete] = useState(false);
    const [serverError, setServerError] = useState(false);
    const [retryAttempts, setRetryAttempts] = useState(0);

    const EVAL_SERVER_URL = "http://localhost:15500";
    const MAX_RETRY_ATTEMPTS = 5;
    const RETRY_DELAY = 2000; // 2 seconds

    // Check if evaluation server is accessible with automatic retries
    const checkEvalServer = async () => {
        try {
            const response = await fetch(`${EVAL_SERVER_URL}/eval`);
            if (response.ok) {
                setServerError(false);
                setRetryAttempts(0);
            } else {
                throw new Error("Server not ready");
            }
        } catch (error) {
            console.log(`Connection attempt ${retryAttempts + 1} failed`);
            if (retryAttempts < MAX_RETRY_ATTEMPTS) {
                setRetryAttempts(prev => prev + 1);
            } else {
                setServerError(true);
                setRetryAttempts(0);
            }
        }
    };

    // Automatic retry effect
    useEffect(() => {
        if (evaluationComplete && retryAttempts > 0 && retryAttempts <= MAX_RETRY_ATTEMPTS) {
            const timer = setTimeout(() => {
                checkEvalServer();
            }, RETRY_DELAY);
            return () => clearTimeout(timer);
        }
    }, [evaluationComplete, retryAttempts]);

    // Initial check when evaluation completes
    useEffect(() => {
        if (evaluationComplete) {
            setTimeout(() => {
                checkEvalServer();
            }, RETRY_DELAY);
        }
    }, [evaluationComplete]);

    const generateConfig = async () => {
        if (!prompt || !model || !dataset) {
            alert("Please fill all fields.");
            return;
        }

        try {
            const response = await axios.post("http://127.0.0.1:8000/generate-config/", {
                prompt,
                model,
                dataset
            });

            console.log(response.data);
            alert("Config file generated successfully!");
        } catch (error) {
            console.error("Error generating config:", error);
            alert("Failed to generate config.");
        }
    };

    const runEval = async () => {
        if (!prompt || !model || !dataset) {
            alert("Please generate the config first.");
            return;
        }

        setEvaluationComplete(false);
        setServerError(false);
        setRetryAttempts(0);
        setIsRunning(true);

        try {
            const response = await axios.post("http://127.0.0.1:8000/run-eval/");
            console.log("Evaluation response:", response.data);
            
            if (response.data.message === "Evaluation completed successfully, and view is running in the background.") {
                setIsRunning(false);
                setEvaluationComplete(true);
            }
        } catch (error) {
            console.error("Error running evaluation:", error);
            setIsRunning(false);
            setServerError(true);
        }
    };

    const manualRetryConnection = () => {
        setServerError(false);
        checkEvalServer();
    };

    return (
        <div className="app-container">
            <header className="header">
                <h2>PromptFoo Tester</h2>
            </header>
            
            <div className="main-content">
                <div className="left-panel">
                    <div className="input-group">
                        <label>Prompt:</label>
                        <input
                            type="text"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="Enter your prompt"
                        />

                        <label>Evalutator model Name:</label>
                        <input
                            type="text"
                            value={model}
                            onChange={(e) => setModel(e.target.value)}
                            placeholder="Enter model name"
                        />

                        <label>Generator model Name:</label>
                        <input
                            type="text"
                            value={modelOne}
                            onChange={(e) => setModelOne(e.target.value)}
                            placeholder="Enter model name"
                        />

                        <label>URL to your google sheet dataset:</label>
                        <input
                            type="text"
                            value={dataset}
                            onChange={(e) => setDataset(e.target.value)}
                            placeholder="Enter dataset name"
                        />
                    </div>

                    <div className="button-group">
                        <button 
                            className="primary-button"
                            onClick={generateConfig}
                        >
                            Generate Config
                        </button>

                        <button 
                            className="primary-button"
                            onClick={runEval} 
                            disabled={isRunning}
                        >
                            {isRunning ? "Running..." : "Start Evaluation"}
                        </button>
                    </div>
                </div>

                <div className="right-panel">
                    {!evaluationComplete && !isRunning && !serverError && (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-gray-500">Run an evaluation to see the results</p>
                        </div>
                    )}
                    
                    {isRunning && (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-blue-500">Evaluation in progress...</p>
                        </div>
                    )}
                    
                    {evaluationComplete && retryAttempts > 0 && retryAttempts <= MAX_RETRY_ATTEMPTS && (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-blue-500">Connecting to evaluation server... Attempt {retryAttempts}/{MAX_RETRY_ATTEMPTS}</p>
                        </div>
                    )}
                    
                    {serverError && (
                        <div className="flex h-full flex-col items-center justify-center gap-4">
                            <p className="text-red-500">Unable to connect to evaluation server at {EVAL_SERVER_URL}</p>
                            <button 
                                onClick={manualRetryConnection}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                Retry Connection
                            </button>
                        </div>
                    )}
                    
                    {evaluationComplete && !serverError && retryAttempts === 0 && (
                        <iframe
                            src={`${EVAL_SERVER_URL}/eval`}
                            className="w-full h-[600px] rounded-md bg-white"
                            style={{ border: '1px solid #e2e8f0' }}
                            title="Evaluation Results"
                            onError={() => setServerError(true)}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;