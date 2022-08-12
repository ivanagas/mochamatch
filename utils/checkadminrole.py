from tinydb import TinyDB, Query
import os

DB_LOCATION = os.getenv('DB_LOCATION')
db = TinyDB(DB_LOCATION)

async def check_admin_role(interaction):
  # Check if admin role exists, if not return True (that command can be used).
  # If admin role exists, check that the command author has the role.
  # If not, send requirement message and return false (that command can't be used).

  # Check if admin role exists
  Guild = Query()
  guild_rec = db.get(Guild.guild_id == interaction.guild.id)
  if guild_rec == None:
    return True
  if 'admin_role' in guild_rec:
    admin_role = guild_rec['admin_role']
  else:
    return True

  # Check if user has admin role
  command_permission = False
  for role in interaction.user.roles:
    if role.name == admin_role:
      command_permission = True

  if not command_permission:
    await interaction.response.send_message(
      f'You require the {admin_role} role to use this command.',
      ephemeral=True
    )
    return False
  return True
