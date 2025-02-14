from typing import Dict, List, Optional
import random

from spanda_domains.services.EdTech.microservices.qa_generation.filters import context_relevance_filter
from spanda_domains.services.EdTech.shared.config.model_configs import ModelType
from spanda_domains.services.EdTech.shared.platform_client.service_client import invoke_llm
from spanda_domains.services.EdTech.microservices.qa_generation.spanda_types import QueryRequest
from spanda_domains.services.EdTech.shared.platform_client.rag_client import call_spanda_retrieve


async def process_context(context_payload: Dict, query_context: Optional[str]) -> Dict:
    retrieve_response = await call_spanda_retrieve(context_payload)
    retrieved_context = retrieve_response.get('context', '')
    documents = retrieve_response.get('documents', [])

    document_titles = [doc['title'] for doc in documents]
    titles_string = ', '.join(document_titles) if documents else "No source documents"

    filtered_context = await context_relevance_filter(context_payload["query"], retrieved_context)

    final_combined_context = f"{filtered_context.strip()} {query_context.strip()}" if query_context else filtered_context.strip()

    return {
        "filtered_context": final_combined_context,
        "titles_string": titles_string
    }


def tag_spanda_question(question: str, correct_answer: str, question_type: str, all_options: list = None) -> dict:
    """
    Tag the question with its correct answer and options in a structured format based on the question type.
    """
    if question_type.lower() == "multiple choice questions":
        return {
            "type": "MCQ",
            "question": question,
            "options": all_options,
            "correct_answer": correct_answer
        }

    elif question_type.lower() == "true/false":
        return {
            "type": "True/False",
            "question": question,
            "correct_answer": correct_answer
        }

    elif question_type.lower() == "fill in the blanks":
        return {
            "type": "Fill in the Blanks",
            "question": question,
            "correct_answer": correct_answer
        }

    elif question_type.lower() == "short answer":
        return {
            "type": "Short Answer",
            "question": question,
            "correct_answer": correct_answer
        }

    elif question_type.lower() == "essay":
        return {
            "type": "Essay",
            "question": question,
            "key_points": correct_answer
        }

    else:
        raise ValueError("Unknown question type")


async def isCodeBased(topic: str) -> str:
    """
    Determines if a given topic is related to coding, computer science, or software development.

    Args:
        topic (str): The topic to classify.

    Returns:
        str: 'Yes' if the topic is related to coding/CS, 'No' otherwise.
    """
    system_prompt = """You are a precise topic classifier specialized in identifying coding and computer science related subjects.

Guidelines for classification:
- Consider topics related to:
    - Programming languages and frameworks (e.g., Python, JavaScript, React.js, Angular, Django, TensorFlow)
    - Software development practices (e.g., Agile, CI/CD, Version Control, TDD)
    - Computer science concepts and algorithms (e.g., Sorting Algorithms, Big-O Notation, Machine Learning, Cryptography)
    - Data structures and databases (e.g., Linked Lists, HashMaps, SQL, NoSQL)
    - System architecture and design (e.g., Microservices, Monolithic Architecture, REST APIs, MVC Pattern)
    - DevOps and deployment (e.g., Docker, Kubernetes, Jenkins, Cloud Deployment)
    - Computer hardware and networks (e.g., CPUs, GPUs, Networking Protocols, Load Balancers)
- Exclude topics that only:
    - Mention technology companies without technical context (e.g., "What does Google do?", "History of Microsoft")
    - Use technical terms metaphorically (e.g., "What is the cloud in my thoughts?", "How does a human network?")
    - Involve basic computer usage (e.g., "How to turn on a computer?", "How to use a browser?")
    - Mathematics topics like probability and statistics etc.

Respond with exactly one word: 'Yes' or 'No'."""

    user_prompt = f"""Topic: {topic.strip()}

Question: Is this topic directly related to coding, software development, or computer science? Consider:
1. React.js is a JavaScript library used to build user interfaces in web development.
2. It involves writing code for the front-end of web applications.
3. React.js would typically be taught in a computer science or software development course as part of front-end development.

Reply with only 'Yes' or 'No'."""

    result = await invoke_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
          model_type= ModelType.ANALYSIS
    )

    cleaned_result = result.get('answer', '').strip().lower()

    return 'Yes' if cleaned_result == 'yes' else 'No'


