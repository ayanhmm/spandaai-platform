const constantRubric = {
    "Subject Mastery": {
        "criteria_explanation": `
        "Subject Mastery evaluates the instructor's depth of knowledge and ability to teach effectively. This includes:
        - Command over subject matter
        - Integration of recent research and developments
        - Effective use of teaching resources
        - Pedagogical expertise
        The key question: 'Does the instructor demonstrate expertise and effectively convey subject knowledge?'"`,

        "criteria_output": {
            "1. Assess content depth": "Evaluate whether the instructor provides in-depth knowledge, including contemporary research, historical context, and multiple perspectives.",
            "2. Review use of resources": "Determine if the instructor utilizes up-to-date references, examples, and instructional materials to enhance learning.",
            "3. Evaluate pedagogical expertise": "Analyze whether the instructor effectively structures lessons, scaffolds learning, and adapts content complexity as needed."
        },

        "score_explanation": {
            "Score 1": {
                "Description": "Minimal knowledge, outdated content, lacks pedagogical structure.",
                "Examples": "Fails to explain core concepts, does not reference contemporary developments, uses incorrect information.",
                "Explanation": "Fails to meet academic teaching standards."
            },
            "Score 2": {
                "Description": "Basic knowledge with gaps in content and pedagogy.",
                "Examples": "Covers only surface-level topics, lacks structured explanations, minimal reference to current research.",
                "Explanation": "Shows limited expertise in the subject matter."
            },
            "Score 3": {
                "Description": "Competent subject knowledge with adequate pedagogy.",
                "Examples": "Covers key topics sufficiently, explains with some clarity, uses basic but relevant resources.",
                "Explanation": "Meets fundamental teaching standards."
            },
            "Score 4": {
                "Description": "Strong mastery with clear and structured teaching.",
                "Examples": "Explains complex topics clearly, integrates relevant examples, aligns content with current academic knowledge.",
                "Explanation": "Demonstrates effective instructional competence."
            },
            "Score 5": {
                "Description": "Exceptional expertise with cutting-edge insights.",
                "Examples": "References latest research, makes deep connections, demonstrates superior pedagogical acumen.",
                "Explanation": "Exemplary teaching standard with high academic rigor."
            }
        }
    },

    "Clarity and Communication": {
        "criteria_explanation": `
        "This dimension assesses the instructor’s ability to deliver content clearly and maintain student engagement. This includes:
        - Language clarity
        - Organization of content
        - Voice modulation, tone, and pacing
        - Use of visuals and examples
        The key question: 'Does the instructor communicate effectively to facilitate understanding?'"`,

        "criteria_output": {
            "1. Assess clarity of explanations": "Evaluate if explanations are concise, structured, and avoid ambiguity.",
            "2. Review engagement techniques": "Identify whether the instructor uses relatable examples, analogies, and demonstrations to clarify concepts.",
            "3. Analyze vocal delivery": "Assess the instructor’s tone, pacing, and ability to emphasize key ideas effectively."
        },

        "score_explanation": {
            "Score 1": {
                "Description": "Confusing, disorganized explanations with poor communication skills.",
                "Examples": "Monotonous speech, no emphasis on key points, unclear explanations.",
                "Explanation": "Fails to effectively convey information."
            },
            "Score 2": {
                "Description": "Basic communication with occasional clarity issues.",
                "Examples": "Some explanations are clear, but content organization is weak or inconsistent.",
                "Explanation": "Limited ability to effectively communicate subject matter."
            },
            "Score 3": {
                "Description": "Generally clear communication with structured explanations.",
                "Examples": "Well-paced delivery, moderate use of visuals/examples, reasonably engaging.",
                "Explanation": "Meets acceptable communication standards."
            },
            "Score 4": {
                "Description": "Strong communication with engaging delivery.",
                "Examples": "Uses voice modulation, emphasizes key points, provides well-structured explanations.",
                "Explanation": "Facilitates student understanding effectively."
            },
            "Score 5": {
                "Description": "Exceptional communication skills that captivate and clarify.",
                "Examples": "Engages students dynamically, explains complex ideas with precision and enthusiasm.",
                "Explanation": "Highly effective in ensuring conceptual clarity."
            }
        }
    },

    "Lesson Organization and Flow": {
        "criteria_explanation": `
        "This criterion assesses the logical structuring of the lesson and whether the instructor ensures smooth content transitions. This includes:
        - Clearly defined learning objectives
        - Logical sequencing of topics
        - Effective time management
        - Consistency with the curriculum
        The key question: 'Is the lesson well-structured and logically delivered?'"`,

        "criteria_output": {
            "1. Evaluate lesson structure": "Determine if the instructor presents topics in a logical, coherent order with clear objectives.",
            "2. Assess content transitions": "Review how well the instructor connects concepts and maintains lesson continuity.",
            "3. Analyze curriculum alignment": "Ensure the lesson aligns with established syllabus expectations."
        },

        "score_explanation": {
            "Score 1": {
                "Description": "Unstructured lesson with unclear objectives.",
                "Examples": "Jumps between topics randomly, fails to establish learning outcomes.",
                "Explanation": "Lacks coherence and structure."
            },
            "Score 2": {
                "Description": "Basic organization but lacks smooth transitions.",
                "Examples": "Some structure exists but key points feel disconnected.",
                "Explanation": "Partially structured but needs refinement."
            },
            "Score 3": {
                "Description": "Well-organized with minor flow issues.",
                "Examples": "Lesson follows a structured plan but may have some abrupt topic shifts.",
                "Explanation": "Generally effective organization."
            },
            "Score 4": {
                "Description": "Highly structured and logically sequenced.",
                "Examples": "Lessons build on previous knowledge, flow naturally.",
                "Explanation": "Strong lesson planning and execution."
            },
            "Score 5": {
                "Description": "Flawlessly organized with seamless transitions.",
                "Examples": "Masterfully structured lessons with well-integrated topics.",
                "Explanation": "Exemplary lesson design."
            }
        }
    },

    "Classroom Management": {
        "criteria_explanation": `
        "Classroom Management assesses how well the instructor maintains a disciplined and productive learning environment. This includes:
        - Punctuality and adherence to schedule
        - Establishment of routines
        - Management of disruptions
        - Fostering an inclusive environment
        The key question: 'Does the instructor create an effective and respectful classroom atmosphere?'"`,

        "criteria_output": {
            "1. Assess time management": "Review punctuality and consistency in starting/ending lessons on time.",
            "2. Evaluate class engagement": "Analyze instructor’s ability to keep students attentive and prevent distractions.",
            "3. Review fairness and inclusion": "Ensure the instructor fosters equal participation opportunities."
        },

        "score_explanation": {
            "Score 1": {
                "Description": "Disorganized, frequent disruptions, lacks control.",
                "Examples": "Late to class, unable to maintain student attention.",
                "Explanation": "Ineffective class management."
            },
            "Score 2": {
                "Description": "Basic management but struggles with engagement.",
                "Examples": "Some disruptions persist, but structure is present.",
                "Explanation": "Needs improvement in discipline and engagement."
            },
            "Score 3": {
                "Description": "Effective management with occasional lapses.",
                "Examples": "Generally maintains control and student focus.",
                "Explanation": "Competent class management."
            },
            "Score 4": {
                "Description": "Well-managed classroom with minimal disruptions.",
                "Examples": "Creates a structured environment, addresses distractions quickly.",
                "Explanation": "Strong control over classroom dynamics."
            },
            "Score 5": {
                "Description": "Exceptionally well-managed class environment.",
                "Examples": "Encourages self-discipline, minimizes distractions.",
                "Explanation": "Highly effective in fostering an optimal learning environment."
            }
        }
    },

    "Assessment and Feedback": {
        "criteria_explanation": `
        "Assessment and Feedback evaluate how well the instructor measures student understanding and provides constructive feedback. This includes:
        - Clear assessment criteria
        - Alignment of evaluations with learning objectives
        - Constructive feedback for student improvement
        The key question: 'Does the instructor assess learning effectively and provide meaningful feedback?'"`,

        "criteria_output": {
            "1. Review assessment clarity": "Analyze if grading criteria are clearly communicated before evaluations.",
            "2. Ensure alignment with objectives": "Check if assessments accurately measure student understanding of course material.",
            "3. Evaluate feedback quality": "Assess whether feedback is specific, constructive, and helps students improve."
        },

        "score_explanation": {
            "Score 1": {
                "Description": "Lacks assessment clarity or appropriate feedback.",
                "Examples": "Vague assessment criteria, generic or unhelpful feedback.",
                "Explanation": "Fails to support student improvement."
            },
            "Score 2": {
                "Description": "Basic assessments with limited feedback.",
                "Examples": "Minimal explanation for grades, occasional gaps in criteria.",
                "Explanation": "Does not fully support improvement."
            },
            "Score 3": {
                "Description": "Adequate assessments and feedback.",
                "Examples": "Moderately clear criteria, some constructive feedback.",
                "Explanation": "Provides basic guidance."
            },
            "Score 4": {
                "Description": "Strong assessments and meaningful feedback.",
                "Examples": "Well-communicated criteria, actionable and specific feedback.",
                "Explanation": "Helps students improve effectively."
            },
            "Score 5": {
                "Description": "Outstanding assessments with detailed feedback.",
                "Examples": "Clear criteria, feedback tailored to individual needs.",
                "Explanation": "Ensures continuous improvement and understanding."
            }
        }
    },

    "Instructor’s Enthusiasm and Engagement": {
        "criteria_explanation": `
        "This dimension evaluates the instructor’s passion for teaching and ability to engage students. This includes:
        - Energy and enthusiasm during lectures
        - Ability to keep students engaged
        - Use of humor, storytelling, or interactive elements
        The key question: 'Does the instructor create an engaging learning experience?'"`,

        "criteria_output": {
            "1. Assess enthusiasm": "Determine if the instructor conveys passion and excitement about the subject.",
            "2. Review engagement techniques": "Check if the instructor uses storytelling, humor, or interactive methods to maintain student attention.",
            "3. Evaluate student interaction": "Analyze whether the instructor actively encourages participation and makes lessons engaging."
        },

        "score_explanation": {
            "Score 1": {
                "Description": "Lack of enthusiasm, minimal engagement.",
                "Examples": "Monotonous tone, no interaction.",
                "Explanation": "Fails to engage students."
            },
            "Score 2": {
                "Description": "Limited enthusiasm with occasional engagement.",
                "Examples": "Occasional attempts to engage students but inconsistent.",
                "Explanation": "Minimal effort to sustain engagement."
            },
            "Score 3": {
                "Description": "Moderate enthusiasm with reasonable engagement.",
                "Examples": "Sufficient energy, occasional interactive elements.",
                "Explanation": "Meets basic engagement standards."
            },
            "Score 4": {
                "Description": "Consistent enthusiasm and effective engagement.",
                "Examples": "Energetic delivery, frequent interaction.",
                "Explanation": "Keeps students actively involved."
            },
            "Score 5": {
                "Description": "Exceptional enthusiasm and outstanding engagement.",
                "Examples": "Highly energetic, seamlessly integrates interactive elements.",
                "Explanation": "Captivates and motivates students."
            }
        }
    }
};


export default {constantRubric};