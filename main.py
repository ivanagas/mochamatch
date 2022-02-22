import os
import random

import discord
from dotenv import load_dotenv

from discord.ext import commands
from discord.utils import find
from discord.ext.commands import has_permissions

# join links
# https://discord.com/api/oauth2/authorize?client_id=829578421893070849&permissions=68672&scope=bot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

bot = commands.Bot(command_prefix='/m ', help_command = help_command)

@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}! Users with application commands permissions can use `/m start` to gather users for matching and `/m match` to pair them up. Use `/m help` if you forget.'.format(guild.name))

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@bot.command(name='start', help='Sends message to gather users for matching')
@has_permissions(use_slash_commands=True)
async def start(ctx):
    response = 'React to this message to be matched'
    message = await ctx.send(response)

    emoji = '👋'
    await message.add_reaction(emoji)

@bot.command(name='match', help='Runs matching and sends messages with pairs')
@has_permissions(use_slash_commands=True)
async def match(ctx):

    last_message = await ctx.message.channel.history().find(lambda m: (m.author.id == bot.user.id) and (m.content == 'React to this message to be matched'))
    if last_message == None:
        await ctx.send('Start message not found, please use "/m start" to gather users for matches.')
        return

    match_list = []
    for reaction in last_message.reactions:
        async for user in reaction.users():
            if user.id != bot.user.id and user.id not in match_list:
                match_list.append(user.id)
    
    if len(match_list) <= 1:
        await ctx.send('You need at least 2 people to react to create a match.')
        return

    random.shuffle(match_list)
    pairs = ([match_list[i:i + 2] for i in range(0, len(match_list), 2)])
    message = await ctx.send('Here are the matches:')
    for match in pairs:
        if len(match) == 2:
            await message.channel.send(f"<@{match[0]}> & <@{match[1]}>")
            continue
        await message.channel.send(f"<@{match[0]}> is left out :(")
    emoji = "😀"
    await message.channel.send("Message your match to get to know them better {}".format(emoji))
    
bot.run(TOKEN)

