# Discordbot

My first discord bot created using python, with some moderation commands and a youtube notifier for the channel "Absolute".

## Setup/Usage

### Requirements

- Python version 3.5.3 or higher
- Pip

Install the pip requirements with:

`pip install -r requirements.txt`

### Required environment variables

Create a .env file in the same folder where the `main.py` file is located and add these lines:

```
DISCORD_TOKEN={Your bot's discord token here}
YOUTUBE_API_KEY={Your project's youtube api key here}
BOT_ENV=development/production
```

Replace the text between the brackets with the actual tokens, you have to get those from discord and from google.

> Note: The Youtube API Key is only required if you want the notifier to work.

Alternatively, add the environment variables with export from your terminal:

```
export DISCORD_TOKEN={Your bot's discord token here}
export YOUTUBE_API_KEY={Your project's youtube api key here}
BOT_ENV=development/production
```

### Creating the databases

Run the python interpreter in the same folder and enter the following:

```python
>>> import db
>>> db.create_all()
```

---

Then run main.py:

`python main.py`
