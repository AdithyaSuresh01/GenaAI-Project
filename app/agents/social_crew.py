from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm

class SocialCrew:
    def __init__(self, llm=None):
        # If the API passes a specific LLM (User's Gemini), use it.
        # Otherwise, fall back to the default (Admin Perplexity/Gemini).
        self.llm = llm if llm else get_llm()

    def generate_social_content(self, project_name: str, tech_stack: str, description: str):
        # 1. LinkedIn Agent
        linkedin_agent = Agent(
            role='Tech Influencer & Career Coach',
            goal='Write viral, professional LinkedIn posts for students',
            backstory="You know exactly how to frame a student project to attract recruiters. You use emojis, clear hooks, and professional hashtags.",
            verbose=True,
            llm=self.llm
        )

        # 2. GitHub Agent
        github_agent = Agent(
            role='Senior Open Source Maintainer',
            goal='Write an impressive GitHub README summary',
            backstory="You know what makes a repository stand out. You focus on features, installation, and tech stack highlighting.",
            verbose=True,
            llm=self.llm
        )

        # 3. Tasks
        linkedin_task = Task(
            description=f"""
            Write a LinkedIn post announcing that I just built {project_name} using {tech_stack}.
            Description: {description}
            
            Structure:
            - Catchy Hook (Problem solved)
            - What I built (Solution)
            - Tech Stack used (Keywords)
            - Call to Action (Check my GitHub)
            - Hashtags
            """,
            expected_output="A ready-to-post LinkedIn text update.",
            agent=linkedin_agent
        )

        readme_task = Task(
            description=f"""
            Write a professional README.md introduction for {project_name}.
            Include badges for {tech_stack}, a 'Features' section, and a 'Getting Started' section.
            """,
            expected_output="Markdown formatted README content.",
            agent=github_agent
        )

        # 4. Crew
        crew = Crew(
            agents=[linkedin_agent, github_agent],
            tasks=[linkedin_task, readme_task],
            process=Process.sequential  # Run both at same time for speed
        )

        return crew.kickoff()
