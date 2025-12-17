from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm

class DebugCrew:
    def __init__(self, llm=None):
        # If the API passes a specific LLM (User's Gemini), use it.
        # Otherwise, fall back to the default (Admin Perplexity/Gemini).
        self.llm = llm if llm else get_llm()

    def debug_code(self, code_snippet: str, error_message: str):
        # 1. Agent
        debugger = Agent(
            role='Senior Software Debugger',
            goal='Identify and fix code errors efficiently',
            backstory="You are a veteran developer who has seen every error message. You don't just fix code; you explain the fix so the student learns.",
            verbose=True,
            llm=self.llm
        )

        # 2. Task
        debug_task = Task(
            description=f"""
            Analyze this broken code and error message.
            
            CODE:
            {code_snippet}
            
            ERROR:
            {error_message}
            
            Your Output must include:
            1. **The Root Cause**: What went wrong?
            2. **The Fix**: The corrected code block.
            3. **Prevention**: How to avoid this in the future.
            """,
            expected_output="A structured debugging report with fixed code.",
            agent=debugger
        )

        # 3. Crew
        crew = Crew(
            agents=[debugger],
            tasks=[debug_task],
            process=Process.sequential
        )

        return crew.kickoff()
