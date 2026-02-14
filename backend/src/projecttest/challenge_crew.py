from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class ChallengeCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def interviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["interviewer"],
            verbose=False
        )

    @task
    def generate_coding_challenge(self) -> Task:
        return Task(
            config=self.tasks_config["generate_coding_challenge"]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.interviewer()],
            tasks=[self.generate_coding_challenge()],
            verbose=False
        )
