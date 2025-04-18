import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys
import time


class AsyncStreamingAPITester:
    """Professional API testing utility for streaming question generation service"""
    
    def __init__(self, api_url, test_image_path):
        self.api_url = api_url
        self.test_image_path = test_image_path
        self.elapsed_time = 0
        self.params = None
        self.all_questions = []
        self.analysis = None
        self.stats = None
        self.events_received = []
    
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
    async def execute_streaming_test(self, params):
        """Execute the streaming API test with given parameters"""
        self.params = params  # Store params for later use
        
        print("\nSending streaming request with parameters:")
        print(json.dumps(params, indent=2))
        
        try:
            start_time = datetime.now()
            
            # Read image file
            with open(self.test_image_path, 'rb') as f:
                image_data = f.read()
            
            # Create form data
            form_data = aiohttp.FormData()
            form_data.add_field('image', 
                            image_data, 
                            filename='image.png',
                            content_type='image/png')
            
            # Add other parameters to form data
            for key, value in params.items():
                if key == 'question_types' and isinstance(value, list):
                    for qt in value:
                        form_data.add_field('question_types', qt)
                elif key == 'use_default_prompt' and isinstance(value, bool):
                    form_data.add_field(key, str(value).lower())
                else:
                    form_data.add_field(key, str(value))
            
            # Set headers for SSE
            headers = {
                "Accept": "text/event-stream"
            }
            
            # Initialize output collector
            output_collector = {
                'analysis': '',
                'questions': [],
                'stats': None,
                'errors': []
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=form_data, headers=headers) as response:
                    if response.status != 200:
                        print(f"ERROR: Request failed with status {response.status}")
                        error_text = await response.text()
                        print(f"Response: {error_text}")
                        return False
                    
                    print("\nStreaming events:")
                    print("----------------")
                    
                    buffer = ""
                    async for line in response.content:
                        line = line.decode('utf-8')
                        buffer += line
                        
                        if "\n\n" in buffer:
                            messages = buffer.split("\n\n")
                            buffer = messages.pop()  # Keep incomplete message in buffer
                            
                            for msg in messages:
                                if msg.startswith("data: "):
                                    data = msg[6:]  # Remove "data: " prefix
                                    try:
                                        event_data = json.loads(data)
                                        event_type = event_data.get("event", "message")
                                        
                                        # Store events for later analysis
                                        self.events_received.append({
                                            "type": event_type,
                                            "data": event_data.get("data", {})
                                        })
                                        
                                        # Process different event types
                                        if event_type == "analysis_complete":
                                            self.analysis = event_data.get("data", {}).get("analysis")
                                            output_collector['analysis'] = self.analysis
                                            print(f"✓ Analysis complete ({len(self.analysis)} chars)")
                                            print(f"\n[Current Analysis Output]:\n{self.analysis}...\n")
                                        
                                        elif event_type == "question_generated":
                                            question_data = event_data.get("data", {})
                                            question_number = question_data.get("question_number")
                                            question_text = question_data.get("question")
                                            
                                            if question_text:
                                                self.all_questions.append(question_text)
                                                output_collector['questions'].append(question_text)
                                                print(f"✓ Question {question_number}: {question_text}...")
                                                print(f"\n[Current Questions List]:")
                                                for i, q in enumerate(output_collector['questions'], 1):
                                                    print(f"{i}. {q}{'...' if len(q) > 70 else ''}")
                                                print()
                                        
                                        elif event_type == "generation_complete":
                                            self.stats = event_data.get("data", {}).get("stats")
                                            output_collector['stats'] = self.stats
                                            final_questions = event_data.get("data", {}).get("questions", [])
                                            print(f"✓ Generation complete - generated {self.stats.get('generated')} questions")
                                            print("\n[Final Statistics]:")
                                            print(json.dumps(self.stats, indent=2))
                                        
                                        elif event_type == "error":
                                            error_message = event_data.get("data")
                                            output_collector['errors'].append(error_message)
                                            print(f"✗ Error: {error_message}")
                                            return False
                                        
                                    except json.JSONDecodeError as e:
                                        print(f"Warning: Couldn't parse data: {data}")
                                        print(f"Error: {str(e)}")
                    
                    # Handle any remaining data in the buffer
                    if buffer.startswith("data: "):
                        try:
                            data = buffer[6:]  # Remove "data: " prefix
                            event_data = json.loads(data)
                            # Process the final event if needed
                        except json.JSONDecodeError:
                            pass
            
            self.elapsed_time = (datetime.now() - start_time).total_seconds()
            
            # Print final collected output
            print("\n\n=== FINAL OUTPUT ===")
            print(f"\nAnalysis ({len(output_collector['analysis'])} chars):")
            print(output_collector['analysis'] + ("..." if len(output_collector['analysis']) > 1000 else ""))
            
            print(f"\nGenerated Questions ({len(output_collector['questions'])}):")
            for i, question in enumerate(output_collector['questions'], 1):
                print(f"{i}. {question}")
            
            if output_collector['stats']:
                print("\nStatistics:")
                print(json.dumps(output_collector['stats'], indent=2))
            
            if output_collector['errors']:
                print("\nErrors encountered:")
                for error in output_collector['errors']:
                    print(f"- {error}")
            
            print(f"\nTotal streaming time: {self.elapsed_time:.2f}s")
            return True
                
        except aiohttp.ClientError as e:
            print(f"ERROR: Connection failed: {str(e)}")
            return False
        except Exception as e:
            print(f"ERROR: Test execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False    
    
    def validate_streaming_results(self):
        """Validate the streaming results"""
        # Check if we received image analysis
        if not self.analysis:
            print("ERROR: Did not receive image analysis")
            return False
        
        # Check if we received questions
        if not self.all_questions:
            print("ERROR: Did not receive any questions")
            return False
        
        # Check if we received stats
        if not self.stats:
            print("ERROR: Did not receive stats")
            return False
        
        # Check question count
        requested_num = self.params['num_questions']
        if isinstance(requested_num, str):
            requested_num = int(requested_num)
            
        if len(self.all_questions) != requested_num:
            print(f"WARNING: Requested {requested_num} questions but received {len(self.all_questions)}")
        
        # Check expected event types
        expected_events = ["analysis_complete", "question_generated", "generation_complete"]
        received_event_types = [event["type"] for event in self.events_received]
        
        for event_type in expected_events:
            if event_type not in received_event_types:
                print(f"WARNING: Did not receive expected event type: {event_type}")
        
        return True
    
    def display_streaming_results(self):
        """Display the streaming test results in a structured format"""
        print("\nSTREAMING TEST RESULTS")
        print("=====================")
        
        # Display statistics
        if self.stats:
            print(f"Questions requested: {self.stats.get('requested', 'N/A')}")
            print(f"Questions generated: {self.stats.get('generated', 'N/A')}")
            print(f"Difficulty: {self.stats.get('difficulty', 'N/A')}")
            print(f"Cognitive level: {self.stats.get('cognitive_level', 'N/A')}")
            print(f"Domain: {self.stats.get('domain', 'N/A')}")
            print(f"Question type: {self.stats.get('question_type', 'N/A')}")
        else:
            print("No stats available")
        
        # Display analysis summary
        if self.analysis:
            print("\nImage Analysis Summary:")
            print(self.analysis[:150] + "..." if len(self.analysis) > 150 else self.analysis)
        else:
            print("\nNo image analysis available")
        
        # Display questions
        if self.all_questions:
            print(f"\nGenerated Questions ({len(self.all_questions)}):")
            for i, question in enumerate(self.all_questions, 1):
                print(f"{i}. {question}")
        
        # Print event timeline
        if os.environ.get("DEBUG_EVENTS") == "1":
            print("\nEvent Timeline:")
            for i, event in enumerate(self.events_received, 1):
                print(f"{i}. {event['type']}: {json.dumps(event['data'])[:100]}...")
        
        return True


async def main_async():
    """Main async streaming test execution function"""
    print("\n===== STREAMING QUESTION GENERATION API TEST =====\n")
    
    # Configuration - UPDATE THESE TO MATCH YOUR ENVIRONMENT
    API_URL = "http://localhost:8014/qbg-image/stream-questions"  # Using the new streaming endpoint
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
    }
    
    # Initialize tester
    tester = AsyncStreamingAPITester(API_URL, TEST_IMAGE_PATH)
    
    # Run test phases
    if not tester.validate_environment():
        return 1
    
    if not await tester.execute_streaming_test(params):
        return 1
    
    if not tester.validate_streaming_results():
        return 1
    
    tester.display_streaming_results()
    
    print("\nStreaming test completed successfully")
    return 0


def main():
    """Entry point that runs the async main function"""
    try:
        import aiohttp
    except ImportError:
        print("Installing required package: aiohttp")
        os.system("pip install aiohttp")
        import aiohttp
        
    return asyncio.run(main_async())


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)