import os
from dotenv import load_dotenv
import posthog
from quart import Quart

from discord.ext import commands
from discord.utils import find
import discord

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN']
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID') or None
APPLICATION_ID = os.environ['APPLICATION_ID']

posthog.project_api_key = os.getenv('POSTHOG_API_KEY')
posthog.host = 'https://app.posthog.com'

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

class MochaBot(commands.Bot):

  def __init__(self):
    super().__init__(
      command_prefix='/m ',
      intents = discord.Intents.default(),
      application_id = APPLICATION_ID
    )

  async def setup_hook(self):
    bot.loop.create_task(app.run_task('0.0.0.0'))
    await self.load_extension(f"cogs.commands")
    if TEST_GUILD_ID:
      await bot.tree.sync(guild = discord.Object(id = int(TEST_GUILD_ID)))
    else:
      await bot.tree.sync()

  async def on_ready(self):
    print(f'{self.user} has connected to Discord!')

bot = MochaBot()
app = Quart(__name__)

@app.route("/")
async def home():
  return 'hi'

@bot.event
async def on_guild_join(guild):
  posthog.capture(
    guild.id, 
    'join',
    {'guildId': guild.id, 'guildName': guild.name}
  )
  general = find(lambda x: x.name == 'general',  guild.text_channels)
  if general and general.permissions_for(guild.me).send_messages:
    await general.send(
      f'Hello {guild.name}! Use `/m start` to gather users for matching and `/m match` to match them up.'
    )

def run():
  bot.run(TOKEN)

if __name__ == "__main__":
  run()
