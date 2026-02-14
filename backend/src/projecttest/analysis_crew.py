from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from projecttest.models.cv_analysis import CVAnalysis


@CrewBase
class CVAnalysisCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/analysis_tasks.yaml"

    @agent
    def cv_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["cv_analyzer"],
            verbose=False
        )

    @task
    def analyze_cv_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_cv_task"],
            output_pydantic=CVAnalysis
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.cv_analyzer()],
            tasks=[self.analyze_cv_task()],
            verbose=False
        )
