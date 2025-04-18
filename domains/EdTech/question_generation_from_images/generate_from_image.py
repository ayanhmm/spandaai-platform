from typing import Dict, List, Optional, AsyncGenerator
import logging
from services.service_client import invoke_llm, analyze_image
from services.model_configs import ModelType
import json

logger = logging.getLogger(__name__)

# In your generate_from_image.py file, modify the stream_educational_questions function:

async def stream_educational_questions(
    image_data: bytes,
    num_questions: int = 5,
    question_types: Optional[List[str]] = None,
    difficulty: str = "master",
    domain: Optional[str] = None,
    user_instructions: Optional[str] = None,
    use_default_prompt: bool = True,
    cognitive_level: str = "analyze",
    numerical: bool = True
) -> AsyncGenerator[str, None]:
    """
    Streams graduate-level questions as they're generated.
    
    Yields SSE formatted events containing analysis results and questions as they're processed.
    """
    # Validate inputs
    difficulty = difficulty if difficulty in ["easy", "medium", "hard", "master"] else "master"
    
    image_prompt = """Describe this image in precise detail, listing only what is visually present. Avoid assumptions or interpretations. Be thorough and exact."""

    # Get image analysis
    try:
        image_analysis = await analyze_image(
            image_data=image_data,
            prompt=image_prompt,
            use_default_prompt=use_default_prompt,
        )
        
        if not image_analysis.get("response"):
            # Format as SSE with data: prefix and double newline
            yield f"data: {json.dumps({'event': 'error', 'data': 'Image analysis failed'})}\n\n"
            return
            
        # Stream the image analysis result immediately
        image_description = image_analysis["response"]
        yield f"data: {json.dumps({'event': 'analysis_complete', 'data': {'analysis': image_description}})}\n\n"
        
        questions = []
        
        # Stream each question as it's generated
        for i in range(num_questions):
            # Build context of previous questions
            context = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(questions)) if questions else "None yet"
            
            # Numerical question specific instructions
            numerical_instructions = ""
            if numerical:
                numerical_instructions = """
                This must be a NUMERICAL problem where:
                - Question requires mathematical calculations or quantitative analysis
                - All necessary numerical values must be extracted from the image
                - Clear computational steps are required to arrive at the answer
                - Calculations must involve more than basic arithmetic (e.g. application of formulas, multi-step processes)
                - The solution pathway is non-trivial and requires mathematical reasoning
                """
            else:
                numerical_instructions = """
                This must be a THEORETICAL question where:
                - Focus is on conceptual understanding and reasoning
                - Question requires analysis of principles, theories, or mechanisms 
                - No numerical calculations are required for the answer
                - The ideal response demonstrates deep understanding of underlying concepts
                - May involve comparison, evaluation, or synthesis of ideas
                """
            
            # Use your sophisticated prompt system
            system_prompt = f"""
            You are a professor designing graduate-level examination questions. Generate ONE sophisticated question with these characteristics:
            
            Academic Level: Masters
            Difficulty: {difficulty}
            Cognitive Level: {cognitive_level}
            Domain: {domain or 'Multidisciplinary'}
            
            {numerical_instructions}
            
            Required Question Attributes:
            1. Requires integration of multiple concepts
            2. Demands evidence-based reasoning
            3. Should test higher-order thinking
            4. Must be answerable from image context
            5. Should reflect current academic discourse
            
            Forbidden Elements:
            - Simple recall questions
            - Yes/no questions
            - Questions with single definitive answers
            - Overly broad questions
            """
            
            user_prompt = f"""
            **Technical Image Description:**
            {image_description}

            Generate exactly ONE new graduate-level question that:
            - Requires advanced {domain or 'disciplinary'} knowledge
            - Demands {cognitive_level} of the material
            - Has {difficulty} complexity
            - Relates directly to the visual content
            - {'Must be a numerical problem requiring calculations based on values visible in the image' if numerical else 'Must be theoretical requiring conceptual understanding rather than calculations'}
                    
            Previous Questions:
            {context}

            {'**Important Instructions:**' if user_instructions else ''}
            {user_instructions or ''}

            Return ONLY the question text with NO numbering, quotes, or additional commentary. Generate a NEW question which is different from the questions already generated.
            """
            
            llm_response = await invoke_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_type=ModelType.ANALYSIS
            )
            
            if llm_response.get("answer"):
                question = llm_response["answer"].strip()
                questions.append(question)
                
                # Stream each question as it's generated - with proper SSE format
                yield f"data: {json.dumps({'event': 'question_generated', 'data': {'question_number': len(questions), 'question': question}})}\n\n"
        
        # Send final stats - with proper SSE format
        yield f"data: {json.dumps({'event': 'generation_complete', 'data': {'stats': {'requested': num_questions, 'generated': len(questions), 'difficulty': difficulty, 'cognitive_level': cognitive_level, 'domain': domain, 'question_type': 'numerical' if numerical else 'theoretical'}, 'questions': questions}})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"


