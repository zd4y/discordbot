from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')


def get_prefix(bot, msg):
    guild_id = str(msg.guild.id)
    with open('config.json') as file:
        config = json.load(file)
    try:
        prefix = config[guild_id]['prefix']
    except KeyError:
        prefix = config['default']['prefix']
    return prefix


def set_prefix(msg, *args):
    guild_id = str(msg.guild.id)
    with open('config.json') as file:
        config = json.load(file)
    try:
        config[guild_id]
    except KeyError:
        config[guild_id] = {}
    if len(args) == 1 and args[0] == '!' and list(config[guild_id].keys()) == ['prefix']:
        config.pop(guild_id, None)
    else:
        config[guild_id]['prefix'] = list(args)
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=2)
