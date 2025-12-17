from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm # Uses your Perplexity/Sonar config

class AssessmentCrew:
    def __init__(self, llm=None):
        # If the API passes a specific LLM (User's Gemini), use it.
        # Otherwise, fall back to the default (Admin Perplexity/Gemini).
        self.llm = llm if llm else get_llm()

    def create_assessment(self, topic: str, assessment_type: str, user_context: str):
        # --- AGENT 1: The Professor ---
        # Responsible for creativity and pedagogical value
        professor = Agent(
            role='Senior Curriculum Developer',
            goal=f'Create a high-quality {assessment_type} that tests deep understanding, not just rote memory.',
            backstory="You are a professor known for creating assessments that perfectly match a student's skill level. You avoid ambiguous questions.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # --- AGENT 2: The Examiner (Validation) ---
        # Responsible for JSON structure and correctness
        examiner = Agent(
            role='Strict Exam Auditor',
            goal='Validate the assessment and ensure strict JSON output format.',
            backstory="You are an algorithm designed to format educational content into machine-readable JSON. You discard bad questions and fix formatting errors.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # --- TASK 1: Draft ---
        draft_task = Task(
            description=f"""
            Draft 5 questions for a '{assessment_type}' on the topic: '{topic}'.
            
            USER CONTEXT: {user_context}
            
            Requirements:
            1. If it's a 'Quiz', provide 4 options and 1 correct answer.
            2. If it's an 'Assignment', provide a coding scenario and the expected outcome.
            3. Ensure difficulty matches the user context.
            """,
            agent=professor,
            expected_output="A list of conceptual questions with options and answers."
        )

        # --- TASK 2: Format & Validate ---
        format_task = Task(
            description=f"""
            Review the drafted questions. Ensure they are correct and fair.
            Then, convert them into this STRICT JSON format:
            
            {{
                "title": "Creative Title Here",
                "questions": [
                    {{
                        "q": "Question text here?",
                        "options": ["A", "B", "C", "D"],  (Include this ONLY if type is 'quiz' or 'test')
                        "answer": "Correct Answer string"
                    }}
                ]
            }}
            
            CRITICAL: Return ONLY the raw JSON string. Do not use Markdown code blocks (```
            """,
            agent=examiner,
            expected_output="Valid JSON string.",
            context=[draft_task] # Depends on the draft
        )

        # --- CREW ---
        crew = Crew(
            agents=[professor, examiner],
            tasks=[draft_task, format_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result
