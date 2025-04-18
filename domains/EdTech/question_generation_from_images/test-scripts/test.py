import requests
import json
import os
from datetime import datetime
import sys

class APITester:
    """Professional API testing utility for question generation service"""
    
    def __init__(self, api_url, test_image_path):
        self.api_url = api_url
        self.test_image_path = test_image_path
        self.response = None
        self.elapsed_time = 0
        self.params = None
    
    def validate_environment(self):
        """Validate test prerequisites are met"""
        print(f"Target: {self.api_url}")
        print(f"Using test image: {self.test_image_path}")
        
        if not os.path.isfile(self.test_image_path):
            print(f"ERROR: Test image not found at {self.test_image_path}")
            print("Please create the image or update TEST_IMAGE_PATH variable")
            return False
            
        print("✓ Test image found and readable")
        return True
    
    def execute_test(self, params):
        """Execute the API test with given parameters"""
        self.params = params  # Store params for later use
        
        print("\nSending request with parameters:")
        print(json.dumps(params, indent=2))
        
        try:
            with open(self.test_image_path, 'rb') as image_file:
                # Create properly formatted form data
                form_data = {}
                files = {'image': image_file}
                
                # Convert num_questions to integer
                if 'num_questions' in params:
                    form_data['num_questions'] = int(params['num_questions']) if isinstance(params['num_questions'], str) else params['num_questions']
                
                # Process question_types as a comma-separated list for the API
                if 'question_types' in params:
                    if isinstance(params['question_types'], str):
                        try:
                            # Parse JSON string to list
                            question_types_list = json.loads(params['question_types'])
                            # FastAPI expects a repeated form field for list items
                            for qt in question_types_list:
                                if 'question_types' not in form_data:
                                    form_data['question_types'] = []
                                form_data['question_types'].append(qt)
                        except json.JSONDecodeError:
                            print("WARNING: Could not parse question_types as JSON, skipping")
                    elif isinstance(params['question_types'], list):
                        form_data['question_types'] = params['question_types']
                
                # Pass other parameters directly
                for key in ['difficulty', 'domain', 'custom_prompt', 'cognitive_level']:
                    if key in params and params[key] is not None:
                        form_data[key] = params[key]
                
                # Process boolean use_default_prompt
                if 'use_default_prompt' in params:
                    if isinstance(params['use_default_prompt'], str):
                        value = params['use_default_prompt'].lower() == 'true'
                    else:
                        value = bool(params['use_default_prompt'])
                    form_data['use_default_prompt'] = str(value).lower()
                
                start_time = datetime.now()
                
                # Send request with proper parameters
                self.response = requests.post(
                    self.api_url, 
                    files=files, 
                    data=form_data,
                    timeout=None  # Unlimited timeout
                )
                
                self.elapsed_time = (datetime.now() - start_time).total_seconds()
                
            print(f"Response time: {self.elapsed_time:.2f}s")
            print(f"Status: {self.response.status_code}")
            
            return True
        except requests.exceptions.ConnectionError:
            print("ERROR: Connection failed - Is the server running?")
            return False
        except Exception as e:
            print(f"ERROR: Test execution failed: {str(e)}")
            return False
    
    def validate_response(self):
        """Validate the API response structure and content"""
        if self.response.status_code != 200:
            print(f"ERROR: Request failed with status {self.response.status_code}")
            print(f"Response: {self.response.text}")
            return False
        
        try:
            result = self.response.json()
            print("\nResponse received successfully")
            
            # Check if 'questions' field exists, which is the most important
            if 'questions' not in result:
                print("ERROR: Response doesn't contain 'questions' field")
                print(f"Response keys: {', '.join(result.keys())}")
                return False
                
            # Check questions field
            if not isinstance(result['questions'], list):
                print("ERROR: 'questions' field is not a list")
                return False
            
            # Get num_questions as integer for comparison
            requested_num = self.params['num_questions']
            if isinstance(requested_num, str):
                requested_num = int(requested_num)
                
            if len(result['questions']) != requested_num:
                print(f"WARNING: Requested {requested_num} questions but received {len(result['questions'])}")
            
            # Warn about optional fields that are missing but not fail the test
            expected_fields = ['questions', 'analysis', 'stats']
            missing_fields = [field for field in expected_fields if field not in result]
            
            if missing_fields:
                print(f"WARNING: Some expected fields are missing: {', '.join(missing_fields)}")
            
            # Check if stats contains requested and generated counts, if stats exists
            if 'stats' in result:
                stats = result['stats']
                if 'requested' in stats and 'generated' in stats:
                    if stats['requested'] != stats['generated']:
                        print(f"WARNING: Requested {stats['requested']} questions but generated {stats['generated']}")
            
            return True
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON response")
            print(f"Response: {self.response.text}")
            return False
        except Exception as e:
            print(f"ERROR: Response validation failed: {str(e)}")
            return False
    
    def display_results(self):
        """Display the test results in a structured format"""
        try:
            result = self.response.json()
            
            print("\nTEST RESULTS")
            print("===========")
            
            # Display statistics if available
            if 'stats' in result:
                stats = result['stats']
                print(f"Questions requested: {stats.get('requested', 'N/A')}")
                print(f"Questions generated: {stats.get('generated', 'N/A')}")
                print(f"Difficulty: {stats.get('difficulty', 'N/A')}")
                print(f"Cognitive level: {stats.get('cognitive_level', 'N/A')}")
                print(f"Domain: {stats.get('domain', 'N/A')}")
            else:
                # If stats aren't available, show basic info
                requested_num = self.params['num_questions']
                if isinstance(requested_num, str):
                    requested_num = int(requested_num)
                print(f"Questions requested: {requested_num}")
                print(f"Questions generated: {len(result.get('questions', []))}")
            
            # Display analysis summary if available
            if 'analysis' in result:
                analysis = result['analysis']
                print("\nImage Analysis Summary:")
                print(analysis[:150] + "..." if len(analysis) > 150 else analysis)
            else:
                print("\nNo image analysis provided in response")
            
            # Display questions
            if 'questions' in result and isinstance(result['questions'], list):
                print(f"\nGenerated Questions ({len(result['questions'])}):")
                for i, question in enumerate(result['questions'], 1):
                    # Handle both string questions and dictionary questions
                    if isinstance(question, dict) and 'question' in question:
                        q_text = question['question']
                    else:
                        q_text = str(question)
                    
                    print(f"{i}. {q_text}")
            
            # Print full response for debug if needed
            if os.environ.get("DEBUG_RESPONSE") == "1":
                print("\nFull Response:")
                print(json.dumps(result, indent=2))
            
            return True
        except Exception as e:
            print(f"ERROR: Failed to display results: {str(e)}")
            return False

def main():
    """Main test execution function"""
    print("\n===== QUESTION GENERATION API TEST =====\n")
    
    # Configuration - UPDATE THESE TO MATCH YOUR ENVIRONMENT
    API_URL = "http://localhost:8014/generate-questions"
    TEST_IMAGE_PATH = "question-generation-test-image.png"
    
    # Test parameters aligned with the API specification in the server code
    params = {
        'num_questions': 5,  # Integer as expected by the API
        'difficulty': 'medium',
        'question_types': ["conceptual", "factual"],  # List format
        'use_default_prompt': True,  # Boolean value
        'cognitive_level': 'analyze',
        'numerical': True,
        'user_instructions': "Please generate questions that do not involve very formulaic calculations, but rather, tests application."
        # Optionally add these parameters:
        # 'domain': 'physics',
        # 'custom_prompt': 'Analyze this image in the context of...'
    }
    
    # Initialize tester
    tester = APITester(API_URL, TEST_IMAGE_PATH)
    
    # Run test phases
    if not tester.validate_environment():
        return 1
    
    if not tester.execute_test(params):
        return 1
    
    if not tester.validate_response():
        return 1
    
    tester.display_results()
    
    print("\nTest completed successfully")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)