async def question_generation_agent(query_request: QueryRequest, context: str, previous_questions: Optional[list] = None) -> Dict:


    """
    Generates an advanced question based on the context and query request.
    Supports both custom few-shot examples and default examples based on difficulty.
    """


    # Default examples for each difficulty level
    default_examples = {
            "fill in the blanks": {
                "Easy": """1. A gas compresses from 8 liters to _____ liters against a varying pressure described by P=2/V (in atm/L), doing -600 J of work. (Answer: 4 liters)

        2. In statistical thermodynamics, the average kinetic energy of gas molecules is proportional to _____, while their root mean square speed is proportional to _____. (Answer: temperature, square root of temperature)""",

                "Medium": """1. During a polytropic process (PV^n = constant) at 400K, a gas does 800 J of work while compressing from 6L to _____ L with polytropic index n = _____ . (Answer: 3L, 1.4)

        2. For a real gas following the van der Waals equation, the correction term 'a' accounts for _____, while 'b' accounts for _____ of the gas molecules. (Answer: attractive forces, finite volume)""",

                "Hard": """1. In an irreversible adiabatic process at initial temperature 350K, if a gas expands from 3L to 9L and the initial pressure is 4 atm, the entropy change will be _____ J/K. (Answer: 2.303)

        2. For a polyatomic gas at high temperature, the ratio of specific heats (γ) approaches _____, because the vibrational modes contribute _____ R to the heat capacity. (Answer: 1.33, 1)"""
            },

            "true/false": {
                "Easy": """1. Calculate whether this statement is true or false: In a reversible adiabatic process, the quantity PV^γ remains constant, where γ depends on the molecular structure of the gas. (Answer: True)

        2. For an ideal gas undergoing an isothermal process at 300K, the product of pressure and volume at two different states (P1V1 = P2V2) is constant. (Answer: False)""",

                "Medium": """1. Evaluate if this statement is true or false: In a van der Waals gas, the internal pressure decreases with increasing volume while keeping temperature constant. (Answer: True)

        2. A system absorbs 500J of heat and performs 300J of work; the change in internal energy of the system is 200J. (Answer: True)""",

                "Hard": """1. Evaluate if this statement is true or false: For a Stirling engine operating between 500K and 300K with regeneration, if it absorbs 2000J of heat, the work output will be greater than a Carnot engine operating between the same temperatures. (Answer: False)

        2. Assess if this statement is true or false: The fugacity coefficient of a real gas approaches unity as pressure approaches zero at any temperature. (Answer: True)"""
            },

            "multiple choice questions": {
                "Easy": """1. A gas undergoes a polytropic process (PV^n = constant) from 2L to 6L. If n = 1.4, the work done by the gas is:

        2. Which of these is NOT a valid Maxwell relation?""",

                "Medium": """1. For a real gas following van der Waals equation, which quantity represents the internal pressure?

        2. The change in Gibbs free energy for a reversible process at constant temperature and pressure is:""",

                "Hard": """1. A heat pump operates between -5°C and 35°C with 65% of Carnot COP. Its actual COP for heating is:

        2. For a binary mixture at constant temperature and pressure, the Gibbs-Duhem equation states:
"""
            },

            "short answer": {
                "Easy": """1. Calculate the change in entropy when 2 moles of an ideal gas undergoes free expansion from 2L to 8L at constant temperature. Show your work and explain why the process is irreversible.

        2. Define fugacity and explain its relationship with pressure for real gases at different conditions.""",

                "Medium": """1. A heat engine operates on a dual cycle (combination of Otto and Diesel cycles) with compression ratio 16:1 and cut-off ratio 2. Calculate its thermal efficiency if γ = 1.4.

        2. Explain the concept of chemical potential and its significance in phase equilibrium. How does it relate to Gibbs free energy?""",

                "Hard": """1. An ideal gas undergoes a polytropic process (PV^n = constant) from 3 atm and 2L to 1 atm and 4L. Calculate the work done, heat transferred, and change in internal energy if n = 1.2 and the gas is diatomic.

        2. Derive the Maxwell relations from the total differential of internal energy and explain their practical significance in thermodynamics."""
            },

            "essay": {
                "Easy": """1. Derive the virial equation of state from statistical mechanics principles, explaining the physical significance of each virial coefficient and their temperature dependence.

        2. Discuss the concept of exergy and its destruction in irreversible processes. Include examples from engineering systems and explain its importance in efficiency analysis.""",

                "Medium": """1. Analyze the behavior of real gases using the van der Waals equation, including a detailed discussion of the critical point, Maxwell construction, and metastable states. Compare with experimental behavior.

        2. Examine the thermodynamic basis of chemical equilibrium using the concept of chemical potential. Discuss the effects of temperature, pressure, and composition on equilibrium constants.""",

                "Hard": """1. A complex heat engine operates on a combined cycle using different working fluids in each stage. Analyze its performance using the Second Law, including availability analysis, entropy generation, and lost work. Compare with simpler cycles.

        2. Develop the theoretical framework for phase transitions in multicomponent systems using the Gibbs phase rule. Include detailed analysis of binary phase diagrams and their practical applications."""
            }
        }

    if query_request.few_shot:

        example_prompt = f"""
        Few-Shot Example:
        The following is a custom example demonstrating the expected question format and difficulty level:
        {query_request.few_shot}
        """
    else:
        difficulty = query_request.difficulty
        question_type = query_request.type_of_question.lower()

        if question_type in default_examples:

            if difficulty in default_examples[question_type]:
                example_questions = default_examples[question_type][difficulty]
                example_prompt = f"""
                Example Questions at {difficulty} Difficulty Level for {question_type}:
                {example_questions}
                """
            else:
                example_questions = default_examples[question_type]["Medium"]
                example_prompt = f"""
                Example Questions at Medium Difficulty Level for {question_type} (Default):
                {example_questions}
                """
        else:
            raise ValueError(f"Invalid question type: {question_type}. Available types: {list(default_examples.keys())}")

    coding = """
#### Programming Challenge
    Generate a computer science question that:
    Must require coding implementation (Preferrably) or numerical calculation.
    Should be numerical, NOT theoretical.
    Should be solvable within 15 minutes.

    Example format:
    'Write a function to reverse a linked list.
    Input: 1->2->3
    Output: 3->2->1
    """

    non_coding = """
#### Technical Concept Analysis
- **Objective**:Generate a computer science question that:
    - Encourages critical thinking and analysis.
    - Avoids overly simplistic or obvious questions.
    - Tests understanding of computer science topics and principles
    - Focuses on theoretical aspects without requiring actual code implementation.
    - **Do NOT** require any mathematical calculation.
    - Avoid haveing too many numbers in the question.

    Example format:
     "how encapsulation impacts software maintainability. Provide an example where encapsulation improves code stability."
    """

    numerical = """
### Requirements for Numerical Tricky Problems

1. *Topic-Specific*: Align strictly with the provided topic (e.g., thermodynamics, algebra).
2. *Numerical Calculations*: Must include specific numbers, requiring step-by-step calculations.
3. *Trickiness*: Add multi-step reasoning, hidden details, or common misconception challenges.
4. *Mathematical Steps*: Clearly define required formulae and logical mathematical steps to solve.
5. *Clarity*: Provide all necessary data and avoid ambiguity.
6. *Solvability*: Ensure each problem has a valid and unique solution.

*Example format:
"A gas doubles its volume isothermally at 300 K. Calculate work done (R = 8.314 J/mol·K)."
*Steps*: Use \( W = nRT \ln(V_f / V_i) \).
    """


    non_numerical = """
#### Theory
- **Objective**: Create a question that explores:
    - Encourages critical thinking and analysis.
    - Avoids overly simplistic or obvious questions.
    - Tests understanding of concepts in depth.
    - Focuses on theoretical aspects.
    - **Do NOT** require any numerical calculations.

    Example format:
    What are the trade-offs between design choices in solving a problem.
    """


    iscodetype = await isCodeBased(query_request.topic)
    if iscodetype == "Yes":
        numericality_type = coding if query_request.numericality == "Numerical/Coding" else non_coding
    else:
        numericality_type = numerical if query_request.numericality == "Numerical/Coding" else non_numerical

    base_prompt = f"""
### **Context Provided**:
{context}

### Advanced Question Generation
- **Objective**: Create an intellectually challenging question that tests deep understanding.
- **General Requirements**:
    - **Difficulty Level**: {query_request.difficulty or 'medium'}
    - Ensure the question requires more than surface-level recall

    - **Topic**: {query_request.topic or 'General'}
    - Use clear, precise academic language
    - Minimize ambiguity in the question.
    """

    one_shot_example = """
Here is an example question that you can use as basis, do NOT generate this question, just check the chain of thought used here and use the same:
Example Question:
A pharmaceutical company claims that its new drug reduces cholesterol levels by an average of 20 mg/dL. To test this claim, a random sample of 30 patients is taken, and the reduction in cholesterol levels is measured. The sample has a mean reduction of 18 mg/dL with a standard deviation of 4 mg/dL.

Formulate the null and alternative hypotheses to test the company’s claim.
Conduct a hypothesis test at a 5% significance level to determine if there is enough evidence to refute the company’s claim. Assume the population is normally distributed.
Calculate the p-value for this test.
Based on the results, interpret whether the company’s claim can be upheld.
    """
    new_question_requirement = ""
    if previous_questions:
        formatted_questions = [str(question) for question in previous_questions]
        new_question_requirement = (
            "\n\n### Previously Generated Questions:\n" +
            "\n".join([f"- {question}" for question in formatted_questions]) +
            "\n\n### New Requirement:\n"
            "- Create a **completely distinct** question that tests a different aspect of the topic.\n"
            "- Avoid rephrasing or minor changes to existing questions.\n"
            "- Use this process:\n"
            "  1. Identify the focus of previous questions.\n"
            "  2. Think of an unexplored sub-topic or skill related to the topic.\n"
            "  3. Frame a question targeting that new area."
        )

    question_specific = ""
    type_of_question = query_request.type_of_question.lower()
    if type_of_question == "multiple choice questions":
        question_specific = f"""
    ### Question Generation:

    #### Detailed Requirements:
    1.  Ensure the question can be easily converted into multiple-choice format.
    2. Avoid open-ended questions or those that cannot be answered with a single, clear response.
    3. The question should focus on assessing knowledge, recognition, or simple application of concepts.
    4. Must be interrogative and can be answered within 3-4 lines maximum.
    5. **Generated Questions Must Be**: {numericality_type}

    #### Output Format:
    - Provide only a **single** standalone question.
    - Exclude any answers, explanations, or hints under all circumstances.
    - **Generated Questions Must Be**: {numericality_type}
    """


    elif type_of_question == "true/false":
        question_specific = f"""
        # Task: Generate Numerical True/False Questions

        ## Question Requirements:
        - Question may involve specific numbers, quantities, measurements, or statistics
        - Answer must be definitively True or False (no ambiguity)

        ## Format Specifications:
        - Question should be clear and concise
        - Should NOT be more than 5-6 lines
        - Include units where applicable
        - Provide numerical values in appropriate precision
        - Avoid compound statements that mix multiple facts
        - Generated Question must be:{numericality_type}
        - **Do NOT** generate any explanation, answers or hint in the question
"""

    elif type_of_question == "fill in the blanks":
        question_specific = f"""
###Task: You are a Fill-in-the-Blanks Questions Generator

#### Rules:
## Core Requirements:
- Create ONE strategic blank .
- Question can involve specific numbers, quantities, measurements, or statistics
- Maximum 4 lines of text
- Focus on essential concepts/values
- Ensure unique, unambiguous answer

2. **Structure**:
   - Place blank at critical point
   - Maintain logical flow.
   - Target key terminology or numbers for blanks.
   - Must NOT be bigger than 5-6 lines.
   - Avoid  long or common filler phrases for answers
   - Create only ONE blank.

#### Output:
- Return **ONLY** the statement text with blanks.
- **Exclude**:
  - Answers
  - Hints
  - Given prompts
  - Explanations
  - Source material
- Create only ONE blank.
- Generated Questions Must Be:{numericality_type}
        """

    elif type_of_question == "short answer":
        question_specific = f"""
### Question Type: Short Answer

#### Detailed Requirements:
1. **Cognitive Complexity**:
   - Create thought-provoking questions that require analytical thinking.
   - Ensure the question can be answered comprehensively in 3-5 sentences.

2. **Question Construction**:
   - Generate a single short answer question.
    - Can be numerical or coding question
   - **Do NOT** provide the answer or any hints, just the question.
   - **Generated Questions Must Be**:
        {numericality_type}

#### Output Format:
- A question that can be answered in 3-5 sentences.
- **Exclude** any solutions, hints, or additional context that could reveal the answers.

        """


    elif type_of_question == "essay":
        question_specific = f"""
### Question Type: Essay

#### Detailed Requirements:
1. **Cognitive Complexity**:
   - Create a complex, multif-parts question that requires deep analysis.
   - Ensure the question allows for critical thinking and personal insights.

2. **Question Construction**:
   - Generate one essay question.
   - Can be Mathematical numerical or coding question .
   - can include explanation, derivation, proof in different parts of the question
   - Suggest key points to be addressed in the essay-question.
   - **Do NOT** provide the answer or any hints, just the question.
   -  **Generated Questions Must Be**:
        {numericality_type}

#### Output Format:
- Comprehensive essay question.
- **Exclude** any solutions, hints, or additional context that could reveal the answers.
        """

    else:
        raise ValueError(f"Unsupported question type: {type_of_question}")
    user_prompt_combined = base_prompt+ "\n" + question_specific + "\n" + new_question_requirement  +"\n" + example_prompt

    system_prompt_combined="""You are an expert at crafting thought-provoking questions that require analytical thinking. Your questions:
# Question Crafting Guidelines

## Your Questions:
- Have **no direct solutions** but allow for multiple valid approaches.
- **Connect different concepts** in unexpected ways.
- **Challenge assumptions** and conventional thinking.
- Use **real-world ambiguity and complexity**.
- Focus on **reasoning over recall**.
- Encourage **pattern recognition**.
- **Balance challenge with accessibility**.

You provide minimal context - just enough to understand but leaving room for discovery. Your goal is sparking curiosity and independent thinking rather than guiding to predetermined answers.
"""

    result = await invoke_llm(
        system_prompt=system_prompt_combined,
        user_prompt=user_prompt_combined,
        model_type= ModelType.ANALYSIS
    )

    return result


