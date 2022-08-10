import pytest
from main import MochaBot
import discord


@pytest.fixture(name="bot", scope="function")
async def _bot():
  async with MochaBot() as bot:
    yield bot

@pytest.fixture
def base_interaction():
  class TestInteraction:
    def __init__(self):
      self.guild = TestGuild()
      self.user = TestUser()
      self.channel = TestCategoryChannel(id=16121612, name="test", position=0)
    
    @property
    def response(self):
      return TestInteractionResponse(self)
    
    async def original_response(self):
      return TestInteractionMessage(self)
  
  class TestGuild():
    def __init__(self):
      self.id = 1612
      self.channels = [
        TestCategoryChannel(id=16121612, name="test", position=0)
      ]
      self.name = "Test"
  
  class TestCategoryChannel(discord.TextChannel):
    def __init__(self, id, name, position):
      self.id = id
      self.name = name
      self.position = position
  
  class TestUser():
    def __init__(self):
      self.id = 1

  class TestInteractionResponse():
    def __init__(self, parent):
      self._parent = parent
    
    async def send_message(self, msg=None, ephemeral=False, view=None, embed=None):
      return

  class TestInteractionMessage():
    def __init__(self, parent):
      self._parent = parent
    
    async def add_reaction(self, emoji):
      return

  interaction = TestInteraction()
  return interaction
