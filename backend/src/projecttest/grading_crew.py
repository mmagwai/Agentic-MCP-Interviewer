from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from projecttest.tools.code_runner import run_code_tool
from projecttest.tools.run_code_tool import RunCodeTool


@CrewBase
class GradingCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/grading_tasks.yaml"

    @agent
    def answer_grader(self) -> Agent:
        return Agent(
            config=self.agents_config["answer_grader"],
            verbose=True,
            tools=[RunCodeTool()]
        )

    @task
    def grade_coding_solution(self) -> Task:
        return Task(config=self.tasks_config["grade_coding_solution"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.answer_grader()],
            tasks=[self.grade_coding_solution()],
            verbose=False,
        )