async def  correct_statement_agent(type_of_question: str, question: str, context: str) -> Dict:
    """
    Enhanced Generic Answer Agent
    Generates sophisticated answers based on the type of question from the query request and context.s

    Args:
        query_request (QueryRequest): Request containing question type and parameters
        question (str): The specific question or statement to be processed
        context (str): Contextual information to guide answer generation

    Returns:
        Dict: Structured response based on question type
    """
    prompts = {
"multiple choice questions": f"""
# Task: Generate the Precise and Definitive Answer

### Input:
- **Context**: {context}
- **Question**: {question}

### Objective:
Deliver a concise, accurate answer directly addressing the question. Avoid any introductory phrases, filler text, or unnecessary elaboration.

### Strict Guidelines:
1. Focus solely on extracting key details from the context.
2. Provide a complete , precise and well-defined answer as an option
3. No explanations, solution,  calculation or reasoning—just the final answer itself.
4.**STRICT**:In case of Numerical question, generate ONLY the final calculated value with NO calculation.

### Output:
A clear and accurate answer to the question, with only the final calculated value included.
"""
,

"true/false": f"""Comprehensive True/False Statement Evaluation

Evaluation Parameters:
Reference Context: {context}
Statement: {question}

Analytical Framework:
- Conduct a focused contextual analysis
- Assess statement's accuracy with scholarly precision
- Provide clear, evidence-based justification


Detailed Assessment Requirements:
1. Determine definitively: True/False
2. Provide concise justification:
   - Direct evidence supporting classification
   - Clear and logical reasoning

Statement: {question}

Output Expectations:
- Classification: True/False
- Justification: Brief and to the point explanation
**Note**: Remove everything else except the two items above.

""",

"fill in the blanks":f"""Identify all the blanks in the question and fill with the most appropriate and correct fits.

Input:
- Context: {context}
- Target: {question}

Rules:
1. Analyze context and target sentence
2. Fill ALL blanks with:
   - Grammatically correct terms
   - Contextually appropriate phrases
   - Logically coherent answers
   - Semantically relevant content

Requirements:
- Must maintain sentence structure
- Must align with given context
- Must use precise terminology
- Must be a proper answer

DON'T:
- Leave any blank without answering
- Add any markers, labels, tags etc.

Target: {question}

Output Format:
1. Completion: [Fill ALL blanks with most appropriate terms]
Note: Return ONLY the exact word(s), phrase(s), or term(s) for the blank(s). Do not include any other text, alternative answers, explanations, markers, labels, tags or full sentences in the output.
""",

"short answer": f"""
# Advanced Short-Answer Response Generation Framework

### Input Information:
- **Contextual Foundation**: {context}
- **Question**: {question}

### Purpose:
Generate a precise, contextually grounded answer that directly addresses the question with clarity and sophistication.

### Response Development Strategy:
1. **Extract Core Insights**: Identify the most relevant details from the context to construct the response.
2. **Answer Structure**:
   - Start with a clear and definitive claim answering the question.
   - Include 2-3 supporting details or examples derived explicitly from the context.
   - Conclude with a concise and insightful synthesis.
   - In case of coding or numerical question, give code or solution in a structured format

### Composition Guidelines:
- Use professional, clear, and accessible language.
- Ensure logical flow and coherence in the response.
- Avoid verbose explanations or extraneous information.
- Focus on accuracy and direct alignment with the question.

### Output Requirements:
- Limit the response to 3-5 sentences.
- Exclude reference to the context in the output.
- Provide an answer that is comprehensive, concise, and directly addresses the question.
- Ensure the response reflects a deep understanding of the question without explicitly mentioning the context.

---

### Final Output:
A well-structured and concise response that answers the question effectively.
""",

        "essay": f"""
# Advanced Essay Outline Generation

### Essay Blueprint Requirements:
**Contextual Foundation:** {context}

---

### Strategic Outline Development:
- Conduct comprehensive contextual analysis
- Identify multiple interpretative dimensions
- Create intellectually robust structural framework

---

### Outline Composition Guidelines:
1. Generate 3-5 sophisticated thematic sections
2. Ensure logical progressive development
3. Incorporate potential counterarguments
4. Reflect nuanced understanding

---

### Structural Expectations:
- Introductory Thesis Section
- Analytical Body Sections
- Critical Interpretative Perspectives
- Potential Scholarly Counterpoints
- Synthesizing Conclusion
- *Do not provide references in the output*
- In case of coding or numerical question, give code or solution in a structured format

---

### Question:
**{question}**

---

### Intellectual Depth Indicators:
- Demonstrate multifaceted comprehension
- Showcase analytical sophistication
- Provide framework for comprehensive exploration
"""
    }

    question_type = type_of_question.lower()
    if question_type not in prompts:
        raise ValueError(f"Unsupported question type: {type_of_question}")

    user_prompt_combined = prompts[question_type]
    system_prompt="""You generate answers with maximum sophistication while maintaining strict contextual accuracy. Your responses:

- Present information with academic-level depth and precision
- Use precise technical language appropriate to the field
- Structure complex ideas clearly and logically
- Include relevant theoretical frameworks when applicable
- Remove all meta-markers from multiple choice selections

For multiple choice questions:
- The correct option appears as plain text
- No explanatory labels, tags, or markers
- No "Option:" or "Answer:" prefixes
- No additional notes or commentary
- No trailing indicators

For all other responses:
- Provide comprehensive analysis
- Maintain formal academic tone
- Include domain-specific terminology
- Structure response hierarchically

Keep responses focused solely on content, eliminating any meta-text or markers that could detract from pure information delivery."""
    result = await invoke_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt_combined,
          model_type= ModelType.ANALYSIS
    )
    return result


