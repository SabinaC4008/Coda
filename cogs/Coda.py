from discord.ext import commands
import discord
from modules import coda_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import json
import random

class Coda(commands.Cog):
  """Commands for studying using AI agents."""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xcb1aee

    session_service = InMemorySessionService()

    APP_NAME = "coda_app"
    self.USER_ID = "user_1"
    self.SESSION_ID = "session_001"

    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=self.USER_ID,
        session_id=self.SESSION_ID
    )

    # === RUNNER ===
    self.runner = Runner(
        agent=coda_agent, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service # Uses our session manager
    )

  async def call_agent_async(self, query: str, runner, user_id, session_id):
        print(f"Calling agent with query: {query}")
        content = types.Content(role='user', parts=[types.Part(text=query)])
        final_response_text = "Agent did not produce a final response." # Default

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):

            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break # Stop processing events once the final response is found

        return final_response_text

  @commands.command(name="multiple", aliases=["m", "mult"], help="Play command for multiple choice questions.")
  async def multiple(self, ctx, *msg):
    query = " ".join(msg)

    # enviar ejercicio a user

    # TODO: Fetch question and options from Coda
    question_bank = ["""___ square(number):
                        return number * number

                        result = square(5)
                        print(result)""", 
                        
                        """ if x < 5:
                              print("less than")
                            ___ x < 5:
                              print("greater than")
                            else:
                              print("error")""",
                        
                        """when creating an attribute for a python classes, 
                        they should all start with"""]
    answer_choices = [["function", "fun", "def", "func"], 
    ["elif", "else if", "if else", "or"], 
    ["classname.", "own.", "Class.", "self."]] 
    answer_key = ["def", "elif", "self."]

    new_question = random.randint(0,2) # this is only a demo set of questions. ideally
    # the question set would be much larger to prevent repeats.
    question = question_bank[new_question]
    ans_options = answer_choices[new_question]
    correct_answer = answer_key[new_question]

    emoji = {
        "1️⃣": 0,
        "2️⃣": 1,
        "3️⃣": 2,
        "4️⃣": 3
    }
    embed = discord.Embed(
      title="Coda Agent Response",
      description=f"""{question}\n\n
      1️⃣ {ans_options[0]}
      2️⃣ {ans_options[1]}
      3️⃣ {ans_options[2]}
      4️⃣ {ans_options[3]}
      \n\n*Please react with the corresponding emoji to select your answer.*""",
      color=self.COLOR
    )

    message = await ctx.send(embed=embed)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")

    # esperar rpta
    while True:
        def check(reaction, user):
          return (user == ctx.author
                  and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
                  and reaction.message.id == message.id)
        try:
            reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=20.0, check=check)

            answer = ans_options[emoji[str(reaction.emoji)]]
            await message.clear_reactions()
            break

        except:
          await message.clear_reactions()
          # TODO: You took too long
          break

    # mandar a coda
    query = f"""
        exercise_type: 'multiple_choice'
        user_answer: {answer}
        correct_answer_data: {correct_answer}"""

    res = await self.call_agent_async(query=query,
                            runner=self.runner,
                            user_id=self.USER_ID,
                            session_id=self.SESSION_ID)
    print(res)
    print(type(res))
    python_dict = json.loads(res)

    embed = discord.Embed(
        title="Coda Agent Response",
        description=f"""Score: {python_dict.get('score', 'N/A')}\n
        Feedback: {python_dict.get('feedback', 'No feedback provided.')}""",
        color=self.COLOR
    )

    await message.edit(embed=embed)