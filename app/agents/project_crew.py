from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm
import json

class ProjectCrew:
    def __init__(self, llm=None):
        # If the API passes a specific LLM (User's Gemini), use it.
        # Otherwise, fall back to the default (Admin Perplexity/Gemini).
        self.llm = llm if llm else get_llm()

    def generate_project(self, description: str, technology: str, difficulty: str):
        # 1. Define Agents
        architect = Agent(
            role='Systems Architect',
            goal=f'Design a practical, portfolio-worthy project using {technology}',
            backstory="You are a senior software architect who designs clean, modular, and impressive projects for students to showcase on GitHub.",
            verbose=True,
            llm=self.llm
        )

        developer = Agent(
            role='Lead Developer',
            goal='Write the actual code files for the project',
            backstory="You are an expert coder. You write clean, commented, and error-free code. You provide the FULL content of files.",
            verbose=True,
            llm=self.llm
        )

        # 2. Define Tasks
        design_task = Task(
            description=f"""
            Analyze this project request: "{description}"
            Tech Stack: {technology}
            Difficulty: {difficulty}
            
            Design a complete folder structure and file list for this project.
            The root folder name should be short and descriptive (e.g. "SnakeGame").
            
            Output MUST be a JSON structure:
            {{
                "project_name": "MyProjectName",
                "files": ["main.py", "utils.py", "requirements.txt"]
            }}
            """,
            expected_output="JSON structure of the project.",
            agent=architect
        )

        # 3. Update Coding Task
        coding_task = Task(
            description="""
            Write the FULL code for every file listed by the architect.
            
            You MUST return a VALID JSON object where keys are filenames and values are the code content.
            
            Example:
            {
                "main.py": "import os...",
                "utils.py": "def helper(): pass",
                "requirements.txt": "pandas"
            }
            """,
            expected_output="JSON object with file contents.",
            agent=developer,
            context=[design_task]
        )

        # 3. Create Crew
        crew = Crew(
            agents=[architect, developer],
            tasks=[design_task, coding_task],
            process=Process.sequential
        )

        return crew.kickoff()
