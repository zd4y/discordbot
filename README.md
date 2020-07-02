# Discordbot

![Python v3.5.3+](https://img.shields.io/badge/python-v3.5.3+-blue)
![License: MIT](https://img.shields.io/github/license/zd4y/discordbot)

My first discord bot created using python, with some moderation commands and a youtube notifier for any channel.

**To do:**

- [ ] Translate messages to english

## Setup/Usage

### Requirements

- Python version 3.7 or higher
- Pip

Install the pip requirements with `pip install -r requirements.txt`

### Required environment variables

Create a `.env` file in the same folder where the `bot` folder is located and add these lines:

```
DISCORD_TOKEN={Your bot's discord token here}
YOUTUBE_API_KEY={Your project's youtube api key here}
DATABASE_URL={your database's URL}
DEFAULT_SETTINGS={"prefix": "!", "debug": false}
LOOP_MINUTES=30
DEVELOPERS_ID=[123, 456]
```

`DEVELOPERS_ID` is a json list of the discord id of each developer who has access to commands like `!reload` and `!debug` as an integer.

Replace the text between the brackets with the actual tokens, you have to get those from [discord](https://discordapp.com/developers/applications/) and from [google](https://console.developers.google.com/).

> Note: The Youtube API Key is only required if you want the notifier and the youtube commands to work.

Alternatively, add the environment variables with `export` from your terminal (If you are on Windows, use `set` instead).

### Creating the databases

Create the database using `alembic upgrade head`

### Running the bot

To start the bot use `python -m bot`
