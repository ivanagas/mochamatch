import os
import random
import logging
from dotenv import load_dotenv

from discord.ext import commands
from discord.utils import find
from discord.ext.commands import has_permissions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(format)
logger.addHandler(handler)

bot = commands.Bot(command_prefix='/m ', help_command = help_command)


@bot.event
async def on_ready():
  print('Mocha Match running...')

@bot.event
async def on_guild_join(guild):
  logger.info(f"guild:{guild.id}({guild.name}) - cmd:join")
  general = find(lambda x: x.name == 'general',  guild.text_channels)
  if general and general.permissions_for(guild.me).send_messages:
    await general.send('Hello {}! Users with application commands permissions can use `/m start` to gather users for matching and `/m match` to pair them up. Use `/m help` if you forget.'.format(guild.name))

@bot.command(name='start', help='Sends message to gather users for matching')
@has_permissions(use_slash_commands=True)
async def start(ctx):
  response = 'React to this message to be matched'
  message = await ctx.send(response)

  emoji = '👋'
  await message.add_reaction(emoji)

  logger.info(f"guild:{ctx.guild.id}({ctx.guild.name}) - user:{ctx.author.id} - cmd:start")
    
@bot.command(name='match', help='Runs matching and sends messages with pairs')
@has_permissions(use_slash_commands=True)
async def match(ctx, match_size=2):

  if match_size <= 1:
    await ctx.send('The match size must be an integer greater than 1. For example "/m match 3"')
    logger.info(f"guild:{ctx.guild.id}({ctx.guild.name}) - user:{ctx.author.id} - cmd:match - error:matchsize")
    return

  last_message = await ctx.message.channel.history(limit=None).find(lambda m: (m.author.id == bot.user.id) and (m.content == 'React to this message to be matched'))
  if last_message == None:
    await ctx.send('Start message not found, please use "/m start" to gather users for matches.')
    logger.info(f"guild:{ctx.guild.id}({ctx.guild.name}) - user:{ctx.author.id} - cmd:match - error:nomessage")
    return

  match_list = []
  for reaction in last_message.reactions:
    async for user in reaction.users():
      # Prevent bot and duplicate users from being added to match_list
      if user.id != bot.user.id and user.id not in match_list:
        match_list.append(user.id)

  logger.info(f"guild:{ctx.guild.id}({ctx.guild.name}) - user:{ctx.author.id} - cmd:match - matchsize:{match_size} - matched:{len(match_list)}")
  
  if len(match_list) < match_size:
    await ctx.send(f'You need at least {match_size} people to react to create a match.')
    return

  random.shuffle(match_list)
  pairs = ([match_list[i:i + match_size] for i in range(0, len(match_list), match_size)])
  message = await ctx.send('Here are the matches:')
  
  for match in pairs:
    if len(match) == match_size:
      match_msg = f"<@{match[0]}>"
      for matched_user in match[1:]:
        match_msg += f" & <@{matched_user}>"
      await message.channel.send(match_msg)
      continue

    if len(match) == 1:
      await message.channel.send(f"<@{match[0]}> is left out :(")
      continue
    
    left_msg = f"<@{match[0]}>"
    for left_user in match:
      left_msg += f" & <@{left_user}>"
    left_msg += " are left out :("
    await message.channel.send(left_msg)
  
  emoji = "😀"
  if match_size == 2:
    await message.channel.send("Message your match to get to know them better {}".format(emoji))
    return
  await message.channel.send("Message your matches to get to know them better {}".format(emoji))

@bot.command(name='feedback', help='Provide feedback on Mocha Match')
@has_permissions(use_slash_commands=True)
async def feedback(ctx):
  feedback = ctx.message.clean_content[12:]
  if feedback:
    feedback += '\n'
    with open('feedback.txt', 'a') as f:
      f.write(feedback)
      f.close()
    await ctx.send('Your feedback has been received. Thanks!', delete_after=10)


bot.run(TOKEN)
