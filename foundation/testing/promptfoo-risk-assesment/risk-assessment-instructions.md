**LLM Red Teaming Setup Using Promptfoo**

## **Project Initialization**
To set up a red teaming project for your LLM application using Promptfoo, follow these steps:

### **Step 1: Initialize the Project**
Use one of the following package managers to install and initialize the Promptfoo red teaming tool:
```sh
npx promptfoo@latest redteam setup
```
This command launches a web UI that will guide you through configuring your red teaming project.

### **Step 2: Provide Application Details**
- Fill out details about your target application.
- Ensure that the **Purpose** field is completed with a clear description of your application.
- For a quick setup, you can load an example configuration by clicking **"Load Example"**.

## **Configure the Target**
Since the Promptfoo scanner runs locally, it can attack any accessible endpoint, including:
- Local or remote models
- HTTP endpoints
- Custom applications

## **Select Plugins**
- Plugins generate adversarial test inputs.
- Choose from predefined sets or select individual plugins.
- The **Default** preset is recommended for general use.

## **Select Attack Strategies**
- Attack strategies define how test cases are wrapped into specific adversarial patterns.
- These enhance jailbreak attempts and injection vulnerabilities.

## **Review and Save Configuration**
- Download the generated configuration file (`promptfooconfig.yaml`).
- Navigate to the saved file’s directory and run:
```sh
promptfoo redteam run
```
Alternatively, skip the UI setup and initialize via CLI:
```sh
promptfoo redteam init --no-gui
```

## **Run the Scan**
Execute the adversarial evaluation with:
```sh
npx promptfoo@latest redteam run
```
- This generates a variety of adversarial test cases and stores them in `redteam.yaml`.
- It then runs these test cases against the target.

## **View the Results**
To analyze vulnerabilities, generate a report with:
```sh
npx promptfoo@latest redteam report
```
This report provides insights into:
- **Vulnerability categories**: Prompt injections, context poisoning, and other risks.
- **Severity levels**: Impact analysis of vulnerabilities.
- **Logs**: Raw input/output of detected vulnerabilities.
- **Mitigation suggestions**: Recommendations for securing the system.

## **Common Target Configurations**
### **1. Attacking an API Endpoint**
Modify `promptfooconfig.yaml` to define the API target:
```yaml
targets:
  - id: https
    label: 'travel-agent-agent'
    config:
      url: 'https://example.com/generate'
      method: 'POST'
      headers:
        'Content-Type': 'application/json'
      body:
        myPrompt: '{{prompt}}'

purpose: 'The user is a budget traveler looking for the best deals. The system is a travel agent that helps the user plan their trip. The user is anonymous and should not be able to access any information about other users, employees, or other individuals.'
```
- The `label` field is essential for tracking test results across multiple scans.
- Clearly defining the `purpose` improves test case accuracy.

### **2. Testing Specific Prompts and Models**
If no live API is available, configure the YAML to test LLM prompts directly:
```yaml
prompts:
  - 'Act as a travel agent and help the user plan their trip. User query: {{query}}'

targets:
  - id: openai:gpt-4o-mini
    label: 'travel-agent-mini'
```
- Supports various LLM providers (OpenAI, Hugging Face, local models, etc.).

### **3. Direct Integration with Your App**
Promptfoo can directly interact with applications via:
- **HTTP requests to your API**
- **Custom Python scripts for precise control**
- **JavaScript, executable files, local LLM providers, and agent workflows**

## **Continuous Improvement**
- Regularly update and run red teaming scans to enhance security.
- Implement suggested mitigations and refine application defenses.
- Adjust configurations based on evolving threats.

By following these steps, you can systematically test and improve the robustness of your LLM applications against adversarial threats.

