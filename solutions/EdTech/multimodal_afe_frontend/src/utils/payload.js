const constantRubricpayload = {
  "Subject Mastery": {
      criteria_explanation: `Evaluates the instructor’s command of the subject, ability to convey depth, and integration of relevant examples.
      - Demonstrates strong knowledge with real-world connections
      - Uses up-to-date references, practical applications, and different perspectives
      - Adapts complexity to student level
      Key question: 'Is the instructor’s knowledge comprehensive and effectively communicated?'`,

      criteria_output: `1. Content Depth:
 - Does the instructor go beyond basic explanations to provide deeper insights, real-world applications, or multiple perspectives?
2. Use of Resources:
 - Are examples, references, or teaching aids current and relevant?
3. Pedagogical Clarity:
 - Is information structured to gradually build understanding, with clear explanations?`,

      score_explanation: `Score 1:
- Superficial knowledge, lacks depth, outdated content.
Score 2:
- Basic knowledge, missing clarity or depth.
Score 3:
- Competent, with structured but limited depth.
Score 4:
- Strong command, well-supported by examples.
Score 5:
- Exceptional depth, insightful connections, and well-structured delivery.`
  },

  "Clarity and Communication": {
      criteria_explanation: `Evaluates clarity in delivery, engagement methods, and explanation effectiveness.
      - Uses structured explanations and avoids unnecessary complexity
      - Engages learners with relatable examples and effective pacing
      - Delivers content with confidence and emphasis on key ideas
      Key question: 'Does the instructor make concepts accessible and engaging?'`,

      criteria_output: `1. Explanation Clarity:
 - Are explanations concise and well-structured, avoiding ambiguity?
2. Engagement Techniques:
 - Are relatable examples, analogies, or demonstrations used effectively?
3. Vocal Delivery:
 - Does tone, pacing, and emphasis enhance understanding?`,

      score_explanation: `Score 1:
- Confusing, lacks organization and clarity.
Score 2:
- Basic communication but occasionally unclear.
Score 3:
- Clear explanations with minor lapses.
Score 4:
- Engaging delivery with structured explanations.
Score 5:
- Exceptional clarity, engaging style, and effective communication.`
  },

  "Lesson Organization and Flow": {
      criteria_explanation: `Assesses whether the lesson follows a clear, logical structure that enhances learning.
      - Topics build progressively with seamless transitions
      - The session follows an effective timeline with well-paced discussions
      - Learning objectives are clearly defined and consistently followed
      Key question: 'Does the lesson follow a logical, student-friendly structure?'`,

      criteria_output: `1. Logical Structuring:
 - Are concepts presented in a clear sequence that builds on prior knowledge?
2. Content Transitions:
 - Are topic shifts smooth and well-connected?
3. Curriculum Alignment:
 - Does the lesson align with broader learning objectives?`,

      score_explanation: `Score 1:
- Disorganized, unclear objectives, poor sequencing.
Score 2:
- Basic structure, lacks smooth transitions.
Score 3:
- Generally well-organized but with minor issues.
Score 4:
- Strong organization with effective transitions.
Score 5:
- Seamlessly structured, logical, and well-paced.`
  },

  "Classroom Management": {
      criteria_explanation: `Evaluates how well the instructor maintains a productive learning environment.
      - Keeps discussions focused and students engaged
      - Ensures equal participation and active involvement
      - Handles disruptions effectively while maintaining class energy
      Key question: 'Does the instructor create a structured and engaging classroom atmosphere?'`,

      criteria_output: `1. Time & Focus Management:
 - Does the instructor maintain pacing and ensure focused discussions?
2. Engagement & Participation:
 - Are students actively involved, with equal opportunities to contribute?
3. Disruption Handling:
 - Are distractions minimized while maintaining a positive environment?`,

      score_explanation: `Score 1:
- Disruptive, disorganized, lacks engagement.
Score 2:
- Basic management but struggles with maintaining attention.
Score 3:
- Well-managed with occasional lapses.
Score 4:
- Strong, structured, and engaging class management.
Score 5:
- Highly effective, dynamic, and well-structured classroom control.`
  },

  "Assessment and Feedback": {
      criteria_explanation: `Evaluates how well the instructor assesses student learning and provides constructive feedback.
      - Ensures students clearly understand grading criteria and expectations
      - Aligns assessments with learning objectives for meaningful evaluation
      - Provides detailed feedback that guides student improvement
      Key question: 'Does the instructor give clear, helpful, and constructive assessments?'`,

      criteria_output: `1. Assessment Clarity:
 - Are grading criteria clear and well-explained?
2. Alignment with Learning Goals:
 - Do assessments accurately reflect key objectives?
3. Quality of Feedback:
 - Is feedback specific, actionable, and helpful?`,

      score_explanation: `Score 1:
- Lacks clear assessment structure or feedback.
Score 2:
- Basic evaluations but minimal feedback.
Score 3:
- Clear assessments with moderate feedback quality.
Score 4:
- Well-structured assessments with detailed, useful feedback.
Score 5:
- Outstanding assessments that guide and support learning effectively.`
  },

  "Instructor’s Enthusiasm and Engagement": {
      criteria_explanation: `Evaluates how well the instructor conveys enthusiasm and maintains student interest.
      - Passion for the subject is evident and infectious
      - Uses interactive elements to sustain engagement
      - Encourages active participation and a dynamic learning atmosphere
      Key question: 'Does the instructor keep students engaged and interested?'`,

      criteria_output: `1. Enthusiasm:
 - Does the instructor convey passion for the subject?
2. Engagement Techniques:
 - Are interactive elements, storytelling, or real-world connections used?
3. Encouraging Participation:
 - Does the instructor actively involve students in the learning process?`,

      score_explanation: `Score 1:
- Low enthusiasm, minimal engagement.
Score 2:
- Limited enthusiasm with occasional engagement.
Score 3:
- Moderate enthusiasm with student involvement.
Score 4:
- Consistently engaging and dynamic.
Score 5:
- Highly enthusiastic, engaging, and inspiring.`
  }
};

 
 
 export default {constantRubricpayload};