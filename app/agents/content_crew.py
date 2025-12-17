from crewai import Agent, Task, Crew, Process
from app.core.llm import get_llm

class ContentCrew:
    def __init__(self, llm=None):
        # If the API passes a specific LLM (User's Gemini), use it.
        # Otherwise, fall back to the default (Admin Perplexity/Gemini).
        self.llm = llm if llm else get_llm()

    def create_chapter(self, topic: str, subtopics: list[str], detail_level: str):
        # 1. Define Agent: The Professor
        professor = Agent(
            role='Technical Educator',
            goal=f'Write a comprehensive and engaging chapter on {topic}',
            backstory="""You are a world-class technical writer and professor. 
            You explain complex concepts simply, using analogies, code examples, 
            and clear diagrams (using text/mermaid). You focus on "learning by doing".""",
            verbose=True,
            llm=self.llm
        )

        # 2. Define Task
        chapter_task = Task(
            description=f"""
            Write a detailed educational chapter on "{topic}".
            
            Focus specifically on these subtopics: {', '.join(subtopics)}.
            Target Audience Level: {detail_level}
            
            Structure:
            1. **Introduction**: Why this matters.
            2. **Core Concepts**: Explain the theory clearly.
            3. **Hands-on Examples**: Provide Python code snippets (or relevant language) that work.
            4. **Common Mistakes**: What errors do beginners usually make?
            5. **Summary**: Key takeaways.
            
            Make the tone encouraging but technically rigorous.
            """,
            expected_output="A complete chapter in Markdown format with code blocks.",
            agent=professor
        )

        # 3. Create Crew
        crew = Crew(
            agents=[professor],
            tasks=[chapter_task],
            process=Process.sequential
        )

        return crew.kickoff()
