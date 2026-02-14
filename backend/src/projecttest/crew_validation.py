from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from projecttest.models.cv_analysis import CVAnalysis

@CrewBase
class ValidationCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def interviewer(self) -> Agent:
        return Agent(config=self.agents_config["interviewer"], verbose=True)

    @task
    def validate_answer_task(self) -> Task:
        return Task(
            config=self.tasks_config["validate_answer_task"]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.interviewer()],
            tasks=[self.validate_answer_task()],
            verbose=True
        )
