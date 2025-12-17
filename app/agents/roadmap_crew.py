from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm

class RoadmapCrew:
    def __init__(self , llm=None):
        self.llm = llm if llm else get_llm()

    def create_roadmap(self, topic: str, duration: str, level: str):
        # 1. Define Agents
        counselor = Agent(
            role='Senior Academic Counselor',
            goal=f'Analyze the learning requirements for {topic}',
            backstory="You are an expert at understanding student needs and breaking down complex subjects into manageable learning phases.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        architect = Agent(
            role='Curriculum Architect',
            goal=f'Design a detailed {duration} roadmap for {topic}',
            backstory="You are a curriculum expert who creates structured, week-by-week learning plans with clear outcomes and resource recommendations.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # 2. Define Tasks
        analysis_task = Task(
            description=f"""
            Analyze the request: Learn {topic} in {duration} at a {level} level.
            Identify key concepts that MUST be covered.
            List prerequisites and potential pitfalls for beginners.
            """,
            expected_output="A summary of key learning modules and prerequisites.",
            agent=counselor
        )

        curriculum_task = Task(
            description=f"""
            Using the counselor's analysis, create a structured week-by-week roadmap.
            
            You MUST return a VALID JSON object with this exact structure:
            {{
                "roadmap": [
                    {{
                        "week": 1,
                        "title": "Topic Name",
                        "description": "Brief summary of the week",
                        "topics": ["Topic 1", "Topic 2", "Topic 3"],
                        "project": "Description of the mini-project"
                    }},
                    ...
                ]
            }}
            
            Do NOT return markdown formatting (no ``````). Just the raw JSON string.
            """,
            expected_output="A structured JSON object containing the roadmap.",
            agent=architect,
            context=[analysis_task]
        )

        # 3. Create Crew
        crew = Crew(
            agents=[counselor, architect],
            tasks=[analysis_task, curriculum_task],
            process=Process.sequential
        )

        return crew.kickoff()
