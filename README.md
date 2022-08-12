# Mocha Match

## Setup
- install python 3.8.10 and poetry from https://python-poetry.org/docs/
- run "poetry install"
- create a top-level folder named data and add a file "testdb.json"
- create a .env file and add DISCORD_TOKEN, APPLICATION_ID, TEST_GUILD_ID, and DB_LOCATION (i.e. data/testdb.json)
- run "poetry run python main.py" to start

## Testing
- run "poetry run python -m pytest tests/"
  - add "-rP" to command to see print messages

## Links
- Main site: https://www.mochamatch.xyz/
- Join link (live): https://discord.com/api/oauth2/authorize?client_id=829578421893070849&permissions=2147552320&scope=bot%20applications.commands
- Join link (dev): https://discord.com/api/oauth2/authorize?client_id=948647613652172891&permissions=2147552320&scope=bot%20applications.commands
- Demo recording: https://www.loom.com/share/0c447690d10e41aaa47644e8b83bf2bb
- Test server: https://discord.gg/tvaUg83AKb
- Top.gg link: https://top.gg/bot/829578421893070849
- Notion link: https://www.notion.so/ianv/Discord-Matcher-Mocha-Match-f8d02b95155f43f2b720acb03f6c29e7

## Permissions Needed
- scopes: bot, application.commands
- bot permissions: Read Messages/View Channels, Send Messages, Read Message History, Add Reactions, Use Slash Commands

## Other
To install the discord package in poetry, run "poetry add git+https://github.com/Rapptz/discord.py"
