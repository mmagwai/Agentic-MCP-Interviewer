from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class EvaluationCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/question_tasks.yaml"

    @agent
    def interviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["interviewer"],
            verbose=True
        )

    @task
    def evaluate_answer(self) -> Task:
        return Task(
            config=self.tasks_config["evaluate_answer"]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.interviewer()],
            tasks=[self.evaluate_answer()],
            verbose=True
        )
