import os
import random

import discord
from dotenv import load_dotenv

from discord.ext import commands
from discord.utils import find
from discord.ext.commands import has_permissions


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
async def match(ctx, match_size=2):

    if match_size <= 1:
        await ctx.send('The match size must be an integer greater than 1. For example "/m match 3"')
        return

    last_message = await ctx.message.channel.history(limit=None).find(lambda m: (m.author.id == bot.user.id) and (m.content == 'React to this message to be matched'))
    if last_message == None:
        await ctx.send('Start message not found, please use "/m start" to gather users for matches.')
        return

    match_list = []
    for reaction in last_message.reactions:
        async for user in reaction.users():
            if user.id != bot.user.id and user.id not in match_list:
                match_list.append(user.id)
    
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


bot.run(TOKEN)

