from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm

class MarketingCrew:
    def __init__(self, llm=None):
        # If the API passes a specific LLM (User's Gemini), use it.
        # Otherwise, fall back to the default (Admin Perplexity/Gemini).
        self.llm = llm if llm else get_llm()

    def generate_post(self, project_name: str, description: str, tech_stack: str, tone: str):
        # 1. Define Agent
        marketer = Agent(
            role='Senior Developer Relations (DevRel) Specialist',
            goal='Craft viral, engaging, yet professional social media content for developers.',
            backstory="""You are a top-tier DevRel expert. 
            You know how to write LinkedIn posts that get engagement from the tech community. 
            You balance technical details with storytelling. 
            You use emojis effectively but not excessively.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # 2. Define Task
        post_task = Task(
            description=f"""
            Write a LinkedIn post for a student developer's project.
            
            Project Name: {project_name}
            Tech Stack: {tech_stack}
            Description: {description}
            Desired Tone: {tone}
            
            Requirements:
            - Start with a catchy "Hook" line to grab attention.
            - Explain the "Why" (problem solved) and "How" (tech used).
            - Highlight the specific tech stack ({tech_stack}) used.
            - Include a call to action (e.g., "Check out the repo!" or "What do you think?").
            - Use 3-5 relevant hashtags (e.g., #coding, #python, #opensource).
            - Format it for readability (short paragraphs, bullet points).
            - The output must be JUST the post content, no "Here is your post" preambles.
            """,
            expected_output="A complete, formatted LinkedIn post string.",
            agent=marketer
        )

        # 3. Create Crew
        crew = Crew(
            agents=[marketer],
            tasks=[post_task],
            verbose=True,
            process=Process.sequential
        )

        # 4. Execute
        result = crew.kickoff()
        return str(result)
