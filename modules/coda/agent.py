from google.adk.agents import Agent
from .tools import DirectVerificationTool
from .sub_agents import coda_sub_agent
from .prompts import return_instructions, return_description

import warnings
warnings.filterwarnings("ignore")

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="coda_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description=return_description(),
    instruction=return_instructions(),
    tools=[DirectVerificationTool],
    sub_agents=[coda_sub_agent]
)
