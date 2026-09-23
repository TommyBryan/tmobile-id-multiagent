from pathlib import Path
from crewai import Agent, Task, LLM
from src.models.intake_model import IntakeOutputContract

def load_prompt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")

# Initialize LLM
claude_llm = LLM(model="anthropic/claude-sonnet-5")

# Load Intake System Prompt from Markdown
intake_prompt = load_prompt("config/agents/01_intake.md")

# Instantiate Agent
intake_agent = Agent(
    role="Intake Screening Agent",
    goal="Pre-screen inbound L&D requests, score urgency, check duplicates, and route without diagnosing.",
    backstory=intake_prompt,
    llm=claude_llm,
    verbose=True
)

def create_intake_task(raw_request_payload: str) -> Task:
    """Creates an Intake Screening Task bound to the Pydantic JSON contract."""
    return Task(
        description=f"Parse and pre-screen the following L&D inbound request:\n\n{raw_request_payload}",
        expected_output="Valid JSON conforming to the IntakeOutputContract schema.",
        agent=intake_agent,
        output_json=IntakeOutputContract
    )