async def distractor_generation_agent(
    question: str,
    correct_answer: str,
    context: str,
    existing_distractors: List[str] = []
) -> Dict:
    """
    Distractor Generation Agent
    Generates plausible, incorrect answers (distractors) based on the context.

    Args:
        question (str): The multiple-choice question
        correct_answer (str): The correct answer to the question
        context (str): Contextual information to base distractors on
        existing_distractors (List[str], optional): Previously generated distractors to avoid

    Returns:
        Dict: A dictionary containing the generated distractor
    """


    user_prompt_combined = f"""
## Task: Generate ONE NEW Wrong Option

### Question:
{question}

### Correct Answer:
{correct_answer}

### Existing Wrong Options:
{chr(10).join(existing_distractors) if existing_distractors else 'None'}

### Instructions:
Create **one new wrong option** that:
1. Is **plausible** and appears similar to the correct answer.
2. Has subtle differences that make it **incorrect**.
3. Avoids repeating any existing wrong options.
4. Is designed to challenge the student by being misleading without being obviously incorrect.
5. Should not give any hint on why it's incorrect.

Provide only the new wrong option as output.
"""

    system_prompt_combined="""You generate a single, highly plausible incorrect option for multiple-choice questions.
The distractor closely mirrors the complexity, language, and length of the correct answer while containing subtle but significant errors that reflect common misconceptions.
It appears authentic, reasonable, and maintains consistent technical depth without being obviously wrong.
Your delivery rules are: provide only the distractor text with no explanations, justifications, labels, markers, or commentary on its plausibility, and no hints about why it's incorrect."""

    result = await invoke_llm(
        system_prompt=system_prompt_combined,
        user_prompt=user_prompt_combined,
          model_type= ModelType.ANALYSIS
    )

    if "error" in result:
        raise ValueError(f"LLM Error: {result['error']}")

    distractor_text = result.get("answer", "").strip()
    if not distractor_text:
        raise ValueError(f"Invalid distractor from LLM: {result}")

    return {
        "answer": distractor_text,  # Standardize to 'answer'
        "is_valid": (
            distractor_text != correct_answer and
            distractor_text not in existing_distractors
        )
    }


