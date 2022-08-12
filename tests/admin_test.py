from utils.checkadminrole import check_admin_role
import pytest


@pytest.mark.asyncio
async def test_no_admin_role(base_interaction):
  # Command runs if no admin_role is set
  base_interaction.guild.id = 1984
  assert await check_admin_role(base_interaction)

@pytest.mark.asyncio
async def test_right_admin_role(base_interaction):
  # Command runs if interaction has correct admin_role
  assert await check_admin_role(base_interaction)

@pytest.mark.asyncio
async def test_wrong_admin_role(base_interaction):
  # Command doesn't run if interaction has wrong admin_role
  base_interaction.guild.id = 1738
  assert not await check_admin_role(base_interaction)
