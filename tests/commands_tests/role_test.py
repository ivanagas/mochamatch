import pytest
from cogs.commands import MochaCommands
from tinydb import Query


@pytest.mark.asyncio
async def test_role_command(bot, base_interaction, db):
  # Changes admin_role in DB to role provided
  BeforeGuild = Query()
  before_guild_rec = db.get(BeforeGuild.guild_id == base_interaction.guild.id)
  
  command = MochaCommands(bot).role
  await command.callback(self=command, interaction=base_interaction, role='BetterMod')
  
  AfterGuild = Query()
  after_guild_rec = db.get(AfterGuild.guild_id == base_interaction.guild.id)
  
  assert (after_guild_rec['admin_role'] == base_interaction.guild.roles[1].name
         and before_guild_rec['admin_role'] != after_guild_rec['admin_role'])

@pytest.mark.asyncio
async def test_mention_role_command(bot, base_interaction, db):
  # Changes admin_role in DB to @mentioned role provided
  BeforeGuild = Query()
  before_guild_rec = db.get(BeforeGuild.guild_id == base_interaction.guild.id)
  
  command = MochaCommands(bot).role
  await command.callback(self=command, interaction=base_interaction, role='<@&2>')
  
  AfterGuild = Query()
  after_guild_rec = db.get(AfterGuild.guild_id == base_interaction.guild.id)
  
  assert (after_guild_rec['admin_role'] == base_interaction.guild.roles[1].name
         and before_guild_rec['admin_role'] != after_guild_rec['admin_role'])

@pytest.mark.asyncio
async def test_wrong_role_set(bot, base_interaction, db):
  # Doesn't change admin_role when nonexistent role is provided
  BeforeGuild = Query()
  before_guild_rec = db.get(BeforeGuild.guild_id == base_interaction.guild.id)

  command = MochaCommands(bot).role
  await command.callback(self=command, interaction=base_interaction, role='wrong')
  
  AfterGuild = Query()
  after_guild_rec = db.get(AfterGuild.guild_id == base_interaction.guild.id)
  
  assert before_guild_rec['admin_role'] == after_guild_rec['admin_role']

@pytest.mark.asyncio
async def test_no_role(bot, base_interaction, db):
  # Removes admin_role when no role is provided
  base_interaction.guild.id = 1491 # Guild ID for data to modify
  BeforeGuild = Query()
  before_guild_rec = db.get(BeforeGuild.guild_id == base_interaction.guild.id)

  command = MochaCommands(bot).role
  await command.callback(self=command, interaction=base_interaction)
  
  AfterGuild = Query()
  after_guild_rec = db.get(AfterGuild.guild_id == base_interaction.guild.id)
  
  assert ('admin_role' in before_guild_rec.keys() 
          and 'admin_role' not in after_guild_rec.keys())
