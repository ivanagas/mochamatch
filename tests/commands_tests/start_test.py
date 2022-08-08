import pytest
from cogs.commands import MochaCommands

@pytest.mark.asyncio
async def test_start_command(bot, base_interaction):
  command = MochaCommands(bot).start
  call = await command.callback(self=command, interaction=base_interaction)
  assert call == None