async def generate_multiple_choice_questions(query_request: QueryRequest, context: str) -> Dict:
    previous_questions = []
    final_questions = []

    for _ in range(query_request.no_of_questions):
        question_result = await question_generation_agent(query_request, context, previous_questions)

        if not isinstance(question_result, dict) or 'answer' not in question_result:
            raise ValueError(f"Invalid question result: {question_result}")

        question = question_result['answer']
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Invalid question format: {question}")

        previous_questions.append(question)

        correct_answer_result = await correct_statement_agent(query_request.type_of_question, question, context)
        correct_answer = correct_answer_result.get('answer', '').strip()
        if not correct_answer:
            raise ValueError(f"Invalid correct answer: {correct_answer_result}")

        distractors = []
        current_context = context or ""
        for _ in range(query_request.no_of_options - 1):
            distractor_result = await distractor_generation_agent(
                question,
                correct_answer,
                current_context,
                existing_distractors=distractors
            )
            new_distractor = distractor_result.get('answer', '').strip()
            if not new_distractor:
                raise ValueError(f"Invalid distractor: {distractor_result}")
            distractors.append(new_distractor)
            current_context += f"\nPrevious Distractors: {', '.join(distractors)}"

        all_options = [correct_answer] + distractors
        random.shuffle(all_options)

        tagged_question = tag_spanda_question(question, correct_answer, "multiple choice questions", all_options)
        final_questions.append(tagged_question)

    return {
        "questions": final_questions,
        "metadata": {"total_questions": len(final_questions)}
    }


