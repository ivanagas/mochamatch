import pytest
from cogs.commands import MochaCommands

@pytest.mark.asyncio
async def test_help_command(bot, base_interaction):
  command = MochaCommands(bot).help
  call = await command.callback(self=command, interaction=base_interaction)
  assert call == None