async def generate_educational_questions(
    image_data: bytes,
    num_questions: int = 5,
    question_types: Optional[List[str]] = None,
    difficulty: str = "master",
    domain: Optional[str] = None,
    user_instructions: Optional[str] = None,
    use_default_prompt: bool = True,
    cognitive_level: str = "analyze",
    numerical: bool = True
) -> Dict[str, List[str]]:
    """
    Generate graduate-level questions using the enhanced prompt system.
    
    Args:
        image_data: Raw image bytes
        num_questions: Number of questions to generate
        question_types: List of question types to generate
        difficulty: Question difficulty level (easy, medium, hard, master)
        domain: Academic domain for questions
        custom_prompt: Optional custom prompt for image analysis
        use_default_prompt: Whether to use default prompt for image analysis
        cognitive_level: Bloom's taxonomy level (remember, understand, apply, analyze, evaluate, create)
        numerical: Whether to generate numerical problem-solving questions
        
    Returns:
        Dictionary with generated questions, image analysis, and stats
    """
    # Validate inputs
    difficulty = difficulty if difficulty in ["easy", "medium", "hard", "master"] else "master"
    image_prompt = """Describe this image in precise detail, listing only what is visually present. Avoid assumptions or interpretations. Be thorough and exact."""

    # Get image analysis
    image_analysis = await analyze_image(
        image_data=image_data,
        prompt=image_prompt,
        use_default_prompt=use_default_prompt,
    )
    
    if not image_analysis.get("response"):
        return {"error": "Image analysis failed"}
    
    questions = []
    image_description = image_analysis["response"]
    
    for i in range(num_questions):
        # Build context of previous questions
        context = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(questions)) if questions else "None yet"
        
        # Numerical question specific instructions
        numerical_instructions = ""
        if numerical:
            numerical_instructions = """
            This must be a NUMERICAL problem where:
            - Question requires mathematical calculations or quantitative analysis
            - All necessary numerical values must be extracted from the image
            - Clear computational steps are required to arrive at the answer
            - Calculations must involve more than basic arithmetic (e.g. application of formulas, multi-step processes)
            - The solution pathway is non-trivial and requires mathematical reasoning
            """
        else:
            numerical_instructions = """
            This must be a THEORETICAL question where:
            - Focus is on conceptual understanding and reasoning
            - Question requires analysis of principles, theories, or mechanisms 
            - No numerical calculations are required for the answer
            - The ideal response demonstrates deep understanding of underlying concepts
            - May involve comparison, evaluation, or synthesis of ideas
            """
        
        # Use your sophisticated prompt system
        system_prompt = f"""
        You are a professor designing graduate-level examination questions. Generate ONE sophisticated question with these characteristics:
        
        Academic Level: Masters
        Difficulty: {difficulty}
        Cognitive Level: {cognitive_level}
        Domain: {domain or 'Multidisciplinary'}
        
        {numerical_instructions}
        
        Required Question Attributes:
        1. Requires integration of multiple concepts
        2. Demands evidence-based reasoning
        3. Should test higher-order thinking
        4. Must be answerable from image context
        5. Should reflect current academic discourse
        
        Forbidden Elements:
        - Simple recall questions
        - Yes/no questions
        - Questions with single definitive answers
        - Overly broad questions
        """
        
        user_prompt = f"""
        **Technical Image Description:**
        {image_description}

        Generate exactly ONE new graduate-level question that:
        - Requires advanced {domain or 'disciplinary'} knowledge
        - Demands {cognitive_level} of the material
        - Has {difficulty} complexity
        - Relates directly to the visual content
        - {'Must be a numerical problem requiring calculations based on values visible in the image' if numerical else 'Must be theoretical requiring conceptual understanding rather than calculations'}
                
        Previous Questions:
        {context}

        {'**Important Instructions:**' if user_instructions else ''}
        {user_instructions or ''}

        Return ONLY the question text with NO numbering, quotes, or additional commentary. Generate a NEW question which is different from the questions already generated.
        """
        
        llm_response = await invoke_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_type=ModelType.ANALYSIS
        )
        
        if llm_response.get("answer"):
            questions.append(llm_response["answer"].strip())
    
    return {
        "questions": questions,
        "analysis": image_description,
        "stats": {
            "requested": num_questions,
            "generated": len(questions),
            "difficulty": difficulty,
            "cognitive_level": cognitive_level,
            "domain": domain,
            "question_type": "numerical" if numerical else "theoretical"
        }
    }