async def generate_true_false_questions(query_request: QueryRequest, context: str) -> Dict:
    previous_questions = []
    final_questions = []

    for _ in range(query_request.no_of_questions):
        question_result = await question_generation_agent(query_request, context, previous_questions)

        if not isinstance(question_result, dict) or 'answer' not in question_result:
            raise ValueError(f"Invalid question result: {question_result}")

        question = question_result['answer']
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Invalid question format: {question}")

        previous_questions.append(question)

        correct_answer_result = await correct_statement_agent(query_request.type_of_question, question, context)
        correct_answer = correct_answer_result.get('answer', '').strip()
        if not correct_answer:
            raise ValueError(f"Invalid correct answer: {correct_answer_result}")

        tagged_question = tag_spanda_question(
            question,
            correct_answer,
            "True/False"
        )

        final_questions.append(tagged_question)

    return {
        "questions": final_questions,
        "metadata": {"total_questions": len(final_questions)}
    }


async def generate_fill_blank_questions(query_request: QueryRequest, context: str) -> Dict:
    previous_questions = []
    final_questions = []

    for _ in range(query_request.no_of_questions):
        question_result = await question_generation_agent(query_request, context, previous_questions)

        if not isinstance(question_result, dict) or 'answer' not in question_result:
            raise ValueError(f"Invalid question result: {question_result}")

        question = question_result['answer']
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Invalid question format: {question}")

        previous_questions.append(question)

        correct_answer_result = await correct_statement_agent(query_request.type_of_question, question, context)
        correct_answer = correct_answer_result.get('answer', '').strip()

        if not correct_answer:
            raise ValueError(f"Invalid correct answer: {correct_answer_result}")

        tagged_question = tag_spanda_question(
            question,
            correct_answer,
            "Fill in the Blanks"
        )

        final_questions.append(tagged_question)

    return {
        "questions": final_questions,
        "metadata": {"total_questions": len(final_questions)}
    }


