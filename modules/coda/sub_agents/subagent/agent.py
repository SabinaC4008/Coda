from google.adk.agents import Agent
#from .tools import evaluate_code
from .prompts import return_instructions

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

coda_sub_agent = None
try:
    coda_sub_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="coda_sub_agent",
        instruction=return_instructions(),
        description="Analyzes and scores user-submitted code for correctness by running it against a predefined set of test cases.",
        #tools=[evaluate_code],
    )
    print(f"✅ Agent '{coda_sub_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")
except Exception as e:
    print(f"❌ Could not create coda sub agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")