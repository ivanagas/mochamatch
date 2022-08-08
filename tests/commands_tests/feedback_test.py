import pytest
from cogs.commands import MochaCommands

@pytest.mark.asyncio
async def test_feedback_command(bot, base_interaction):
  command = MochaCommands(bot).feedback
  feedback_message = "testing"

  with open('feedback.txt') as f:
    initial_length = len(f.readlines())
    f.close()

  call = await command.callback(
    self=command,
    interaction=base_interaction,
    feedback=feedback_message
  )
  
  # Check that the feedback is the length of the message longer
  # and that the last piece of feedback is the message
  with open('feedback.txt') as f:
    line_list = f.readlines()
    after_length = len(line_list)
    last_value = line_list[-1]
    f.close()
  
  assert (call == None and after_length == initial_length + 1 
          and feedback_message in last_value)