async def generate_short_answer_questions(query_request: QueryRequest, context: str) -> Dict:
    tracked_questions = []
    final_questions = []

    for _ in range(query_request.no_of_questions):
        question_result = await question_generation_agent(query_request, context, previous_questions=tracked_questions)

        question = question_result.get('answer', '')
        if not question:
            raise ValueError("No question generated")

        tracked_questions.append(question)

        sample_answer_result = await correct_statement_agent(query_request.type_of_question, question, context)
        sample_answer = sample_answer_result.get('answer', '').strip()
        if not sample_answer:
            raise ValueError(f"No answer generated for question: {question}")

        tagged_question = tag_spanda_question(
            question,
            sample_answer,
            "Short Answer"
        )

        final_questions.append(tagged_question)

    return {
        "questions": final_questions,
        "metadata": {"total_questions": len(final_questions)}
    }


async def generate_essay_questions(query_request: QueryRequest, context: str) -> Dict:
    previous_questions = []
    final_questions = []

    for _ in range(query_request.no_of_questions):
        question_result = await question_generation_agent(query_request, context, previous_questions)

        if not isinstance(question_result, dict) or 'answer' not in question_result:
            raise ValueError(f"Invalid question result: {question_result}")

        question = question_result['answer']
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Invalid question format: {question}")

        previous_questions.append(question)

        key_points_result = await correct_statement_agent(query_request.type_of_question, question, context)
        key_points = key_points_result.get('answer', '').strip()
        if not key_points:
            raise ValueError(f"Invalid key points: {key_points_result}")

        tagged_question = tag_spanda_question(
            question,
            key_points,
            "Essay"
        )

        final_questions.append(tagged_question)

    return {
        "questions": final_questions,
        "metadata": {
            "total_questions": len(final_questions)
        }
    }
