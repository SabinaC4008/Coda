from discord.ext import commands
import discord
from modules import coda_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import json
import sqlite3
import datetime

class Coda(commands.Cog):
  """Commands for studying using AI agents."""

  def __del__(self):
    self.conexion.close()

  def __init__(self, client):

    self.conexion = sqlite3.connect('game.db')
    self.cursor = self.conexion.cursor()

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            date DATETIME NOT NULL,
            score INTEGER NOT NULL,
            language TEXT NOT NULL,
            server TEXT NOT NULL
        )
    ''')

    self.conexion.commit()

    self.CLIENT = client
    self.COLOR = 0xC1FF72

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
    question = """___ square(number):
  return number * number

result = square(5)
print(result)"""
    ans_options = {
        "1️⃣": "fun",
        "2️⃣": "def",
        "3️⃣": "func",
        "4️⃣": "function"
    }
    correct_answer = "def"

    embed = discord.Embed(
      title="Coda Agent Response",
      description=f"""{question}\n\n
      1️⃣ {ans_options['1️⃣']}
      2️⃣ {ans_options['2️⃣']}
      3️⃣ {ans_options['3️⃣']}
      4️⃣ {ans_options['4️⃣']}
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

            answer = ans_options[str(reaction.emoji)]
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


    self.cursor.execute(
       "INSERT INTO questions (user, date, score, language, server) VALUES (?, ?, ?, ?, ?)",
       (str(ctx.author.display_name), datetime.datetime.now(), python_dict.get('score', 0), 'Python', str(ctx.guild.id))
    )

    self.conexion.commit()

    embed = discord.Embed(
        title="Coda Agent Response",
        description=f"""Score: {python_dict.get('score', 'N/A')}\n
        Feedback: {python_dict.get('feedback', 'No feedback provided.')}""",
        color=self.COLOR
    )
    await message.edit(embed=embed)

  @commands.command(name="leaderboard", aliases=["lead", "l"], help="Show the leaderboard.")
  async def leaderboard(self, ctx):
      self.cursor.execute("SELECT user, sum(score) FROM questions GROUP BY user ORDER BY sum(score) DESC LIMIT 10")
      rows = self.cursor.fetchall()

      embed = discord.Embed(
          title="Leaderboard",
          description="Top 10 users:",
          color=self.COLOR
      )

      i = 1
      for fila in rows:
          embed.add_field(name=f"{i}. {fila[0]}", value=fila[1], inline=False)
          i += 1

      await ctx.send(embed=embed)

  @commands.command(name="fill", aliases=["f"], help="Answer a fill-in-the-blank question.")
  async def fill(self, ctx):

        question = "___ is the keyword used to define a function in Python."
        correct_answer = "def"

        embed = discord.Embed(
            title="coda Agent: Fill in the Blank!",
            description=f"**Question:**\n`{question}`\n\nType your one-word answer in the chat. You have 20 seconds!",
            color=self.COLOR
        )
        message = await ctx.send(embed=embed)

        # esperar rpta
        while True:
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel
            try:
                user_message = await self.CLIENT.wait_for("message", timeout=20.0, check=check)
                user_answer = user_message.content.strip().lower()
                break

            except:
              # TODO: You took too long
              break

        # mandar a coda
        query = f"""
            exercise_type: 'fill_in_the_blank'
            user_answer: {user_answer}
            correct_answer_data: {correct_answer}"""

        res = await self.call_agent_async(query=query,
                                runner=self.runner,
                                user_id=self.USER_ID,
                                session_id=self.SESSION_ID)
        print(res)
        print(type(res))
        python_dict = json.loads(res)


        self.cursor.execute(
          "INSERT INTO questions (user, date, score, language, server) VALUES (?, ?, ?, ?, ?)",
          (str(ctx.author.display_name), datetime.datetime.now(), python_dict.get('score', 0), 'Python', str(ctx.guild.id))
        )

        self.conexion.commit()

        embed = discord.Embed(
            title="Coda Agent Response",
            description=f"""Score: {python_dict.get('score', 'N/A')}\n
            Feedback: {python_dict.get('feedback', 'No feedback provided.')}""",
            color=self.COLOR
        )
        await message.edit(embed=embed)


  @commands.command(name="code", aliases=["c"], help="Code the question.")
  async def code(self, ctx):

        question = "Code a function that returns the sum of two numbers."

        embed = discord.Embed(
            title="coda Agent: Code the Question!",
            description=f"**Question:**\n`{question}`\n\nType your code answer in the chat. You have 2 minutes!",
            color=self.COLOR
        )
        message = await ctx.send(embed=embed)

        # esperar rpta
        while True:
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel
            try:
                user_message = await self.CLIENT.wait_for("message", timeout=120.0, check=check)
                user_answer = user_message.content.strip().lower()
                break

            except:
              # TODO: You took too long
              break

        print(user_answer)

        example_user_code = f"""def add(a, b):
            print('Adding numbers')
            return a + b"""

        example_test_cases = {
            "Test Case 1": {
                "function_name": "add",
                "args": (2, 3),
                "expected_return": 5
            },
            "Test Case 2": {
                "function_name": "add",
                "args": (-1, 1),
                "expected_return": 0
            },
        }

        # mandar a coda
        query = f"""
            exercise_type: 'write_code'
            user_code: {user_answer}
            question: {question}
            test_cases: {example_test_cases}"""

        res = await self.call_agent_async(query=query,
                                runner=self.runner,
                                user_id=self.USER_ID,
                                session_id=self.SESSION_ID)
        print(res)
        print(type(res))
        python_dict = json.loads(res)
        print("______________")
        print(python_dict)
        print(type(python_dict))

        self.cursor.execute(
          "INSERT INTO questions (user, date, score, language, server) VALUES (?, ?, ?, ?, ?)",
          (str(ctx.author.display_name), datetime.datetime.now(), python_dict.get('score', 0), 'Python', str(ctx.guild.id))
        )

        self.conexion.commit()

        embed = discord.Embed(
            title="Coda Agent Response",
            description=f"""Score: {python_dict.get('score', 'N/A')}\n
            Feedback: {python_dict.get('feedback', 'No feedback provided.')}""",
            color=self.COLOR
        )
        await message.edit(embed=embed)
