import os
from typing import Optional
import random
from dotenv import load_dotenv
from utils.checkadminrole import check_admin_role
from tinydb import TinyDB, Query
from tinydb.operations import delete
import posthog

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

DB_LOCATION = os.getenv('DB_LOCATION')
db = TinyDB(DB_LOCATION)

load_dotenv()
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID') or None

posthog.project_api_key = os.getenv('POSTHOG_API_KEY')
posthog.host = 'https://app.posthog.com'


class MochaCommands(commands.GroupCog, name="m"):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    super().__init__()

  @app_commands.command(
    name = "start",
    description = "Sends message to gather users for matching"
  )

  async def start(
    self,
    interaction: discord.Interaction) -> None:

    if not await check_admin_role(interaction):
      return

    # Send match message and react as prompt
    await interaction.response.send_message(
      f'React to this message to be matched'
    )
    message = await interaction.original_response()
    emoji = '👋'
    await message.add_reaction(emoji)
    
    posthog.capture(
      str(interaction.user.id), 
      'start',
      {
        'guildId': interaction.guild.id, 
        'guildName': interaction.guild.name
      }
    )

  @app_commands.command(
    name = "match",
    description = "Runs matching and sends matches"
  )
  @app_commands.describe(
    match_size = "Number of users per match, default is 2 (pairs)",
    leftovers = "What to do with leftover, non-matched users. Default is leaving them out"
  )
  @app_commands.choices(leftovers = [
    Choice(name = "Leave Out (default)", value = "out"),
    Choice(name = "Join to Last Match", value = "join"),
    Choice(name = "Create Smaller Match", value = "smaller")
  ])

  async def match(
    self,
    interaction: discord.Interaction,
    match_size:  Optional[int] = 2,
    leftovers: Optional[str] = 'out') -> None:

    if not await check_admin_role(interaction):
      return

    if match_size <= 1:
      await interaction.response.send_message(
        'The match size must be an integer greater than 1. For example "/m match 3"',
        ephemeral=True
      )
      posthog.capture(
        str(interaction.user.id),
        'match',
        {
          'guildId': interaction.guild.id, 
          'guildName': interaction.guild.name, 
          'error': 'wrong match size'
        }
      )
      return

    # Check for start message
    message_history = interaction.channel.history(
      limit=None
    )
    last_message = None
    async for m in message_history:
      if (m.author.id == self.bot.user.id) and (m.content == 'React to this message to be matched'):
        last_message = m
        break

    # No start message found
    if last_message == None:
      await interaction.response.send_message(
        'Start message not found, please use "/m start" to gather users for matches.',
        ephemeral=True
      )
      posthog.capture(
        str(interaction.user.id),
        'match',
        {
          'guildId': interaction.guild.id, 
          'guildName': interaction.guild.name, 
          'error': 'no start message'
        }
      )
      return
      
    match_list = []
    for reaction in last_message.reactions:
      async for user in reaction.users():
        # Prevent bot and duplicate users from being added to match_list
        if user.id != self.bot.user.id and user.id not in match_list:
          match_list.append(user.id)
    
    if len(match_list) < match_size:
      await interaction.response.send_message(
        f'You need at least {match_size} people to react to create a match.',
        ephemeral=True
      )
      posthog.capture(
        str(interaction.user.id),
        'match',
        {
          'guildId': interaction.guild.id, 
          'guildName': interaction.guild.name,
          'match size': match_size,
          'error': 'not enough users'
        }
      )
      return 

    # Create match groups
    random.shuffle(match_list)
    groups = ([match_list[i:i + match_size] for i in range(0, len(match_list), match_size)])
    embed=discord.Embed(title="Here are the matches ☕")

    # Format match message
    for idx, match in enumerate(groups):
      if len(match) == match_size or (leftovers == 'smaller' and len(match)>1):
        match_msg = f"<@{match[0]}>"
        for matched_user in match[1:]:
          match_msg += f" & <@{matched_user}>"

        if leftovers == 'join' and idx == len(groups) - 2:
          for matched_user in groups[-1]:
            match_msg += f" & <@{matched_user}>"
          
        embed.add_field(
          name='\u200b', value=match_msg, inline=False
        )
        continue

      # Handle "leftover" users
      if leftovers == 'out' or (leftovers == 'smaller' and len(match)==1):
        if len(match) == 1:
          embed.add_field(
            name='\u200b', value=f"<@{match[0]}> is left out :(", inline=False
          )
          continue
        
        left_msg = f"<@{match[0]}>"
        for left_user in match[1:]:
          left_msg += f" & <@{left_user}>"
        left_msg += " are left out :("
        embed.add_field(
          name='\u200b', value=f"{left_msg}", inline=False
        )
      
    emoji = "😀"
    if match_size == 2:
      embed.set_footer(
        text=f"Message your match to get to know them better {emoji}"
      )
    else:
      embed.set_footer(
        text=f"Message your matches to get to know them better {emoji}"
      )
      
    await interaction.response.send_message(
      embed=embed
    )
    posthog.capture(
      str(interaction.user.id),
      'match',
      {
        'guildId': interaction.guild.id, 
        'guildName': interaction.guild.name, 
        'match size': match_size, 
        'matched': len(match_list)
      }
    )
  
  @app_commands.command(
    name = "role",
    description = "Sets admin role for Mocha Match. Send without role to remove."
  )
  @app_commands.describe(
    role="Required admin role for calling commands"
  )

  async def role(
    self,
    interaction: discord.Interaction,
    role: str = None) -> None:

    if not await check_admin_role(interaction):
      return

    # Remove role if none is provided
    if not role:
      # Check if admin_role is set
      Guild = Query()
      guild_rec = db.get(Guild.guild_id == interaction.guild.id)
      if 'admin_role' not in guild_rec.keys():
        await interaction.response.send_message(
          f'No bot admin role set. Anyone can use the commands.',
          ephemeral=True
        )
        return
      # If admin_role is set, remove it
      db.update(delete('admin_role'), Guild.guild_id == interaction.guild.id)
      await interaction.response.send_message(
        f'Bot admin role removed. Anyone can now use the commands.',
        ephemeral=True
      )
      return
  
    # Check if role is an @mention
    if all(c in role for c in ['<', '@', '>']):
      role_id = int(role[3:-1])
      role_data = discord.utils.get(interaction.guild.roles, id=role_id)
      role = role_data.name
  
    # Check if role exists
    if not discord.utils.get(interaction.guild.roles, name=role):
      await interaction.response.send_message(
        f'The "{role}" role does not exist, please make sure you have spelt it correctly (case sensitive).',
        ephemeral=True
      )
      posthog.capture(
        str(interaction.user.id),
        'role',
        {
          'guildId': interaction.guild.id, 
          'guildName': interaction.guild.name,
          'error': 'no role exists'
        }
      )
      return
  
    # Set role in db
    Guild = Query()
    db.upsert(
      {'guild_id': interaction.guild.id, 'admin_role': role}, Guild.guild_id == interaction.guild.id
    )
  
    await interaction.response.send_message(
      f'{role} was set as the admin role for Mocha Match.',
      ephemeral=True
    )
    posthog.capture(
      str(interaction.user.id),
      'role',
      {
        'guildId': interaction.guild.id, 
        'guildName': interaction.guild.name
      }
    )

  @app_commands.command(
    name = "feedback",
    description = "Provide feedback on Mocha Match"
  )
  @app_commands.describe(
    feedback = "Problems or recommendations to improve Mocha Match"
  )

  async def feedback(
    self,
    interaction: discord.Interaction,
    feedback: str) -> None:

    posthog.capture(
      str(interaction.user.id),
      'feedback',
      {
        'guildId': interaction.guild.id, 
        'guildName': interaction.guild.name,
        'feedback': feedback
      }
    )

    await interaction.response.send_message(
      f'Your feedback has been received. Thanks!',
      ephemeral=True
    )

  @app_commands.command(
    name = "help",
    description = "Get details about this bot"
  )

  async def help(
    self,
    interaction: discord.Interaction) -> None:

    embed=discord.Embed(
      title='Mocha Match Help', 
      url='https://www.mochamatch.xyz/'
    )
    embed.add_field(name='/m start', value='Sends message to gather users for matching', inline=False)
    embed.add_field(name='/m match', value='Runs matching and sends message with matches', inline=False)
    embed.add_field(name='/m role', value='Set admin role for using commands', inline=False)
    embed.add_field(name='/m feedback', value='Provide feedback on Mocha Match', inline=False)
    embed.add_field(name='/m help', value='Sends this message', inline=False)
    embed.add_field(
      name='Details', 
      value='Created by [Ian Vanagas](https://ianvanagas.com/) using [discord.py 2.0](https://github.com/Rapptz/discord.py)', 
      inline=False
    )

    await interaction.response.send_message(
      embed=embed,
      ephemeral=True
    )
    posthog.capture(
      str(interaction.user.id),
      'help',
      {
        'guildId': interaction.guild.id, 
        'guildName': interaction.guild.name
      }
    )

async def setup(bot: commands.Bot) -> None:
  if TEST_GUILD_ID:
    await bot.add_cog(
      MochaCommands(bot),
      guilds = [discord.Object(id = int(TEST_GUILD_ID))]
    )
  else:
    await bot.add_cog(
      MochaCommands(bot)
    )
