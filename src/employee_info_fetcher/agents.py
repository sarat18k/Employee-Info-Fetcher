from dataclasses import dataclass

from crewai import Agent


@dataclass(frozen=True)
class AgentSpec:
    role: str
    goal: str
    backstory: str
    allow_delegation: bool = False


def _build_agent(spec: AgentSpec) -> Agent:
    return Agent(
        role=spec.role,
        goal=spec.goal,
        backstory=spec.backstory,
        allow_delegation=spec.allow_delegation,
        verbose=False,
    )


MANAGER_SPEC = AgentSpec(
    role="Employee Profile Coordinator",
    goal="Combine specialist reports into one accurate employee profile.",
    backstory=(
        "You merge HR, experience, public profile, and personal-interest reports "
        "into a single cohesive summary without adding facts that were not provided."
    ),
    allow_delegation=False,
)

HR_SPEC = AgentSpec(
    role="Internal Info Specialist",
    goal="Report department, role, and joining date from the provided fields.",
    backstory="You extract structured HR fields from internal records.",
)

EXP_SPEC = AgentSpec(
    role="Experience Specialist",
    goal="Summarize work experience from the provided fields.",
    backstory="You turn experience history into a concise professional summary.",
)

LINKEDIN_SPEC = AgentSpec(
    role="Public Profile Specialist",
    goal="Report the LinkedIn URL from the provided fields.",
    backstory="You surface public professional profile links from internal records.",
)

FUNFACT_SPEC = AgentSpec(
    role="Personal Interests Specialist",
    goal="Report fun facts or hobbies from the provided fields.",
    backstory="You highlight personal details that make profiles more human.",
)

manager = _build_agent(MANAGER_SPEC)
hr_agent = _build_agent(HR_SPEC)
exp_agent = _build_agent(EXP_SPEC)
linkedin_agent = _build_agent(LINKEDIN_SPEC)
funfact_agent = _build_agent(FUNFACT_SPEC)

worker_agents = [hr_agent, exp_agent, linkedin_agent, funfact_agent]
all_agents = worker_agents + [manager]
