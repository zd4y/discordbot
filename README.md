# Discordbot

My first discord bot created using python, with some moderation commands and a youtube notifier for the channel "Absolute".

To do:

- [ ] Use a database instead of a json file

## Setup/Usage

### Requirements

- Python version 3.5.3 or higher
- Pip

Install the pip requirements with:

`pip install -r requirements.txt`

### Required environment variables

Create a .env file in the same folder where main.py is located and add this lines:

```
DISCORD_TOKEN={Your bot's discord token here}
YT_API_KEY={Your project's youtube api key here}
```

Replace the text between the brackets with the actual tokens, you have to get those from discord and from google.

Alternatively, add the environment variables with export:

```
export DISCORD_TOKEN={Your bot's discord token here}
export YT_API_KEY={Your project's youtube api key here}
```

Then run main.py:

`python main.py`