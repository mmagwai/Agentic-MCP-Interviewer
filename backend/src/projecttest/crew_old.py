# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List
# from crewai_tools import SerperDevTool
# from projecttest.models.cv_analysis import CVAnalysis
# # If you want to run a snippet of code before or after the crew starts,
# # you can use the @before_kickoff and @after_kickoff decorators
# # https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# @CrewBase
# class InterviewCrew:
#     agents_config = "config/agents.yaml"
#     tasks_config = "config/tasks.yaml"

#     @agent
#     def cv_analyzer(self) -> Agent:
#         return Agent(
#             config=self.agents_config["cv_analyzer"],
#             verbose=True
#         )
#     @agent
#     def interviewer(self) -> Agent:
#         return Agent(
#             config=self.agents_config["interviewer"],
#             verbose=True
#         )
#     @agent
#     def answer_grader(self) -> Agent:
#         return Agent(
#             config=self.agents_config["answer_grader"],
#             verbose=True
#         )

#     @task
#     def analyze_cv_task(self) -> Task:
#         return Task(
#             config=self.tasks_config["analyze_cv_task"],
#             output_pydantic=CVAnalysis
#         )
#     @task
#     def generate_interview_questions(self) -> Task:
#         return Task(
#             config=self.tasks_config["generate_interview_questions"]
#         )    
#     @task
#     def generate_coding_challenge(self) -> Task:
#         return Task(
#             config=self.tasks_config["generate_coding_challenge"]
#         )

#     @crew
#     def crew(self) -> Crew:
#         return Crew(
#             agents=[
#                 self.cv_analyzer(),
#                 self.interviewer(),
#                 self.answer_grader()
#             ],
#             tasks=[
#                 self.analyze_cv_task(),
#                 self.generate_interview_questions(),
#                 self.generate_coding_challenge()
#             ],
#             verbose=True
#         )
