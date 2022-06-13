import os

from discord.ext import commands
from discord.utils import find
import discord
from utils.mochalogger import getLogger


TOKEN = os.environ['DISCORD_TOKEN']
TEST_GUILD_ID = os.environ['TEST_GUILD_ID']
APPLICATION_ID = os.environ['APPLICATION_ID']

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

log = getLogger()

class MochaBot(commands.Bot):

  def __init__(self):
    super().__init__(
      command_prefix='/m ',
      intents = discord.Intents.default(),
      application_id = APPLICATION_ID
    )

  async def setup_hook(self):
    await self.load_extension(f"cogs.commands")
    await bot.tree.sync()

  async def on_ready(self):
    print(f'{self.user} has connected to Discord!')

bot = MochaBot()

@bot.event
async def on_guild_join(guild):
  log.info(f"guild:{guild.id}({guild.name}) - cmd:join")
  general = find(lambda x: x.name == 'general',  guild.text_channels)
  if general and general.permissions_for(guild.me).send_messages:
    await general.send(
      f'Hello {guild.name}! Use `/m start` to gather users for matching and `/m match` to pair them up.'
    )

def run():
  bot.run(TOKEN)

if __name__ == "__main__":
  run()

