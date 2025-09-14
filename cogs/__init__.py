from .Help import Help
from .Coda import Coda

cogs_list = [
  Help,
  Coda
]

async def setup(client):
  for cog in cogs_list:
    await client.add_cog(cog(client))