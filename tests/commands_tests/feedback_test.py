import pytest
from cogs.commands import MochaCommands

@pytest.mark.asyncio
async def test_feedback_command(bot, base_interaction):
  command = MochaCommands(bot).feedback
  feedback_message = "testing"

  call = await command.callback(self=command, interaction=base_interaction, feedback=feedback_message)
  assert call == None
