import json
from dataclasses import dataclass
from typing import Any

from crewai import Agent, Crew, Process, Task

from employee_info_fetcher.agents import (
    all_agents,
    exp_agent,
    funfact_agent,
    hr_agent,
    linkedin_agent,
    manager,
)

_RECORD_PREFIX = (
    "Use only the fields below. Do not invent or assume missing data.\n\n"
    "Fields:\n{fields_json}\n\n"
)


@dataclass(frozen=True)
class SpecialistTaskSpec:
    agent: Agent
    fields: tuple[str, ...]
    instruction: str
    expected_output: str


SPECIALIST_SPECS: tuple[SpecialistTaskSpec, ...] = (
    SpecialistTaskSpec(
        agent=hr_agent,
        fields=("name", "department", "role", "date_joined"),
        instruction="Report department, role, and date joined.",
        expected_output="Department, role, and joining date.",
    ),
    SpecialistTaskSpec(
        agent=exp_agent,
        fields=("name", "experience"),
        instruction="Summarize work experience.",
        expected_output="Short summary of prior roles and companies.",
    ),
    SpecialistTaskSpec(
        agent=linkedin_agent,
        fields=("name", "linkedin"),
        instruction="Report the LinkedIn profile URL.",
        expected_output="LinkedIn URL from the record.",
    ),
    SpecialistTaskSpec(
        agent=funfact_agent,
        fields=("name", "fun_fact"),
        instruction="Report fun facts or hobbies.",
        expected_output="A few lines describing hobbies or personal interests.",
    ),
)


def _field_slice(employee: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {key: employee[key] for key in fields if key in employee}


def _specialist_task(spec: SpecialistTaskSpec, employee: dict[str, Any]) -> Task:
    fields_json = json.dumps(_field_slice(employee, spec.fields), indent=2)
    description = f"{_RECORD_PREFIX.format(fields_json=fields_json)}{spec.instruction}"
    return Task(
        agent=spec.agent,
        description=description,
        expected_output=spec.expected_output,
    )


def build_crew(employee: dict[str, Any], *, verbose: bool = False) -> Crew:
    display_name = employee.get("name", "the employee")
    specialist_tasks = [_specialist_task(spec, employee) for spec in SPECIALIST_SPECS]

    synthesis = Task(
        agent=manager,
        description=(
            f"Using the specialist reports for {display_name}, write one cohesive employee "
            "profile with sections: Overview, Experience, Public profile, Personal interests. "
            "Do not add information that was not in the specialist outputs."
        ),
        expected_output="A single formatted employee profile.",
        context=specialist_tasks,
    )

    return Crew(
        agents=all_agents,
        tasks=[*specialist_tasks, synthesis],
        process=Process.sequential,
        verbose=verbose,
    )
