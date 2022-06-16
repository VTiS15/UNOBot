# Import statements
import warnings
import asyncio
import discord
import json
import boto3
import sys
from typing import Union
from os import getenv
from treelib import Tree
from math import comb, e, ceil
from botocore.exceptions import ClientError
from aiohttp.client_exceptions import ClientOSError
from treelib.exceptions import DuplicatedNodeIdError
from scipy.stats import rankdata
from copy import deepcopy
from discord import Option, SelectOption
from discord.ui import Button, View, Select
from discord.ext import commands
from discord.ext.commands import has_permissions
from collections import OrderedDict
from PIL import Image
from io import BytesIO
from datetime import datetime
from random import sample, choice
from re import search, sub, I
from discord.ext.commands import UserConverter, RoleConverter, BadArgument
from discord import ApplicationContext, User, Member, Guild, TextChannel

warnings.filterwarnings("ignore", category=DeprecationWarning)

prefix = '/u-'  # Prefix used in bot commands
client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all(),
                      debug_guilds=[getenv('TEST_GUILD_1'), getenv('TEST_GUILD_2')])  # Instantiates a Discord bot class
client.remove_command('help')  # Removes the default help command in Pycord
default_dgs = {
    "DrawUntilMatch": False,
    "QuickStart": False,
    "SpectateGame": False,
    "StackCards": False,
    "Flip": False,
    "7-0": False,
    "StartingCards": 7
}
default_command_settings = {
    'startgame': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'endgame': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': True,
        'Whitelist': None,
        'BlacklistEnabled': False,
        'Blacklist': None
    },
    'joingame': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'leavegame': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'kick': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': True,
        'Whitelist': None,
        'BlacklistEnabled': False,
        'Blacklist': None
    },
    'spectate': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'stats': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'globalstats': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'leaderboard': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'globalleaderboard': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': False,
        'Whitelist': None,
        'BlacklistEnabled': True,
        'Blacklist': None
    },
    'settings': {
        'Enabled': True,
        'Cooldown': 0,
        'WhitelistEnabled': True,
        'Whitelist': None,
        'BlacklistEnabled': False,
        'Blacklist': None
    }
}
cmds = {'startgame', 'endgame', 'joingame', 'leavegame', 'kick', 'spectate', 'stats', 'globalstats', 'leaderboard',
        'globalleaderboard', 'options', 'commands', 'settings'}
cards = ['blue0', 'blue1', 'blue2', 'blue3', 'blue4', 'blue5', 'blue6', 'blue7', 'blue8', 'blue9', 'bluereverse',
         'blueskip', 'blue+2',
         'blue1', 'blue2', 'blue3', 'blue4', 'blue5', 'blue6', 'blue7', 'blue8', 'blue9', 'bluereverse', 'blueskip',
         'blue+2',
         'green0', 'green1', 'green2', 'green3', 'green4', 'green5', 'green6', 'green7', 'green8', 'green9',
         'greenreverse', 'greenskip', 'green+2',
         'green1', 'green2', 'green3', 'green4', 'green5', 'green6', 'green7', 'green8', 'green9', 'greenreverse',
         'greenskip', 'green+2',
         'red0', 'red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'red7', 'red8', 'red9', 'redreverse', 'redskip',
         'red+2',
         'red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'red7', 'red8', 'red9', 'redreverse', 'redskip', 'red+2',
         'yellow0', 'yellow1', 'yellow2', 'yellow3', 'yellow4', 'yellow5', 'yellow6', 'yellow7', 'yellow8',
         'yellow9',
         'yellowreverse', 'yellowskip', 'yellow+2',
         'yellow1', 'yellow2', 'yellow3', 'yellow4', 'yellow5', 'yellow6', 'yellow7', 'yellow8', 'yellow9',
         'yellowreverse', 'yellowskip', 'yellow+2',
         'wild', 'wild', 'wild', 'wild', '+4', '+4', '+4', '+4']
flip_cards = [('blue1', 'purpleskip'), ('blue2', 'pink6'), ('blue3', 'purple8'), ('blue4', 'purple1'),
              ('blue5', 'pink9'), ('blue6', 'purplereverse'), ('blue7', 'orangeskip'), ('blue8', 'tealreverse'),
              ('blue9', 'orange5'), ('bluereverse', 'orange4'),
              ('blueskip', 'pink9'), ('blue+1', 'pink6'), ('blueflip', 'purple7'),
              ('blue1', 'purpleskip'), ('blue2', 'orange8'), ('blue3', 'teal2'), ('blue4', 'teal+5'),
              ('blue5', 'orangereverse'), ('blue6', 'tealskip'), ('blue7', 'orange3'), ('blue8', 'teal4'),
              ('blue9', 'purpleflip'), ('bluereverse', 'darkwild'), ('blueskip', 'teal1'),
              ('blue+1', 'teal6'), ('blueflip', 'purple6'),
              ('green1', 'orangeflip'), ('green2', 'teal+5'), ('green3', 'purple2'), ('green4', 'teal9'),
              ('green5', 'orange7'), ('green6', '+color'), ('green7', 'orange6'), ('green8', 'teal9'),
              ('green9', 'orange+5'),
              ('greenreverse', 'pink7'), ('greenskip', 'orange9'), ('green+1', 'teal6'), ('greenflip', '+color'),
              ('green1', 'orange5'), ('green2', 'tealskip'), ('green3', 'pinkflip'), ('green4', 'pink8'),
              ('green5', 'teal4'), ('green6', 'pink5'), ('green7', 'teal2'), ('green8', 'pinkreverse'),
              ('green9', 'pinkreverse'), ('greenreverse', 'orange1'),
              ('greenskip', 'purple4'), ('green+1', 'orange6'), ('greenflip', 'teal3'),
              ('red1', 'pink3'), ('red2', 'purple+5'), ('red3', '+color'), ('red4', 'purple+5'), ('red5', 'pink2'),
              ('red6', 'pinkskip'), ('red7', 'purple5'), ('red8', 'purplereverse'), ('red9', 'purple5'),
              ('redreverse', 'purple3'), ('redskip', 'darkwild'),
              ('red+1', 'pink4'), ('redflip', 'purple3'),
              ('red1', 'purple2'), ('red2', 'orangereverse'), ('red3', 'pink7'), ('red4', 'orangeflip'),
              ('red5', 'teal5'), ('red6', 'orange9'), ('red7', 'orange1'), ('red8', 'teal7'),
              ('red9', 'tealreverse'), ('redreverse', 'teal7'), ('redskip', 'orange+5'), ('red+1', 'pink3'),
              ('redflip', 'pink8'),
              ('yellow1', 'darkwild'), ('yellow2', 'teal1'), ('yellow3', 'purple1'), ('yellow4', 'purpleflip'),
              ('yellow5', 'teal8'), ('yellow6', '+color'), ('yellow7', 'purple6'), ('yellow8', 'pink1'),
              ('yellow9', 'teal5'),
              ('yellowreverse', 'darkwild'), ('yellowskip', 'tealflip'), ('yellow+1', 'pink1'),
              ('yellowflip', 'orange8'),
              ('yellow1', 'pinkskip'), ('yellow2', 'teal8'), ('yellow3', 'pink+5'), ('yellow4', 'pink+5'),
              ('yellow5', 'purple9'), ('yellow6', 'orangeskip'), ('yellow7', 'orange2'), ('yellow8', 'orange2'),
              ('yellow9', 'purple4'),
              ('yellowreverse', 'tealflip'), ('yellowskip', 'orange3'), ('yellow+1', 'purple8'),
              ('yellowflip', 'pink4'),
              ('wild', 'pinkflip'), ('wild', 'purple7'), ('wild', 'pink5'), ('wild', 'teal3'), ('+2', 'orange4'),
              ('+2', 'pink2'), ('+2', 'purple9'), ('+2', 'orange7')]
bot_names = ['Doggo', 'Mushroom', 'Chin', 'Dragon', 'Crab', 'Matt', 'Susan', 'Carrie', 'Richard', 'Joe']  # Possible names of a bot
resets = []  # List of guilds who wish to reset their data but have not yet confirmed
cooldowns = {}  # Dictionary of command cooldowns
games = {}  # Dictionary of ongoing games' data
stack = {}  # Remembers guilds' card stacking
ending = []  # List of guilds whose games are ending
# Amazon Web Services stuff because the configuration files are stored in an AWS S3 bucket
s3_client = boto3.client('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))
s3_resource = boto3.resource('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))
sys.setrecursionlimit(10 ** 6)  # Changes the system recursion limit to 1,000,000 for the AI


def main():
    """
    Runs the Discord bot.
    """
    try:
        client.run(getenv('BOT_TOKEN'))
    except discord.ext.commands.CommandNotFound or discord.Forbidden:
        pass


async def initialize():
    """
    Initializes the bot.
    """

    # Load default game settings of guilds
    try:
        s3_resource.Object('unobot-bucket', 'dgs.json').load()
    except ClientError:
        s3_client.put_object(Bucket='unobot-bucket', Key='dgs.json', Body=b'{}')
    dgs_file = s3_resource.Object('unobot-bucket', 'dgs.json')
    dgs = json.loads(dgs_file.get()['Body'].read().decode('utf-8'))

    # Load user settings
    try:
        s3_resource.Object('unobot-bucket', 'users.json').load()
    except ClientError:
        s3_client.put_object(Bucket='unobot-bucket', Key='users.json', Body=b'{}')
    users_file = s3_resource.Object('unobot-bucket', 'users.json')
    user_stuff = json.loads(users_file.get()['Body'].read().decode('utf-8'))

    # Load command settings in guilds
    try:
        s3_resource.Object('unobot-bucket', 'commands.json').load()
    except ClientError:
        s3_client.put_object(Bucket='unobot-bucket', Key='commands.json', Body=b'{}')
    commands_file = s3_resource.Object('unobot-bucket', 'commands.json')
    commands = json.loads(commands_file.get()['Body'].read().decode('utf-8'))

    # Initializes or updates the configuration files
    if client.guilds:
        if not dgs:
            for guild in client.guilds:
                dgs[str(guild.id)] = default_dgs

        else:
            for guild in client.guilds:
                if str(guild.id) not in dgs:
                    dgs[str(guild.id)] = default_dgs

            for guild_id in list(dgs.keys()):
                if guild_id not in map(lambda x: str(x.id), client.guilds):
                    del dgs[guild_id]

        dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

        if not user_stuff:
            for member in [x for x in client.get_all_members() if x.id != client.user.id and not x.bot]:
                default_user_stuff = {}
                for guild in [x for x in client.guilds if x.get_member(member.id)]:
                    default_user_stuff[str(guild.id)] = {
                        'Wins': 0,
                        'Score': 0,
                        'Played': 0
                    }
                user_stuff[str(member.id)] = default_user_stuff

        else:
            for member in [x for x in client.get_all_members() if not x.bot]:
                if str(member.id) not in user_stuff:
                    user_stuff[str(member.id)] = {}

                for guild in [x for x in client.guilds if x.get_member(member.id)]:
                    if str(guild.id) not in user_stuff[str(member.id)]:
                        user_stuff[str(member.id)][str(guild.id)] = {
                            'Wins': 0,
                            'Score': 0,
                            'Played': 0
                        }

            for user_id in list(user_stuff.keys()):
                if user_id not in map(lambda x: str(x.id), client.users):
                    del user_stuff[user_id]
                    continue

                for guild_id in list(user_stuff[user_id].keys()):
                    if guild_id not in map(lambda x: str(x.id), client.guilds):
                        del user_stuff[user_id][guild_id]

                        if not user_stuff[user_id]:
                            del user_stuff[user_id]

        users_file.put(Body=json.dumps(user_stuff).encode('utf-8'))

        if not commands:
            for guild in client.guilds:
                commands[str(guild.id)] = default_command_settings

        else:
            for guild in client.guilds:
                if str(guild.id) not in commands:
                    commands[str(guild.id)] = default_command_settings

            for guild_id in list(commands.keys()):
                if guild_id not in map(lambda x: str(x.id), client.guilds):
                    del commands[guild_id]

        commands_file.put(Body=json.dumps(commands).encode('utf-8'))

        for guild in client.guilds:
            cooldowns[str(guild.id)] = []

    else:
        dgs_file.put(Body=b'{}')
        users_file.put(Body=b'{}')
        commands_file.put(Body=b'{}')

    # Create the UNO Spectator role if it does not exist in a guild
    for guild in client.guilds:
        if not discord.utils.get(guild.roles, name='UNO Spectator'):
            await guild.create_role(name='UNO Spectator', color=discord.Color.red())

    # Change the bot's presence
    await client.change_presence(activity=discord.Game(name=f'UNO | Use {prefix}help'))


def rank(user: User = None, guild: Guild = None) -> Union[tuple, list]:
    """Calculates and returns the ranking of a player or a leaderboard.

    Args:
        user: The player whose ranking is to be returned
        guild: The Discord guild user is in

    Returns:
        Union[tuple, list]: Either a user's local/global ranking with total number of local/global players (if user is specified) or a local/global leaderboard
    """

    scores = []  # Stores the scores of players
    # Load users' data
    users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

    # Calculate and append the scores into the scores list
    if guild:
        for id in [x for x in list(users.keys()) if guild.get_member(int(x))]:
            scores.append(users[id][str(guild.id)]['Score'])

    else:
        for id in users:
            s = 0
            for g in [x for x in client.guilds if x.get_member(int(id))]:
                s += users[id][str(g.id)]['Score']
            scores.append(s)

    # Create a leaderboard
    leaderboard = len(scores) - rankdata(scores, method='max') + 1
    # Return the player's ranking with total number of players or the leaderboard
    if user:
        if guild:
            return round(
                leaderboard[[x for x in list(users.keys()) if guild.get_member(int(x))].index(str(user.id))]), len(
                leaderboard)
        else:
            return round(leaderboard[list(users.keys()).index(str(user.id))]), len(leaderboard)
    else:
        return [round(x) for x in leaderboard]


def has_played(user: User):
    """Checks if a user has ever played an UNO game using UNOBot.

    Args:
        user: A Discord user
    """

    for guild in [x for x in client.guilds if x.get_member(user.id)]:
        if json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))[
            str(user.id)][str(guild.id)]['Played'] > 0:
            return True

    return False


def no_guild(user: User):
    """Checks if a user does not belong to any guild.

    Args:
        user: A Discord user
    """

    return any(guild.get_member(user.id) for guild in client.guilds)


def list_duplicates_of(seq: list, item: int) -> list:
    """Lists the indexes of duplicates in an integer sequence.

    Args:
        seq: An integer sequence
        item: The target item in seq

    Returns:
        list: a list of the indexes of the duplicates of item
    """

    start_at = -1
    locs = []

    while True:
        try:
            loc = seq.index(item, start_at + 1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc

    return locs


async def cmd_info(ctx: ApplicationContext, cmd: str):
    """Sends a Discord embed of the information of a command.

    Args:
        ctx: The context in which the command that called this function is being invoked under
        cmd: The command whose information is to be sent
    """

    message = discord.Embed(title=prefix + 'settings commands ' + cmd, color=discord.Color.red())
    message.add_field(name=':level_slider: Toggle ' + cmd.capitalize(),
                      value='Turns a specific command on or off.\n\n`' + prefix + 'settings commands ' + cmd + ' <on|off>`\n' + chr(
                          173), inline=False)
    message.add_field(name=':stopwatch: Set Cooldown',
                      value='Sets a cooldown for the ' + cmd + ' command.\n\n`' + prefix + 'settings commands ' + cmd + ' cooldown <set|view> (time in seconds)`\n' + chr(
                          173), inline=False)
    message.add_field(name=':clipboard: Whitelist or Blacklist',
                      value='Whitelist or blacklist certain roles of users from using the ' + cmd + ' command. Also toggles between whitelist of blacklist modes.\n\n'
                                                                                                    '`' + prefix + 'settings commands ' + cmd + ' <whitelist|blacklist> <add|remove|enable|disable|view> (user|role)`\n' + chr(
                          173), inline=False)
    message.add_field(name=':mag: View Command Info', value='Gives you info on the ' + cmd + ' command\'s settings.\n\n'
                                                                                             '`' + prefix + 'settings commands ' + cmd + ' view`')

    await ctx.respond(embed=message)


async def game_setup(ctx: ApplicationContext, d: dict):
    """Sets up an UNO game.

    Args:
        ctx: The context under which the command that called this function is invoked
        d: The data storage of the game
    """

    guild = ctx.guild
    flip = d['settings']['Flip']

    # Create a channel category for UNO
    category = discord.utils.get(guild.categories, name='UNO-GAME')
    if not category:
        category = await guild.create_category('UNO-GAME')

    # Assign cards to the game
    if flip:
        d['cards'] = flip_cards
    else:
        d['cards'] = cards

    player_ids = list(d['players'].keys())

    # Assign a hand from the deck to bot(s) if they are playing
    for bot in [x for x in player_ids if not str.isdigit(x)]:
        while len(d['cards']) <= d['settings']['StartingCards']:
            if flip:
                d['cards'] += flip_cards
            else:
                d['cards'] += cards

        hand = sample(d['cards'], d['settings']['StartingCards'])
        d['players'][bot] = Bot(bot, guild, games, hand)
        d['cards'] = [card for card in d['cards'] if card not in hand]

    # Determine the order of play
    order = sample(player_ids, len(player_ids))
    ordered_dict = OrderedDict()
    for x in order:
        ordered_dict[x] = d['players'][x]

    # Assign the player list to the game
    d['players'] = dict(ordered_dict)

    async def set_channel(id: str):
        """Creates a channel for a player.

        Args:
            id (str): The ID of the player
        """

        player = guild.get_member(int(id))
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            player: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await category.create_text_channel(
            sub(r'[^\w -]', '', player.name.replace(' ', '-')) + '-UNO-Channel',
            overwrites=overwrites)

        welcome = await channel.send(content='**Welcome, ' + player.mention + '! This is your UNO channel!**\n'
                                                                              'Strategize, play your cards, unleash your wrath by drawing the feces out of people, and have fun with the game of UNO right here!\n\n'
                                                                              '• Use `p/play <card_color> <card_value>` to play a card.\n'
                                                                              '• Use `c/card(s)` to see your cards at anytime.\n'
                                                                              '• Use `d/draw` to draw a card.\n'
                                                                              '• Use `s/say <message>` to send a message to all players in their UNO channels.\n'
                                                                              '• Use `a/alert` to alert the player who is playing a card.')
        await welcome.pin()

        gcontents = '**Game settings:**\n'
        settings = [x for x in d['settings'] if
                    d['settings'][x] and x != 'StartingCards' or d['settings'][x] != 7 and x == 'StartingCards']
        if settings:
            for key in settings:
                gcontents += f'• {key}\n'
        else:
            gcontents += 'None'
        gsettings = await channel.send(content=gcontents)
        await gsettings.pin()

    # Create player channels for UNO
    await asyncio.gather(*[asyncio.create_task(set_channel(x)) for x in player_ids if str.isdigit(x)])

    # Create a spectator channel if the game allows spectating
    if d['settings']['SpectateGame']:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.roles, name='UNO Spectator'): discord.PermissionOverwrite(read_messages=True)
        }
        await category.create_text_channel('Spectator-UNO-Channel', overwrites=overwrites)

    # Let UNOBot know which channels to send messages to if UNOBot is playing
    for bot in [x for x in player_ids if not str.isdigit(x)]:
        d['players'][bot].channels = [x for x in guild.text_channels if x.category.name == 'UNO-GAME']

    for id in [x for x in player_ids if str.isdigit(x)]:
        # Assign more cards to the deck while the deck is not enough
        while len(d['cards']) <= d['settings']['StartingCards']:
            if flip:
                d['cards'] += flip_cards
            else:
                d['cards'] += cards

        # Assign a hand from the deck to a player
        hand = sample(d['cards'], d['settings']['StartingCards'])
        d['players'][id]['cards'] = hand
        d['cards'] = [card for card in d['cards'] if card not in hand]

        # Craft and send an embed message that displays the opening hand of a player
        m = discord.Embed(title='Your cards:', color=discord.Color.red())

        if not flip:
            image = Image.new('RGBA', (
                len(d['players'][id]['cards']) * (
                    round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                              (255, 0, 0, 0))

            for i in range(len(d['players'][id]['cards'])):
                card = Image.open('images/' + d['players'][id]['cards'][i] + '.png')
                refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                       round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))
        else:
            image = Image.new('RGBA', (
                len(d['players'][id]['cards']) * (
                    round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123 * 2)),
                              (255, 0, 0, 0))

            for i in range(len(d['players'][id]['cards'])):
                card = Image.open(
                    'images/' + d['players'][id]['cards'][i][
                        0] + '.png')
                refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                       round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))

                card = Image.open(
                    'images/' + d['players'][id]['cards'][
                        i][1] + '.png')
                refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                       round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], refined.size[1]))

        with BytesIO() as image_binary:
            image.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='image.png')

        m.set_image(url='attachment://image.png')

        await discord.utils.get(guild.text_channels,
                                name=sub(r'[^\w -]', '',
                                         guild.get_member(int(id)).name.lower().replace(' ',
                                                                                        '-')) + '-uno-channel').send(
            file=file, embed=m)

    # Assign the top card of the game
    if flip:
        c = choice(
            [card for card in d['cards'] if
             card[0] != 'wild' and card[0] != '+2' and 'flip' not in card[0] and card[1] != 'darkwild' and card[
                 1] != '+color'])
        d['current'] = c
        d['current_opposite'] = c

    else:
        d['current'] = choice(
            [card for card in d['cards'] if card != 'wild' and card != '+4'])

    # Craft and send a message that displays the top card of the game to every player (except UNOBot)
    if d['settings']['Flip']:
        color = search(r'red|blue|green|yellow', d['current'][0]).group(0)
    else:
        color = search(r'red|blue|green|yellow', d['current']).group(0)

    if color == 'red':
        m = discord.Embed(title='Top card:', color=discord.Color.red())
    elif color == 'blue':
        m = discord.Embed(title='Top card:', color=discord.Color.blue())
    elif color == 'green':
        m = discord.Embed(title='Top card:', color=discord.Color.green())
    else:
        m = discord.Embed(title='Top card:', color=discord.Color.from_rgb(255, 255, 0))

    if flip:
        image = Image.open('images/' + d['current'][0] + '.png')
    else:
        image = Image.open('images/' + d['current'] + '.png')
    refined = image.resize((round(image.size[0] / 6.0123456790123456790123456790123),
                            round(image.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)

    for channel in category.text_channels:
        with BytesIO() as image_binary:
            refined.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='topcard.png')

        m.set_image(url='attachment://topcard.png')
        await channel.send(file=file, embed=m)

    # Specify the first player
    if str.isdigit(order[0]):
        d['player'] = int(order[0])
    else:
        d['player'] = order[0]
    cplayer = order[0]

    # Light side first if Flip
    if flip:
        d['dark'] = False

    # Clear the guild's stack data if not done
    try:
        del stack[str(guild.id)]
    except KeyError:
        pass

    # Increment every player's Played count by 1
    users_file = s3_resource.Object('unobot-bucket', 'users.json')
    users = json.loads(users_file.get()['Body'].read().decode('utf-8'))
    for i in [x for x in player_ids if str.isdigit(x)]:
        users[i][str(guild.id)]['Played'] += 1
    users_file.put(Body=json.dumps(users).encode('utf-8'))

    # Print a message to the console stating a game has successfully started in the guild
    print(
        '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game has started in ' + str(guild) + '.')

    # Handle the case where the top card is a draw card
    # Get the hand of the first player
    if str.isdigit(cplayer):
        hand = d['players'][cplayer]['cards']
    else:
        hand = d['players'][cplayer].cards

    # Check if the first player has any draw cards that can be used to stack
    # If they have, allow them to stack
    # If they do not, draw them
    if not d['settings']['Flip']:
        if '+2' in d['current']:
            if d['settings']['StackCards'] and any('+2' in card for card in hand) or any('+4' in card for card in hand):
                stack[str(guild.id)] = 2

                if str.isdigit(cplayer):
                    await asyncio.gather(
                        *[asyncio.create_task(x.send(embed=discord.Embed(description='**' + guild.get_member(
                            int(cplayer)).name + ' can choose to stack cards or draw 2 cards.**',
                                                                         color=discord.Color.red()))) for x in
                          category.text_channels])

                    await display_cards(guild.get_member(int(cplayer)), guild)
                else:
                    await asyncio.gather(
                        *[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + cplayer + ' can choose to stack cards or draw 2 cards.**',
                            color=discord.Color.red()))) for x in category.text_channels])

                    await display_cards(cplayer, guild)

            else:
                if str.isdigit(cplayer):
                    await draw(guild.get_member(int(cplayer)), guild, 2)
                else:
                    await draw(cplayer, guild, 2)

                if str.isdigit(order[1]):
                    await display_cards(guild.get_member(int(order[1])), guild)
                else:
                    await display_cards(order[1], guild)

        else:
            if str.isdigit(cplayer):
                await display_cards(guild.get_member(int(cplayer)), guild)
            else:
                await display_cards(cplayer, guild)

    else:
        if '+1' in d['current'][0]:
            if d['settings']['StackCards'] and any('+2' in card for card in hand):
                stack[str(guild.id)] = 1

                if str.isdigit(cplayer):
                    await asyncio.gather(
                        *[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + guild.get_member(int(cplayer)).name + ' can choose to stack cards or draw 1 card.**',
                            color=discord.Color.red()))) for x in
                            category.text_channels])

                    await display_cards(guild.get_member(int(cplayer)), guild)
                else:
                    await asyncio.gather(
                        *[asyncio.create_task(x.send(embed=discord.Embed(description='**' + cplayer + ' can choose to stack cards or draw 1 card.**',
                                                                         color=discord.Color.red()))) for x in
                          category.text_channels])

                    await display_cards(cplayer, guild)

            else:
                if not str.isdigit(cplayer):
                    await draw(cplayer, guild, 1)
                else:
                    await draw(guild.get_member(int(cplayer)), guild, 1)

                if not str.isdigit(order[1]):
                    await display_cards(order[1], guild)
                else:
                    await display_cards(guild.get_member(int(order[1])), guild)

        else:
            if not str.isdigit(cplayer):
                await display_cards(cplayer, guild)
            else:
                await display_cards(guild.get_member(int(cplayer)), guild)


async def game_shutdown(d: dict, guild: Guild, winner: Union[Member, str] = None):
    """Shuts down a game.

    Args:
        d: The data storage of the game being shut down
        winner: The winner of the game
        guild: The Discord guild where the game is happening
    """

    player_ids = list(d['players'].keys())

    # If there is a winner
    if winner:
        # Load users' data
        users_file = s3_resource.Object('unobot-bucket', 'users.json')
        users = json.loads(users_file.get()['Body'].read().decode('utf-8'))

        # Scores are only calculated when no bot is playing
        if not [x for x in player_ids if not str.isdigit(x)]:
            # Initialize the score the winner gets to 0
            score = 0
            # Calculate winner's score and losers' penalties (if they are not UNOBot)
            tasks = []

            def get_score(player_id: str) -> int:
                cards = games[str(guild.id)]['players'][player_id]['cards']

                score = 0
                for card in cards:
                    if not games[str(guild.id)]['settings']['Flip']:
                        value = search(r'skip|reverse|wild|\d|\+[42]', card).group(0)

                        if value in ('+2', 'skip', 'reverse'):
                            score += 20
                        elif value in ('+4', 'wild'):
                            score += 50
                        else:
                            score += int(value)

                    elif not games[str(guild.id)]['dark']:
                        value = search(r'skip|reverse|wild|flip|\d|\+[21]', card[0]).group(0)

                        if value == '+1':
                            score += 10
                        elif value in ('reverse', 'flip', 'skip'):
                            score += 20
                        elif value == 'wild':
                            score += 40
                        elif value == '+2':
                            score += 50
                        else:
                            score += int(value)

                    else:
                        value = search(r'skip|reverse|wild|flip|\d|\+[5c]', card[1]).group(0)

                        if value in ('+5', 'reverse', 'flip'):
                            score += 20
                        elif value == 'skip':
                            score += 30
                        elif value == 'wild':
                            score += 40
                        elif value == '+c':
                            score += 60
                        else:
                            score += int(value)

                return score

            # Calculate the winner's score
            for key in [x for x in player_ids if x != str(winner.id)]:
                temp = get_score(key)

                if users[key][str(guild.id)]['Score'] < temp:
                    users[key][str(guild.id)]['Score'] = 0
                else:
                    users[key][str(guild.id)]['Score'] -= temp

                score += temp

            # Craft a message that displays who won , the winner's score, and how many pts every loser lost
            for key in [x for x in player_ids if x != str(winner.id) and 'left' not in d['players'][x]]:
                temp = get_score(key)

                if score == 1:
                    if temp == 1:
                        message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +1 pt',
                                                description=f"You lost **1** pt.",
                                                color=discord.Color.red())
                    else:
                        message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +1 pt',
                                                description=f"You lost **{temp}** pts.",
                                                color=discord.Color.red())
                else:
                    if temp == 1:
                        message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +{score} pts',
                                                description=f"You lost **1** pt.",
                                                color=discord.Color.red())
                    else:
                        message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +{score} pts',
                                                description=f"You lost **{temp}** pts.",
                                                color=discord.Color.red())
                message.set_image(url=winner.display_avatar.url)

                tasks.append(asyncio.create_task(discord.utils.get(guild.text_channels, name=sub(r'[^\w -]', '',
                                                                                                 guild.get_member(
                                                                                                     int(key)).name.lower().replace(
                                                                                                     ' ',
                                                                                                     '-')) + '-uno-channel').send(
                    embed=message)))

            if score == 1:
                message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +1 pt', color=discord.Color.red())
            else:
                message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +{score} pts', color=discord.Color.red())
            message.set_image(url=winner.display_avatar.url)

            tasks.append(asyncio.create_task(discord.utils.get(guild.text_channels, name=sub(r'[^\w -]', '',
                                                                                             winner.name.lower().replace(
                                                                                                 ' ',
                                                                                                 '-')) + '-uno-channel').send(
                embed=message)))
            tasks.append(asyncio.create_task(
                discord.utils.get(guild.text_channels, name='spectator-uno-channel').send(embed=message)))

            await asyncio.gather(*tasks)

            users[str(winner.id)][str(guild.id)]['Score'] += score

        else:
            # Craft a message that displays who won
            if isinstance(winner, Member):
                message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳', color=discord.Color.red())
                message.set_image(url=winner.display_avatar.url)
            else:
                message = discord.Embed(title=f'{winner} Won! 🎉 🥳', color=discord.Color.red())

            await asyncio.gather(
                *[asyncio.create_task(x.send(embed=message)) for x in guild.text_channels if
                  x.category.name == 'UNO-GAME'])

        # Increment winner's Win count and every player's Played count
        if isinstance(winner, Member):
            users[str(winner.id)][str(guild.id)]['Wins'] += 1

        users_file.put(Body=json.dumps(users).encode('utf-8'))

        # Wait 10 seconds before deleting UNO channels
        await asyncio.sleep(10)

    # Delete the UNO channels and category
    for channel in [x for x in guild.text_channels if x.category.name == 'UNO-GAME']:
        await channel.delete()

    # Clear the game's data
    del games[str(guild.id)]
    ending.remove(str(guild.id))
    try:
        del stack[str(guild.id)]
    except KeyError:
        pass

    # Print a message to the console stating the game has been successfully shut down
    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game has ended in ' + str(guild))


async def draw(player: Union[Member, str], guild: Guild, number: int, DUM: bool = False, color: bool = False):
    """Draws a player in a game.

    Args:
        player: The player to be drawn
        guild: The guild of the current game
        number: The number of cards the player is to draw
        DUM: Whether the player needs to draw until match
        color: Whether the player is subject to Wild Draw Color's effect
    """

    bot = None
    if isinstance(player, str):
        bot = games[str(guild.id)]['players'][player]

    # Wild Draw Color case
    if color:
        draw = []  # A list to keep track of the drawn cards

        # Get the color of the Wild Draw Color
        current_color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)
        # Randomly pick a card from the deck
        c = choice(games[str(guild.id)]['cards'])
        games[str(guild.id)]['cards'].remove(c)

        # Add the card from the deck to the player's hand
        if not bot:
            games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
        else:
            bot.cards.append(c)

        # Replenish the deck if no card is left
        if not games[str(guild.id)]['cards']:
            if not games[str(guild.id)]['settings']['Flip']:
                games[str(guild.id)]['cards'] += cards
            else:
                games[str(guild.id)]['cards'] += flip_cards

        # Append the card to the draw list
        draw.append(c)

        # Keep drawing the player while he does not get a card of the specified color
        color = search(r'pink|teal|orange|purple', c[1])
        while not color or color.group(0) != current_color:
            c = choice(games[str(guild.id)]['cards'])
            games[str(guild.id)]['cards'].remove(c)

            # Add the card from the deck to the player's hand
            if not bot:
                games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
            else:
                bot.cards.append(c)

            # Replenish the deck if no card is left
            if not games[str(guild.id)]['cards']:
                if not games[str(guild.id)]['settings']['Flip']:
                    games[str(guild.id)]['cards'] += cards
                else:
                    games[str(guild.id)]['cards'] += flip_cards

            # Append the card to the draw list
            draw.append(c)

            color = search(r'pink|teal|orange|purple', c[1])

    # Normal case
    elif not DUM:
        draw = []  # A list to keep track of the drawn cards

        # Draw the player {number} cards
        for i in range(number):
            # Randomly pick a card from the deck
            c = choice(games[str(guild.id)]['cards'])
            games[str(guild.id)]['cards'].remove(c)

            # Add the card from the deck to the player's hand
            if not bot:
                games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
            else:
                bot.cards.append(c)

            # Replenish the deck if no card is left
            if not games[str(guild.id)]['cards']:
                if not games[str(guild.id)]['settings']['Flip']:
                    games[str(guild.id)]['cards'] += cards
                else:
                    games[str(guild.id)]['cards'] += flip_cards

            # Append the card to the draw list
            draw.append(c)

    # Draw Until Match case
    else:
        draw = []  # A list to keep track of the drawn cards
        # Randomly pick a card from the deck
        c = choice(games[str(guild.id)]['cards'])
        games[str(guild.id)]['cards'].remove(c)

        # Add the card from the deck to the player's hand
        if not bot:
            games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
        else:
            bot.cards.append(c)

        # Replenish the deck if no card is left
        if not games[str(guild.id)]['cards']:
            if not games[str(guild.id)]['settings']['Flip']:
                games[str(guild.id)]['cards'] += cards
            else:
                games[str(guild.id)]['cards'] += flip_cards

        # Append the card to the draw list
        draw.append(c)

        # Keep drawing the player while he does not get a playable card
        if not games[str(guild.id)]['settings']['Flip']:
            current_color = search(r'red|blue|green|yellow', games[str(guild.id)]['current']).group(0)
            current_value = search(r'\+[42]|wild|skip|reverse|\d', games[str(guild.id)]['current']).group(0)

            colour = search(r'red|blue|green|yellow', c)
            if colour:
                colour = colour.group(0)
            value = search(r'\+[42]|wild|skip|reverse|\d', c).group(0)

            while colour != current_color and value not in {current_value, '+4', 'wild'}:
                c = choice(games[str(guild.id)]['cards'])
                games[str(guild.id)]['cards'].remove(c)

                if not bot:
                    games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                else:
                    bot.cards.append(c)

                if not games[str(guild.id)]['cards']:
                    games[str(guild.id)]['cards'] += cards

                draw.append(c)

                colour = search(r'red|blue|green|yellow', c)
                if colour:
                    colour = colour.group(0)
                value = search(r'\+[42]|wild|skip|reverse|\d', c).group(0)

        else:
            if not games[str(guild.id)]['dark']:
                current_color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][0]).group(0)
                current_value = search(r'\+[12]|wild|skip|reverse|flip|\d', games[str(guild.id)]['current'][0]).group(0)

                colour = search(r'red|blue|green|yellow', c[0])
                if colour:
                    colour = colour.group(0)
                value = search(r'\+[12]|wild|skip|reverse|flip|\d', c[0]).group(0)

                while colour != current_color and value not in {current_value, '+2', 'wild'}:
                    c = choice(games[str(guild.id)]['cards'])
                    games[str(guild.id)]['cards'].remove(c)

                    if not bot:
                        games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                    else:
                        bot.cards.append(c)

                    if not games[str(guild.id)]['cards']:
                        games[str(guild.id)]['cards'] += flip_cards

                    draw.append(c)

                    colour = search(r'red|blue|green|yellow', c[0])
                    if colour:
                        colour = colour.group(0)
                    value = search(r'\+[12]|wild|skip|reverse|flip|\d', c[0]).group(0)

            else:
                current_color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)
                current_value = search(r'\+(5|color)|wild|skip|reverse|flip|\d', games[str(guild.id)]['current'][1]).group(0)

                colour = search(r'pink|teal|orange|purple', c[1])
                if colour:
                    colour = colour.group(0)
                value = search(r'\+(5|color)|wild|skip|reverse|flip|\d', c[1]).group(0)

                while colour != current_color and value not in {current_value, '+color', 'wild'}:
                    c = choice(games[str(guild.id)]['cards'])
                    games[str(guild.id)]['cards'].remove(c)

                    if not bot:
                        games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                    else:
                        bot.cards.append(c)

                    if not games[str(guild.id)]['cards']:
                        games[str(guild.id)]['cards'] += flip_cards

                    draw.append(c)

                    colour = search(r'pink|teal|orange|purple', c[1])
                    if colour:
                        colour = colour.group(0)
                    value = search(r'\+(5|color)|wild|skip|reverse|flip|\d', c[1]).group(0)

    # Craft a message that displays the details of the drawn card(s) to every player (except UNOBot)
    message = None
    if not bot:
        description = 'You drew '

        if not games[str(guild.id)]['settings']['Flip']:
            if len(draw) == 1:
                description += ('a **' + draw[0].capitalize() + '**.')

            else:
                for i in range(len(draw)):
                    if i == len(draw) - 1:
                        description += ('and a **' + draw[i].capitalize() + '**.')
                    else:
                        description += ('a **' + draw[i].capitalize() + '**, ')

        else:
            if not games[str(guild.id)]['dark']:
                if len(draw) == 1:
                    description += ('a **' + draw[0][0].capitalize() + '**.')

                else:
                    for i in range(len(draw)):
                        if i == len(draw) - 1:
                            description += ('and a **' + draw[i][0].capitalize() + '**.')
                        else:
                            description += ('a **' + draw[i][0].capitalize() + '**, ')

            else:
                if len(draw) == 1:
                    description += ('a **' + draw[0][1].capitalize() + '**.')

                else:
                    for i in range(len(draw)):
                        if i == len(draw) - 1:
                            description += ('and a **' + draw[i][1].capitalize() + '**.')
                        else:
                            description += ('a **' + draw[i][1].capitalize() + '**, ')

        message = discord.Embed(description=description, color=discord.Color.red())

        image = Image.new('RGBA', (
            len(draw) * (round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
            round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                          (255, 0, 0, 0))

        if not games[str(guild.id)]['settings']['Flip']:
            for i in range(len(draw)):
                card = Image.open('images/' + draw[i] + '.png')
                refined = card.resize(
                    (round(card.size[0] / 6.0123456790123456790123456790123),
                     round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))
        else:
            if not games[str(guild.id)]['dark']:
                for i in range(len(draw)):
                    card = Image.open('images/' + draw[i][0] + '.png')
                    refined = card.resize(
                        (round(card.size[0] / 6.0123456790123456790123456790123),
                         round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                    image.paste(refined, (i * refined.size[0], 0))
            else:
                for i in range(len(draw)):
                    card = Image.open('images/' + draw[i][1] + '.png')
                    refined = card.resize(
                        (round(card.size[0] / 6.0123456790123456790123456790123),
                         round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                    image.paste(refined, (i * refined.size[0], 0))

        with BytesIO() as image_binary:
            image.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='image.png')

        message.set_image(url='attachment://image.png')

    if len(draw) == 1:
        if message:
            await asyncio.gather(
                discord.utils.get(guild.channels,
                                  name=sub(r'[^\w -]', '',
                                           player.name.lower().replace(' ', '-')) + '-uno-channel',
                                  type=discord.ChannelType.text).send(file=file, embed=message),
                *[asyncio.create_task(x.send(
                    embed=discord.Embed(description='**' + player.name + '** drew a card.',
                                        color=discord.Color.red()))) for x in guild.text_channels if
                    x.category.name == 'UNO-GAME' and x.name != sub(r'[^\w -]', '',
                                                                    player.name.lower().replace(' ',
                                                                                                '-')) + '-uno-channel']
            )
        else:
            await asyncio.gather(
                *[asyncio.create_task(x.send(
                    embed=discord.Embed(description=f'**{bot.name}** drew a card.',
                                        color=discord.Color.red()))) for x in guild.text_channels if
                    x.category.name == 'UNO-GAME'])
    else:
        if message:
            await asyncio.gather(
                discord.utils.get(guild.channels,
                                  name=sub(r'[^\w -]', '',
                                           player.name.lower().replace(' ', '-')) + '-uno-channel',
                                  type=discord.ChannelType.text).send(file=file, embed=message),
                *[asyncio.create_task(x.send(
                    embed=discord.Embed(description='**' + player.name + '** drew **' + str(len(draw)) + '** cards.',
                                        color=discord.Color.red()))) for x in guild.text_channels if
                    x.category.name == 'UNO-GAME' and x.name != sub(r'[^\w -]', '',
                                                                    player.name.lower().replace(' ',
                                                                                                '-')) + '-uno-channel']
            )
        else:
            await asyncio.gather(
                *[asyncio.create_task(x.send(
                    embed=discord.Embed(description=f'**{bot.name}** drew **' + str(len(draw)) + '** cards.',
                                        color=discord.Color.red()))) for x in guild.text_channels if
                    x.category.name == 'UNO-GAME'])


async def display_cards(player: Union[Member, str], guild: Guild):
    """Displays the current player's hand to every player except UNOBot.

    Args:
        player: The current player
        guild: The guild of the current game
    """

    if str(guild.id) not in ending:
        async def send_cards(channel: TextChannel):
            """Sends a player's hand to every UNO channel.

            Args:
                channel: The channel of the current player
            """

            if isinstance(player, Member) and channel.name == sub(r'[^\w -]', '',
                                                                  player.name.lower().replace(' ',
                                                                                              '-')) + '-uno-channel':
                if not games[str(guild.id)]['settings']['Flip']:
                    color = search(r'red|blue|green|yellow', games[str(guild.id)]['current']).group(0)

                    if color == 'red':
                        message = discord.Embed(title='It\'s your turn!',
                                                description='The current card is **' + games[str(guild.id)][
                                                    'current'].capitalize() + '**.\n\nYour cards:',
                                                color=discord.Color.red())
                    elif color == 'blue':
                        message = discord.Embed(title='It\'s your turn!',
                                                description='The current card is **' + games[str(guild.id)][
                                                    'current'].capitalize() + '**.\n\nYour cards:',
                                                color=discord.Color.blue())
                    elif color == 'green':
                        message = discord.Embed(title='It\'s your turn!',
                                                description='The current card is **' + games[str(guild.id)][
                                                    'current'].capitalize() + '**.\n\nYour cards:',
                                                color=discord.Color.green())
                    else:
                        message = discord.Embed(title='It\'s your turn!',
                                                description='The current card is **' + games[str(guild.id)][
                                                    'current'].capitalize() + '**.\n\nYour cards:',
                                                color=discord.Color.from_rgb(255, 255, 0))

                    image = Image.new('RGBA', (
                        len(games[str(guild.id)]['players'][str(player.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)]['players'][str(player.id)]['cards'])):
                        card = Image.open(
                            'images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i] + '.png')
                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)
                        image.paste(refined, (i * refined.size[0], 0))

                    with BytesIO() as image_binary:
                        image.save(image_binary, format='PNG', quality=100)
                        image_binary.seek(0)
                        file = discord.File(fp=image_binary, filename='image.png')

                    message.set_image(url='attachment://image.png')

                else:
                    if not games[str(guild.id)]['dark']:
                        color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][0]).group(0)

                        if color == 'red':
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][0].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.red())
                        elif color == 'blue':
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][0].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.blue())
                        elif color == 'green':
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][0].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.green())
                        else:
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][0].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.from_rgb(255, 255, 0))

                    else:
                        color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)

                        if color == 'pink':
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][1].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.from_rgb(255, 20, 147))

                        elif color == 'teal':
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][1].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.from_rgb(0, 128, 128))

                        elif color == 'orange':
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][1].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.from_rgb(255, 140, 0))

                        else:
                            message = discord.Embed(title='It\'s your turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'][1].capitalize() + '**.\n\nYour cards:',
                                                    color=discord.Color.from_rgb(102, 51, 153))

                    image = Image.new('RGBA', (
                        len(games[str(guild.id)]['players'][str(player.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)]['players'][str(player.id)]['cards'])):
                        if not games[str(guild.id)]['dark']:
                            card = Image.open(
                                'images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][0] + '.png')
                        else:
                            card = Image.open(
                                'images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][1] + '.png')

                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)

                        image.paste(refined, (i * refined.size[0], 0))

                    with BytesIO() as image_binary:
                        image.save(image_binary, format='PNG', quality=100)
                        image_binary.seek(0)
                        file = discord.File(fp=image_binary, filename='image.png')

                    message.set_image(url='attachment://image.png')

            else:
                if isinstance(player, Member):
                    if not games[str(guild.id)]['settings']['Flip']:
                        color = search(r'red|blue|green|yellow', games[str(guild.id)]['current']).group(0)

                        if color == 'red':
                            message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.red())
                        elif color == 'blue':
                            message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.blue())
                        elif color == 'green':
                            message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.green())
                        else:
                            message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.from_rgb(255, 255, 0))

                    else:
                        if not games[str(guild.id)]['dark']:
                            color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][0]).group(0)

                            if color == 'red':
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.red())
                            elif color == 'blue':
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.blue())
                            elif color == 'green':
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.green())
                            else:
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(255, 255, 0))
                        else:
                            color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)

                            if color == 'pink':
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(255, 20, 147))

                            elif color == 'teal':
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(0, 128, 128))

                            elif color == 'orange':
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(255, 140, 0))

                            else:
                                message = discord.Embed(title='It\'s ' + player.name + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(102, 51, 153))

                else:
                    if not games[str(guild.id)]['settings']['Flip']:
                        color = search(r'red|blue|green|yellow', games[str(guild.id)]['current']).group(0)

                        if color == 'red':
                            message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.red())
                        elif color == 'blue':
                            message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.blue())
                        elif color == 'green':
                            message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.green())
                        else:
                            message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                    description='The current card is **' + games[str(guild.id)][
                                                        'current'].capitalize() + '**.\n\nTheir cards:',
                                                    color=discord.Color.from_rgb(255, 255, 0))

                    else:
                        if not games[str(guild.id)]['dark']:
                            color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][0]).group(0)

                            if color == 'red':
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.red())
                            elif color == 'blue':
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.blue())
                            elif color == 'green':
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.green())
                            else:
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][0].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(255, 255, 0))
                        else:
                            color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)

                            if color == 'pink':
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(255, 20, 147))

                            elif color == 'teal':
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(0, 128, 128))

                            elif color == 'orange':
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(255, 140, 0))

                            else:
                                message = discord.Embed(title='It\'s ' + player + '\'s turn!',
                                                        description='The current card is **' + games[str(guild.id)][
                                                            'current'][1].capitalize() + '**.\n\nTheir cards:',
                                                        color=discord.Color.from_rgb(102, 51, 153))

                if isinstance(player, Member):
                    image = Image.new('RGBA', (
                        len(games[str(guild.id)]['players'][str(player.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)]['players'][str(player.id)]['cards'])):
                        if games[str(guild.id)]['settings']['Flip']:
                            if not games[str(guild.id)]['dark']:
                                card = Image.open(
                                    'images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][1] + '.png')
                            else:
                                card = Image.open(
                                    'images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][0] + '.png')
                        else:
                            card = Image.open('images/back.png')

                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)

                        image.paste(refined, (i * refined.size[0], 0))

                else:
                    image = Image.new('RGBA', (
                        len(games[str(guild.id)]['players'][player].cards) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)]['players'][player].cards)):
                        if games[str(guild.id)]['settings']['Flip']:
                            if not games[str(guild.id)]['dark']:
                                card = Image.open(
                                    'images/' + games[str(guild.id)]['players'][player].cards[i][1] + '.png')
                            else:
                                card = Image.open(
                                    'images/' + games[str(guild.id)]['players'][player].cards[i][0] + '.png')
                        else:
                            card = Image.open('images/back.png')

                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)

                        image.paste(refined, (i * refined.size[0], 0))

                with BytesIO() as image_binary:
                    image.save(image_binary, format='PNG', quality=100)
                    image_binary.seek(0)
                    file = discord.File(fp=image_binary, filename='image.png')

                message.set_image(url='attachment://image.png')

            if not games[str(guild.id)]['settings']['Flip']:
                thumbnail = discord.File('images/' + games[str(guild.id)]['current'] + '.png', filename='thumbnail.png')
            else:
                if not games[str(guild.id)]['dark']:
                    thumbnail = discord.File('images/' + games[str(guild.id)]['current'][0] + '.png',
                                             filename='thumbnail.png')
                else:
                    thumbnail = discord.File('images/' + games[str(guild.id)]['current'][1] + '.png',
                                             filename='thumbnail.png')
            message.set_thumbnail(url='attachment://thumbnail.png')

            n = None
            p = [x for x in games[str(guild.id)]['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in games[str(guild.id)]['players'][x]]

            temp = iter(p)
            for key in temp:
                if key == player or isinstance(player, Member) and key == str(player.id):
                    n = next(temp, next(iter(p)))
                    if str.isdigit(n):
                        n = guild.get_member(int(n))
                    break

            if isinstance(n, Member):
                message.set_footer(text=n.name + ' is next!')
            else:
                message.set_footer(text=n + ' is next!')

            try:
                await channel.send(files=[thumbnail, file], embed=message)
            except ClientOSError:
                pass

        # Send the current player's hand to every UNO channel
        await asyncio.gather(
            *[asyncio.create_task(send_cards(x)) for x in guild.text_channels if x.category.name == 'UNO-GAME'])

        # Change the current player of the game
        if isinstance(player, Member):
            games[str(guild.id)]['player'] = player.id
        else:
            games[str(guild.id)]['player'] = player

            # Tell the bot to play if they are the current player
            await games[str(guild.id)]['players'][player].play()


def get_hands(guild: Guild, player: Member, n: Member) -> Select:
    """Returns the hands of every player except the current player in the form of a Discord select menu
    for when a 7 card is played under 7-0 game rule.

    Args:
        guild: The guild where the game is happening
        player: The player that wants to see hands of every other player
        n: The next player

    Returns:
        Select: a Discord select menu containing the details of all other players' hands
    """
    options = []  # A list of options for the select menu

    # Create the select menu options
    for key in [x for x in games[str(guild.id)]['players'] if x != str(player.id)]:
        if key != str(client.user.id):
            options.append(SelectOption(
                label=str(guild.get_member(int(key))),
                description=f'{len(games[str(guild.id)]["players"][key]["cards"])} cards'
            ))
        else:
            options.append(SelectOption(
                label=str(guild.get_member(int(key))),
                description=f'{len(games[str(guild.id)]["players"][key].cards)} cards'
            ))

    # Create and return the select menu if player is not UNOBot
    if player.id != client.user.id:
        select = Select(placeholder='Choose a player...',
                        min_values=1,
                        max_values=1,
                        options=options)

        async def select_callback(interaction):
            await interaction.response.defer()

            switch = guild.get_member_named(select.values[0])

            if switch.id != client.user.id:
                games[str(guild.id)]['players'][str(player.id)]['cards'], \
                games[str(guild.id)]['players'][str(switch.id)]['cards'] = \
                    games[str(guild.id)]['players'][str(switch.id)]['cards'], \
                    games[str(guild.id)]['players'][str(player.id)]['cards']
            else:
                games[str(guild.id)]['players'][str(player.id)]['cards'], \
                games[str(guild.id)]['players'][str(switch.id)].cards = \
                    games[str(guild.id)]['players'][str(switch.id)].cards, \
                    games[str(guild.id)]['players'][str(player.id)]['cards']

            await asyncio.gather(
                *[asyncio.create_task(x.send(embed=discord.Embed(
                    description='**' + player.name + '** switched hands with **' + switch.name + '**.',
                    color=discord.Color.red()))) for x in
                    interaction.channel.category.text_channels])

            await display_cards(n, guild)

        select.callback = select_callback

        return select


async def play_card(card: Union[str, tuple], player: Union[Member, str], guild: Guild):
    """Plays a card on behalf of a player.

    Args:
        card: The card played by the player
        player: The player who played the card
        guild: The guild of the current game
    """

    # Check if player is a bot
    bot = None
    if isinstance(player, str):
        bot = games[str(guild.id)]['players'][player]

    # Removes the played card from player's hand and puts it back to the deck
    if not games[str(guild.id)]['settings']['Flip']:
        if not bot:
            if '+4' in card:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove('+4')

                if str(client.user.id) in games[str(guild.id)]['players']:
                    games[str(guild.id)]['players'][str(client.user.id)].losing_colors.add(card.replace('+4', ''))
            elif 'wild' in card:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove('wild')

                if str(client.user.id) in games[str(guild.id)]['players']:
                    games[str(guild.id)]['players'][str(client.user.id)].losing_colors.add(card.replace('wild', ''))
            else:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove(card)

            if '+4' in games[str(guild.id)]['current']:
                games[str(guild.id)]['cards'].append('+4')
            elif 'wild' in games[str(guild.id)]['current']:
                games[str(guild.id)]['cards'].append('wild')
            else:
                games[str(guild.id)]['cards'].append(games[str(guild.id)]['current'])

        else:
            if '+4' in card:
                bot.cards.remove('+4')
            elif 'wild' in card:
                bot.cards.remove('wild')
            else:
                bot.cards.remove(card)

            if '+4' in games[str(guild.id)]['current']:
                games[str(guild.id)]['cards'].append('+4')
            elif 'wild' in games[str(guild.id)]['current']:
                games[str(guild.id)]['cards'].append('wild')
            else:
                games[str(guild.id)]['cards'].append(games[str(guild.id)]['current'])

    else:
        c = None
        if not games[str(guild.id)]['dark']:
            if '+2' in card[0]:
                c = ('+2', card[1])
            elif 'wild' in card[0]:
                c = ('wild', card[1])
        else:
            if '+color' in card[1]:
                c = (card[0], '+color')
            elif 'wild' in card[1]:
                c = (card[0], 'darkwild')

        if not bot:
            if c:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove(c)

                if 'flip' in c:
                    for b in [x for x in games[str(guild.id)]['players'] if not str.isdigit(x)]:
                        b.losing_colors, b.losing_values = set(), set()

                        if games[str(guild.id)]['dark']:
                            b.losing_colors.add(search(r'pink|teal|orange|purple', c[1]).group(0))
                            b.losing_values.add(search(r'skip|reverse|\d', c[1]).group(0))
                            for p in [x for x in games[str(guild.id)]['players'] if str.isdigit(x) and x != b]:
                                for temp in games[str(guild.id)]['players'][p]['cards']:
                                    b.losing_colors.add(search(r'pink|teal|orange|purple', temp[1]).group(0))
                                    v = search(r'\+c|skip|reverse|\d', temp[1]).group(0)
                                    if v == '+c':
                                        b.losing_values.add('skip')
                                        b.losing_values.add('reverse')
                                    else:
                                        b.losing_values.add(v)
                            for p in [x for x in games[str(guild.id)]['players'] if not str.isdigit(x) and x != b]:
                                for temp in games[str(guild.id)]['players'][p].cards:
                                    b.losing_colors.add(search(r'pink|teal|orange|purple', temp[1]).group(0))
                                    v = search(r'\+c|skip|reverse|\d', temp[1]).group(0)
                                    if v == '+c':
                                        b.losing_values.add('skip')
                                        b.losing_values.add('reverse')
                                    else:
                                        b.losing_values.add(v)
                        else:
                            b.losing_colors.add(search(r'red|blue|green|yellow', c[0]).group(0))
                            b.losing_values.add(search(r'skip|reverse|\d', c[0]).group(0))
                            for p in [x for x in games[str(guild.id)]['players'] if str.isdigit(x) and x != b]:
                                for temp in games[str(guild.id)]['players'][p]['cards']:
                                    b.losing_colors.add(search(r'red|blue|green|yellow', temp[0]).group(0))
                                    v = search(r'\+2|skip|reverse|\d', temp[0]).group(0)
                                    if v == '+2':
                                        b.losing_values.add('skip')
                                        b.losing_values.add('reverse')
                                    else:
                                        b.losing_values.add(v)
                            for p in [x for x in games[str(guild.id)]['players'] if not str.isdigit(x) and x != b]:
                                for temp in games[str(guild.id)]['players'][p].cards:
                                    b.losing_colors.add(search(r'red|blue|green|yellow', temp[0]).group(0))
                                    v = search(r'\+2|skip|reverse|\d', temp[0]).group(0)
                                    if v == '+2':
                                        b.losing_values.add('skip')
                                        b.losing_values.add('reverse')
                                    else:
                                        bot.losing_values.add(v)

                if len(games[str(guild.id)]['players'][str(player.id)]['cards']) == 1 and str(client.user.id) in \
                        games[str(guild.id)]['players']:
                    if not games[str(guild.id)]['dark']:
                        bot.losing_colors.add(card[0].replace(c[0], ''))
                    else:
                        bot.losing_colors.add(card[1].replace(c[1], ''))
            else:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove(card)
        else:
            if c:
                bot.cards.remove(c)
            else:
                bot.cards.remove(card)

        if not games[str(guild.id)]['dark']:
            if '+2' in games[str(guild.id)]['current'][0]:
                games[str(guild.id)]['current'] = ('+2', games[str(guild.id)]['current'][1])
            elif 'wild' in games[str(guild.id)]['current'][0]:
                games[str(guild.id)]['current'] = ('wild', games[str(guild.id)]['current'][1])
        else:
            if '+color' in games[str(guild.id)]['current'][1]:
                games[str(guild.id)]['current'] = (games[str(guild.id)]['current'][0], '+color')
            elif 'wild' in games[str(guild.id)]['current'][1]:
                games[str(guild.id)]['current'] = (games[str(guild.id)]['current'][0], 'darkwild')

        games[str(guild.id)]['cards'].append(games[str(guild.id)]['current'])

    # Make the played card the first card on the discard pile
    games[str(guild.id)]['current'] = card

    # Craft an embed message that displays the played card to all players except UNOBot
    if games[str(guild.id)]['settings']['Flip']:
        if not games[str(guild.id)]['dark']:
            color = search(r'red|blue|green|yellow', card[0]).group(0)

            if isinstance(player, Member):
                if color == 'red':
                    message = discord.Embed(title=player.name + ':', color=discord.Color.red())
                elif color == 'blue':
                    message = discord.Embed(title=player.name + ':', color=discord.Color.blue())
                elif color == 'green':
                    message = discord.Embed(title=player.name + ':', color=discord.Color.green())
                else:
                    message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 255, 0))
            else:
                if color == 'red':
                    message = discord.Embed(title=player + ':', color=discord.Color.red())
                elif color == 'blue':
                    message = discord.Embed(title=player + ':', color=discord.Color.blue())
                elif color == 'green':
                    message = discord.Embed(title=player + ':', color=discord.Color.green())
                else:
                    message = discord.Embed(title=player + ':', color=discord.Color.from_rgb(255, 255, 0))
        else:
            color = search(r'pink|teal|orange|purple', card[1]).group(0)

            if isinstance(player, Member):
                if color == 'pink':
                    message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 20, 147))
                elif color == 'teal':
                    message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(0, 128, 128))
                elif color == 'orange':
                    message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 140, 0))
                else:
                    message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(102, 51, 153))
            else:
                if color == 'pink':
                    message = discord.Embed(title=player + ':', color=discord.Color.from_rgb(255, 20, 147))
                elif color == 'teal':
                    message = discord.Embed(title=player + ':', color=discord.Color.from_rgb(0, 128, 128))
                elif color == 'orange':
                    message = discord.Embed(title=player + ':', color=discord.Color.from_rgb(255, 140, 0))
                else:
                    message = discord.Embed(title=player + ':', color=discord.Color.from_rgb(102, 51, 153))

    else:
        color = search(r'red|blue|green|yellow', card).group(0)

        if isinstance(player, Member):
            if color == 'red':
                message = discord.Embed(title=player.name + ':', color=discord.Color.red())
            elif color == 'blue':
                message = discord.Embed(title=player.name + ':', color=discord.Color.blue())
            elif color == 'green':
                message = discord.Embed(title=player.name + ':', color=discord.Color.green())
            else:
                message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 255, 0))
        else:
            if color == 'red':
                message = discord.Embed(title=player + ':', color=discord.Color.red())
            elif color == 'blue':
                message = discord.Embed(title=player + ':', color=discord.Color.blue())
            elif color == 'green':
                message = discord.Embed(title=player + ':', color=discord.Color.green())
            else:
                message = discord.Embed(title=player + ':', color=discord.Color.from_rgb(255, 255, 0))

    if not games[str(guild.id)]['settings']['Flip']:
        image = Image.open('images/' + card + '.png')
    else:
        if not games[str(guild.id)]['dark']:
            image = Image.open('images/' + card[0] + '.png')
        else:
            image = Image.open('images/' + card[1] + '.png')
    refined = image.resize(
        (round(image.size[0] / 6.0123456790123456790123456790123),
         round(image.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)

    async def send_card(channel: TextChannel):
        """Sends the played card to a channel.

        Args:
            channel: The channel to receive the message
        """

        with BytesIO() as image_binary:
            refined.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='card.png')

        message.set_image(url='attachment://card.png')

        await channel.send(file=file, embed=message)

    # Send the played card to all UNO channels
    try:
        await asyncio.gather(
            *[asyncio.create_task(send_card(x)) for x in guild.text_channels if x.category.name == 'UNO-GAME'])
    except discord.NotFound:
        pass

    # Get the next player
    n = None
    p = [x for x in games[str(guild.id)]['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in games[str(guild.id)]['players'][x]]

    temp = iter(p)
    for key in temp:
        if key == player or isinstance(player, Member) and key == str(player.id):
            n = next(temp, next(iter(p)))
            if str.isdigit(n):
                n = guild.get_member(int(n))
            break

    # If the player has no card left
    if isinstance(player, Member) and not games[str(guild.id)]['players'][str(player.id)][
        'cards'] or bot and not bot.cards:
        # Make the game ending
        ending.append(str(guild.id))

        d = False
        if not games[str(guild.id)]['settings']['Flip'] and '+' in card or 'dark' in games[str(guild.id)] and (not games[str(guild.id)]['dark'] and '+' in card[0] or games[str(guild.id)]['dark'] and '+' in card[1]):
            d = not d

        # If the last card is a draw card, draw the next player
        if d:
            if not games[str(guild.id)]['settings']['Flip'] and '4' in card:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 4
                    await draw(n, guild, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, guild, 4)
            elif not games[str(guild.id)]['settings']['Flip'] and '2' in card or not games[str(guild.id)][
                'dark'] and '2' in card[0]:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 2
                    await draw(n, guild, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, guild, 2)
            elif not games[str(guild.id)]['dark'] and '1' in card[0]:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 1
                    await draw(n, guild, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, guild, 1)
            elif games[str(guild.id)]['dark'] and '5' in card[1]:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 5
                    await draw(n, guild, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, guild, 5)
            elif games[str(guild.id)]['dark'] and 'color' in card[1]:
                await draw(n, guild, 1, False, True)

        # If the last card is a flip card, flip everything
        elif 'flip' in card[0] and not games[str(guild.id)]['dark'] or 'flip' in card[1] and games[str(guild.id)][
            'dark']:
            games[str(guild.id)]['dark'] = not games[str(guild.id)]['dark']

        # Edit the game invitation message in order to show who the winner is
        for channel in guild.text_channels:
            try:
                m = await channel.fetch_message(games[str(guild.id)]['message'])
            except (discord.NotFound, discord.Forbidden):
                continue
            else:
                break
        m_dict = m.embeds[0].to_dict()
        for field in m_dict['fields']:
            if field['name'] == 'Players:':
                if bot:
                    field['value'] = field['value'].replace(f':small_blue_diamond:{bot.name}',
                                                            f':crown: **{bot.name}**')
                else:
                    field['value'] = field['value'].replace(f':small_blue_diamond:{player.name}',
                                                            f':crown: **{player.name}**')
                break

        await m.edit(embed=discord.Embed.from_dict(m_dict))

        # Shut down the game where the player wins
        await game_shutdown(games[str(guild.id)], guild, player)


class Bot:
    """The AI that plays UNO by the name of UNOBot.

    When a user mentions UNOBot in the StartGame (/u-sg) command, UNOBot will join the game and play using this AI.
    This AI is NOT trained. However, machine learning elements (e.g. neural network, weights & biases) are present in
    the code and it adopts what is considered the optimal strategy for UNO. Since UNO is based substantially on luck,
    trained AI is only 3% more likely to win against a random player. Training an AI for UNO is thereby worthless.
    A player can beat this AI quite easily. DO NOT expect perfection from this AI or any other UNO AI.

    Attributes:
        name: The name of the AI
        id: The ID of UNOBot
        guild: The guild where UNOBot is playing in
        channels: A list of text channels UNOBot sends messages in
        cards: The hand of UNOBot
        reccount: Number of recursion(s) done by the AI
        losing_colors: Colors to avoid
        losing_value: Values to avoid
    """

    def __init__(self, name: str, guild: Guild, games: dict, cards: list):
        """Initializes the AI."""

        self.name = name
        self.id = client.user.id
        self.guild = guild
        self.channels = self.playables = []
        self.games = games
        self.cards = cards
        self.reccount = 0
        self.losing_colors, self.losing_values = set(), set()

    def __get_color_and_value(self, card: Union[str, tuple]) -> (str, str):
        """Returns the color and value of an UNO card.

        Args:
            card: An UNO card

        Returns:
            (str, str): The color and value of the UNO card
        """

        try:
            d = self.games[str(self.guild.id)]
        except KeyError:
            return

        if not d['settings']['Flip']:
            color = search(r'red|blue|green|yellow', card)
            if color:
                color = color.group(0)
            value = search(r'\+[24]|wild|skip|reverse|\d', card).group(0)

        elif not d['dark']:
            color = search(r'red|blue|green|yellow', card[0])
            if color:
                color = color.group(0)
            value = search(r'\+[12]|wild|skip|reverse|flip|\d', card[0]).group(0)

        else:
            color = search(r'pink|teal|orange|purple', card[1])
            if color:
                color = color.group(0)
            value = search(r'\+(5|color)|wild|skip|reverse|flip|\d', card[1]).group(0)

        return color, value

    def __get_color(self, card: Union[str, tuple]) -> str:
        """Returns the color of an UNO card.

        Args:
            card: An UNO card

        Returns:
            str: The color of the UNO card
        """

        try:
            return self.__get_color_and_value(card)[0]
        except TypeError:
            pass

    def __get_value(self, card: Union[str, tuple]) -> str:
        """Returns the value of an UNO card.

        Args:
            card: An UNO card

        Returns:
            str: The value of the UNO card
        """

        try:
            return self.__get_color_and_value(card)[1]
        except TypeError:
            pass

    def __get_score(self, value: str, color: str = None) -> int:
        """Returns the score (i.e. weight/bias) of an UNO card of a value.

        Args:
            value: The value of an UNO card
            color: The color of an UNO card

        Returns:
            The score (i.e. weight/bias) of an UNO card of the value
        """

        def get_pts(player_id: str, dark: bool) -> int:
            if str.isdigit(player_id):
                cards = games[str(self.guild.id)]['players'][player_id]['cards']
            else:
                cards = games[str(self.guild.id)]['players'][player_id].cards

            score = 0
            for card in cards:
                if not games[str(self.guild.id)]['settings']['Flip'] and not dark:
                    value = search(r'skip|reverse|wild|\d|\+[42]', card).group(0)

                    if value in ('+2', 'skip', 'reverse'):
                        score += 20
                    elif value in ('+4', 'wild'):
                        score += 50
                    else:
                        score += int(value)

                elif not games[str(self.guild.id)]['dark'] and not dark:
                    value = search(r'skip|reverse|wild|flip|\d|\+[21]', card[0]).group(0)

                    if value == '+1':
                        score += 10
                    elif value in ('reverse', 'flip', 'skip'):
                        score += 20
                    elif value == 'wild':
                        score += 40
                    elif value == '+2':
                        score += 50
                    else:
                        score += int(value)

                else:
                    value = search(r'skip|reverse|wild|flip|\d|\+[5c]', card[1]).group(0)

                    if value in ('+5', 'reverse', 'flip'):
                        score += 20
                    elif value == 'skip':
                        score += 30
                    elif value == 'wild':
                        score += 40
                    elif value == '+c':
                        score += 60
                    else:
                        score += int(value)

            return score

        d = self.games[str(self.guild.id)]

        if not d['settings']['Flip']:
            if value in ('skip', 'reverse'):
                if len(d['players']) == 2 or value == 'skip':
                    score = 20
                else:
                    player_ids = list(d['players'].keys())
                    nxt = player_ids[(player_ids.index(self.name) - 1 + len(player_ids)) % len(player_ids)]

                    if str.isdigit(nxt) and len(d['players'][nxt]['cards']) == 1 or not str.isdigit(nxt) and len(
                            d['players'][nxt].cards) == 1:
                        score = 1
                    else:
                        score = 20
            elif value == '+2':
                least = sum(1 for x in self.cards if self.__get_value(x) in ('+2', '+4'))
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        total += len(d['players'][player]['cards'])
                    else:
                        total += len(d['players'][player].cards)
                    n += 1

                prob = 0
                hands = total + len(self.cards)
                if n * least <= 12 * ((total + len(self.cards)) % 108 + 1):
                    for i in range(n * least):
                        if i <= total:
                            prob += comb(12 * (hands // 108 + 1) - least, i) * comb(96 * (hands // 108 + 1) - len(self.cards) + least,
                                                                           total - i) / comb(
                                108 * (hands // 108 + 1) - len(self.cards), total)

                if prob > 0.6:
                    score = 10 * prob
                else:
                    score = 0
            elif value == 'wild':
                return 1
            elif value == '+4':
                least = sum(1 for x in self.cards if self.__get_value(x) == '+4')
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        total += len(d['players'][player]['cards'])
                    else:
                        total += len(d['players'][player].cards)
                    n += 1

                prob = 0
                hands = total + len(self.cards)
                if n * least <= 4 * ((total + len(self.cards)) % 108 + 1):
                    for i in range(n * least):
                        if i <= total:
                            prob += comb(4 * (hands // 108 + 1) - least, i) * comb(
                                104 * (hands // 108 + 1) - len(self.cards) + least,
                                total - i) / comb(
                                108 * (hands // 108 + 1) - len(self.cards), total)

                if prob > 0.6:
                    score = 10 * prob
                else:
                    score = 0
            else:
                score = int(value)

        elif not d['dark']:
            if value == '+1':
                least = sum(1 for x in self.cards if self.__get_value(x) in ('+1', '+2'))
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        total += len(d['players'][player]['cards'])
                    else:
                        total += len(d['players'][player].cards)
                    n += 1

                prob = 0
                hands = total + len(self.cards)
                if n * least <= 12 * (hands % 112 + 1):
                    for i in range(n * least):
                        if i <= total:
                            prob += comb(12 * (hands // 112 + 1) - least, i) * comb(100 * (hands // 112 + 1) - len(self.cards) + least,
                                                                           total - i) / comb(
                                112 * (hands // 112 + 1) - len(self.cards), total)

                if prob > 0.6:
                    score = 10 * prob
                else:
                    score = 0
            elif value in {'reverse', 'skip'}:
                if len(d['players']) == 2 or value == 'skip':
                    score = 20
                else:
                    player_ids = list(d['players'].keys())
                    nxt = player_ids[(player_ids.index(self.name) - 1 + len(player_ids)) % len(player_ids)]

                    if str.isdigit(nxt) and len(d['players'][nxt]['cards']) == 1 or not str.isdigit(nxt) and len(
                            d['players'][nxt].cards) == 1:
                        score = 0
                    else:
                        score = 20
            elif value == 'flip':
                max_ratio = 0

                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        ratio = get_pts(player, True) / len(d['players'][player]['cards'])
                    else:
                        ratio = get_pts(player, True) / len(d['players'][player].cards)

                    if ratio > max_ratio:
                        max_ratio = ratio

                if get_pts(self.name, True) / len(self.cards) > max_ratio:
                    score = 20
                elif max_ratio < 25:
                    score = 1
                else:
                    score = 0

            elif value == 'wild':
                score = 1
            elif value == '+2':
                least = sum(1 for x in self.cards if self.__get_value(x) == '+2')
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        total += len(d['players'][player]['cards'])
                    else:
                        total += len(d['players'][player].cards)
                    n += 1

                prob = 0
                hands = total + len(self.cards)
                if n * least <= 4 * (hands % 112 + 1):
                    for i in range(n * least):
                        if i <= total:
                            prob += comb(4 * (hands // 112 + 1) - least, i) * comb(
                                108 * (hands // 112 + 1) - len(self.cards) + least,
                                total - i) / comb(
                                112 * (hands // 112 + 1) - len(self.cards), total)

                if prob > 0.6:
                    score = 10 * prob
                else:
                    score = 0
            else:
                score = int(value)

        else:
            if value == 'reverse':
                if len(d['players']) == 2:
                    score = 20
                else:
                    player_ids = list(d['players'].keys())
                    nxt = player_ids[(player_ids.index(self.name) - 1 + len(player_ids)) % len(player_ids)]

                    if str.isdigit(nxt) and len(d['players'][nxt]['cards']) == 1 or not str.isdigit(nxt) and len(
                            d['players'][nxt].cards) == 1:
                        score = 1
                    else:
                        score = 20
            elif value == '+5':
                least = sum(1 for x in self.cards if self.__get_value(x) == '+5')
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        total += len(d['players'][player]['cards'])
                    else:
                        total += len(d['players'][player].cards)
                    n += 1

                prob = 0
                hands = total + len(self.cards)
                if n * least <= 8 * (hands % 112 + 1):
                    for i in range(n * least):
                        if i <= total:
                            prob += comb(8 * (hands // 112 + 1) - least, i) * comb(104 * (hands // 112 + 1) - len(self.cards) + least,
                                                                          total - i) / comb(
                                112 * (hands // 112 + 1) - len(self.cards), total)

                if prob > 0.6:
                    score = 10 * prob
                else:
                    score = 0
            elif value == 'skip':
                score = 20
            elif value == 'flip':
                max_ratio = 0

                for player in [x for x in d['players'] if x != self.name]:
                    if str.isdigit(player):
                        ratio = get_pts(player, False) / len(d['players'][player]['cards'])
                    else:
                        ratio = get_pts(player, False) / len(d['players'][player].cards)

                    if ratio > max_ratio:
                        max_ratio = ratio

                if get_pts(self.name, False) / len(self.cards) > max_ratio:
                    score = 20
                elif max_ratio < 25:
                    score = 1
                else:
                    score = 0
            elif value in {'wild', '+color'}:
                score = 1
            else:
                score = int(value)

        if (color in self.losing_colors or value in self.losing_values) and score > 0:
            bot_pos = None
            min_pos = 0
            for i in range(len(d['players'].keys())):
                if list(d['players'].keys())[i] == self.name:
                    bot_pos = i
                else:
                    item, min = list(d['players'].keys())[i], list(d['players'].keys())[min_pos]
                    min_is_bot = not str.isdigit(min)
                    item_is_bot = not str.isdigit(item)

                    if item_is_bot:
                        if min_is_bot and len(d['players'][item].cards) < len(
                                d['players'][min].cards) or not min_is_bot and len(d['players'][item].cards) < len(
                            d['players'][min]['cards']):
                            min_pos = i
                    else:
                        if min_is_bot and len(d['players'][item].cards) < len(
                                d['players'][min]['cards']) or not min_is_bot and len(
                            d['players'][item]['cards']) < len(
                            d['players'][min]['cards']):
                            min_pos = i

            min = list(d['players'].keys())[min_pos]
            if str.isdigit(min):
                return score * (1 - ceil(e**(abs(bot_pos - min_pos)*(1 - len(d['players'][min]['cards']))/5)))
            else:
                return score * (1 - ceil(e**(abs(bot_pos - min_pos)*(1 - len(d['players'][min].cards))/5)))

        return score

    def __is_similar(self, x: Union[str, tuple], y: Union[str, tuple]) -> bool:
        """Checks if cards x and y are similar.

        Args:
            x: An UNO card
            y: Another UNO card

        Returns:
            bool: Whether x and y are similar
        """

        return self.__get_color(x) == self.__get_color(y) or self.__get_value(x) == self.__get_value(
            y) or any(t in ('+4', 'wild') or t[0] in ('+2', 'wild') and not
        self.games[str(self.guild.id)]['dark'] or t[1] in ('+color', 'wild') and self.games[str(self.guild.id)]['dark']
                      for t in (x, y))

    def __build_tree(self, tree: Tree, root: str):
        """Builds a tree (i.e. neural network) according to the optimal strategy.

        Args:
            tree: A tree to be built
            root: The root to which children will be added
        """

        self.reccount += 1

        d = self.games[str(self.guild.id)]

        if not d['settings']['Flip']:
            for card in [x for x in self.cards if
                         not any(x in c for c in tree.rsearch(root)) and self.__is_similar(x, root)]:
                color, value = self.__get_color_and_value(card)
                count = 0

                while True:
                    try:
                        tree.create_node(identifier=card + str(count), tag=str(count),
                                         data=self.__get_score(value, color), parent=root)
                    except DuplicatedNodeIdError:
                        count += 1
                        continue
                    else:
                        break

                if self.reccount <= 1000:
                    self.__build_tree(tree, card + str(count))

        elif not d['dark']:
            rcard = tuple(root.split('|'))

            if self.__get_value(rcard) == 'flip':
                return

            for card in [x for x in self.cards if
                         not any(x[0] + '|' + x[1] in c for c in tree.rsearch(root)) and self.__is_similar(x, rcard)]:
                color, value = self.__get_color_and_value(card)
                count = 0

                while True:
                    try:
                        tree.create_node(identifier=card[0] + '|' + card[1] + str(count), tag=str(count),
                                         data=self.__get_score(value, color), parent=root)

                        if value == 'flip':
                            return
                    except DuplicatedNodeIdError:
                        count += 1
                        continue
                    else:
                        break

                if self.reccount <= 1000:
                    self.__build_tree(tree, card[0] + '|' + card[1] + str(count))

        else:
            rcard = tuple(root.split('|'))

            if self.__get_value(rcard) == 'flip':
                return

            for card in [x for x in self.cards if not any(
                    x[0] + '|' + x[1].replace('dark', '') in c for c in tree.rsearch(root)) and self.__is_similar(x,
                                                                                                                  rcard)]:
                color, value = self.__get_color_and_value(card)
                count = 0

                while True:
                    try:
                        tree.create_node(identifier=card[0] + '|' + card[1] + str(count), tag=str(count),
                                         data=self.__get_score(value, color), parent=root)
                    except DuplicatedNodeIdError:
                        count += 1
                        continue
                    else:
                        break

                if self.reccount <= 1000:
                    self.__build_tree(tree, card[0] + '|' + card[1] + str(count))

    async def __execute_card(self, value: str):
        """Executes an UNO card according to its value.

        Args:
            value: The value of an UNO card
        """

        if str(self.guild.id) not in ending:
            n = None
            try:
                p = [x for x in self.games[str(self.guild.id)]['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in games[str(self.guild.id)]['players'][x]]
            except KeyError:
                return

            temp = iter(p)
            for key in temp:
                if key == self.name:
                    n = next(temp, next(iter(p)))
                    if str.isdigit(n):
                        n = self.guild.get_member(int(n))
                    break

            if value in [str(x) for x in range(10)]:
                if str(self.guild.id) in self.games:
                    await display_cards(n, self.guild)

            elif value == '+4':
                if str(self.guild.id) in self.games:
                    if str(self.guild.id) not in stack:
                        stack[str(self.guild.id)] = 4
                    else:
                        stack[str(self.guild.id)] += 4

                    if isinstance(n, Member) and self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                            '+4' in card for card in self.games[str(self.guild.id)]['players'][str(n.id)]['cards']):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in self.channels])

                        await display_cards(n, self.guild)

                    elif isinstance(n, str) and self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                            '+4' in card for card in self.games[str(self.guild.id)]['players'][n].cards):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in self.channels])

                        await display_cards(n, self.guild)

                    else:
                        await draw(n, self.guild, stack[str(self.guild.id)])

                        del stack[str(self.guild.id)]

                        m = next(temp, next(iter(p)))
                        if str.isdigit(m):
                            m = self.guild.get_member(int(m))
                        if m == n:
                            iterable = iter(p)
                            next(iterable)
                            m = next(temp, next(iterable))
                            if str.isdigit(m):
                                m = self.guild.get_member(int(m))

                        await display_cards(m, self.guild)

            elif value == 'reverse':
                if str(self.guild.id) in self.games:
                    d = self.games[str(self.guild.id)]
                    player_ids = [x for x in d['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in d['players'][x]]

                    if len(player_ids) > 2:
                        player_ids.reverse()

                        ordered_dict = OrderedDict()
                        for x in player_ids:
                            ordered_dict[x] = d['players'][x]

                        d['players'] = dict(ordered_dict)

                        await asyncio.gather(*[asyncio.create_task(x.send(
                            embed=discord.Embed(description='**The player order is reversed.**',
                                                color=discord.Color.red()))) for x in self.channels])

                        p = [x for x in d['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in d['players'][x]]
                        m = None
                        temp = iter(p)
                        for key in temp:
                            if key == self.name:
                                m = next(temp, next(iter(p)))
                                if str.isdigit(m):
                                    m = self.guild.get_member(int(m))
                                break

                        await display_cards(m, self.guild)

                    else:
                        m = next(temp, next(iter(p)))
                        if str.isdigit(m):
                            m = self.guild.get_member(int(m))
                        if m == n:
                            iterable = iter(p)
                            next(iterable)
                            m = next(temp, next(iterable))
                            if str.isdigit(m):
                                m = self.guild.get_member(int(m))

                        if isinstance(n, Member):
                            await asyncio.gather(*[asyncio.create_task(x.send(
                                embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                    color=discord.Color.red()))) for x in self.channels])
                        else:
                            await asyncio.gather(*[asyncio.create_task(x.send(
                                embed=discord.Embed(description='**' + n + ' is skipped.**',
                                                    color=discord.Color.red()))) for x in self.channels])

                        await display_cards(m, self.guild)

            elif value == 'skip':
                if str(self.guild.id) in self.games:
                    if not self.games[str(self.guild.id)]['settings']['Flip'] or not self.games[str(self.guild.id)][
                        'dark']:
                        m = next(temp, next(iter(p)))
                        if str.isdigit(m):
                            m = self.guild.get_member(int(m))
                        if m == n:
                            iterable = iter(p)
                            next(iterable)
                            m = next(temp, next(iterable))
                            if str.isdigit(m):
                                m = self.guild.get_member(int(m))

                        if isinstance(n, Member):
                            await asyncio.gather(*[asyncio.create_task(x.send(
                                embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                    color=discord.Color.red()))) for x in
                                self.channels])
                        else:
                            await asyncio.gather(*[asyncio.create_task(x.send(
                                embed=discord.Embed(description='**' + n + ' is skipped.**',
                                                    color=discord.Color.red()))) for x in
                                self.channels])

                        await display_cards(m, self.guild)

                    else:
                        await asyncio.gather(*[asyncio.create_task(x.send(
                            embed=discord.Embed(description='**Everyone is skipped!**',
                                                color=discord.Color.red()))) for x in
                            self.channels])

                        await display_cards(self.name, self.guild)

            elif value == 'wild':
                if str(self.guild.id) in self.games:
                    await display_cards(n, self.guild)

            elif value == '+2':
                if str(self.guild.id) in self.games:
                    if str(self.guild.id) not in stack:
                        stack[str(self.guild.id)] = 2
                    else:
                        stack[str(self.guild.id)] += 2

                    if isinstance(n, Member) and self.games[str(self.guild.id)]['settings']['StackCards'] and (
                            any('+2' in card for card in
                                self.games[str(self.guild.id)]['players'][str(n.id)]['cards']) or any(
                        '+4' in card for card in self.games[str(self.guild.id)]['players'][str(n.id)]['cards'])):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in
                            self.channels])

                        await display_cards(n, self.guild)

                    elif isinstance(n, str) and self.games[str(self.guild.id)]['settings']['StackCards'] and (
                            any('+2' in card for card in
                                self.games[str(self.guild.id)]['players'][n].cards) or any(
                        '+4' in card for card in self.games[str(self.guild.id)]['players'][n].cards)):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in
                            self.channels])

                        await display_cards(n, self.guild)

                    else:
                        await draw(n, self.guild, stack[str(self.guild.id)])

                        del stack[str(self.guild.id)]

                        m = next(temp, next(iter(p)))
                        if str.isdigit(m):
                            m = self.guild.get_member(int(m))
                        if m == n:
                            iterable = iter(p)
                            next(iterable)
                            m = next(temp, next(iterable))
                            if str.isdigit(m):
                                m = self.guild.get_member(int(m))

                        await display_cards(m, self.guild)

                else:
                    if not self.games[str(self.guild.id)]['dark']:
                        if str(self.guild.id) in self.games:
                            if str(self.guild.id) not in stack:
                                stack[str(self.guild.id)] = 2
                            else:
                                stack[str(self.guild.id)] += 2

                            if isinstance(n, Member) and self.games[str(self.guild.id)]['settings'][
                                'StackCards'] and any(
                                    card[0] == '+2' for card in
                                    self.games[str(self.guild.id)]['players'][str(n.id)]['cards']):
                                await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                        stack[str(self.guild.id)]) + ' cards.**',
                                    color=discord.Color.red()))) for x in
                                    self.channels])

                                await display_cards(n, self.guild)

                            elif isinstance(n, str) and self.games[str(self.guild.id)]['settings'][
                                'StackCards'] and any(
                                    card[0] == '+2' for card in
                                    self.games[str(self.guild.id)]['players'][n].cards):
                                await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                    description='**' + n + ' can choose to stack cards or draw ' + str(
                                        stack[str(self.guild.id)]) + ' cards.**',
                                    color=discord.Color.red()))) for x in
                                    self.channels])

                                await display_cards(n, self.guild)

                            else:
                                await draw(n, self.guild, stack[str(self.guild.id)])

                                del stack[str(self.guild.id)]

                                m = next(temp, next(iter(p)))
                                if str.isdigit(m):
                                    m = self.guild.get_member(int(m))
                                if m == n:
                                    iterable = iter(p)
                                    next(iterable)
                                    m = next(temp, next(iterable))
                                    if str.isdigit(m):
                                        m = self.guild.get_member(int(m))
                                await display_cards(m, self.guild)

            elif value == '+1':
                if self.games[str(self.guild.id)]['settings']['Flip'] and not self.games[str(self.guild.id)][
                    'dark']:
                    if str(self.guild.id) in self.games:
                        if str(self.guild.id) not in stack:
                            stack[str(self.guild.id)] = 1
                        else:
                            stack[str(self.guild.id)] += 1

                        if isinstance(n, Member) and self.games[str(self.guild.id)]['settings']['StackCards'] and (
                                any('+1' in card[0] for card in
                                    self.games[str(self.guild.id)]['players'][str(n.id)]['cards']) or any(
                            card[0] == '+2' for card in
                            self.games[str(self.guild.id)]['players'][str(n.id)]['cards'])):

                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                    stack[str(self.guild.id)]) + ' cards.**',
                                color=discord.Color.red()))) for x in
                                self.channels])

                            await display_cards(n, self.guild)

                        elif isinstance(n, str) and self.games[str(self.guild.id)]['settings']['StackCards'] and (
                                any('+1' in card[0] for card in
                                    self.games[str(self.guild.id)]['players'][n].cards) or any(
                            card[0] == '+2' for card in
                            self.games[str(self.guild.id)]['players'][n].cards)):

                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                description='**' + n + ' can choose to stack cards or draw ' + str(
                                    stack[str(self.guild.id)]) + ' cards.**',
                                color=discord.Color.red()))) for x in
                                self.channels])

                            await display_cards(n, self.guild)

                        else:
                            await draw(n, self.guild, stack[str(self.guild.id)])

                            del stack[str(self.guild.id)]

                            m = next(temp, next(iter(p)))
                            if str.isdigit(m):
                                m = self.guild.get_member(int(m))
                            if m == n:
                                iterable = iter(p)
                                next(iterable)
                                m = next(temp, next(iterable))
                                if str.isdigit(m):
                                    m = self.guild.get_member(int(m))

                            await display_cards(m, self.guild)

            elif value == '+5':
                if str(self.guild.id) in self.games:
                    if str(self.guild.id) not in stack:
                        stack[str(self.guild.id)] = 5
                    else:
                        stack[str(self.guild.id)] += 5

                    if isinstance(n, Member) and self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                            '+5' in card[1] for card in
                            self.games[str(self.guild.id)]['players'][str(n.id)]['cards']):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in
                            self.channels])

                        await display_cards(n, self.guild)

                    elif isinstance(n, str) and self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                            '+5' in card[1] for card in
                            self.games[str(self.guild.id)]['players'][n].cards):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in
                            self.channels])

                        await display_cards(n, self.guild)

                    else:
                        await draw(n, self.guild, stack[str(self.guild.id)])

                        del stack[str(self.guild.id)]

                        m = next(temp, next(iter(p)))
                        if str.isdigit(m):
                            m = self.guild.get_member(int(m))
                        if m == n:
                            iterable = iter(p)
                            next(iterable)
                            m = next(temp, next(iterable))
                            if str.isdigit(m):
                                m = self.guild.get_member(int(m))

                        await display_cards(m, self.guild)

            elif value == '+color':
                if str(self.guild.id) in self.games:
                    await draw(n, self.guild, 1, False, True)

                    m = next(temp, next(iter(p)))
                    if str.isdigit(m):
                        m = self.guild.get_member(int(m))
                    if m == n:
                        iterable = iter(p)
                        next(iterable)
                        m = next(temp, next(iterable))
                        if str.isdigit(m):
                            m = self.guild.get_member(int(m))
                    await display_cards(m, self.guild)

            elif value == 'flip':
                if str(self.guild.id) in self.games:
                    self.games[str(self.guild.id)]['dark'] = not self.games[str(self.guild.id)][
                        'dark']
                    self.games[str(self.guild.id)]['current'], self.games[str(self.guild.id)]['current_opposite'] = \
                        self.games[str(self.guild.id)]['current_opposite'], self.games[str(self.guild.id)]['current']

                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                        description='**Everything is flipped!**',
                        color=discord.Color.red()))) for x in self.channels])

                    await display_cards(n, self.guild)

    async def play(self):
        """Plays an UNO card."""

        if str(self.guild.id) not in ending:
            d = self.games[str(self.guild.id)]

            if not d['settings']['Flip']:
                if str(self.guild.id) not in stack:
                    self.playables = tuple(x for x in self.cards if self.__is_similar(x, d['current']))
                elif '+2' in d['current']:
                    self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+2')
                    if not self.playables:
                        self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+4')
                else:
                    self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+4')
            elif not d['dark']:
                if str(self.guild.id) not in stack:
                    self.playables = tuple(x for x in self.cards if self.__is_similar(x, d['current']))
                elif self.__get_value(d['current']) == '+1':
                    self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+1')
                    if not self.playables:
                        self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+2')
                else:
                    self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+2')
            else:
                if str(self.guild.id) not in stack:
                    self.playables = tuple(x for x in self.cards if self.__is_similar(x, d['current']))
                else:
                    self.playables = tuple(x for x in self.cards if self.__get_value(x) == '+5')

            n = None
            p = [x for x in d['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in d['players'][x]]

            temp = iter(p)
            for key in temp:
                if key == self.name:
                    n = next(temp, next(iter(p)))
                    if str.isdigit(n):
                        n = self.guild.get_member(int(n))
                    break

            if not self.playables:
                if str(self.guild.id) in stack:
                    await draw(self.name, self.guild, stack[str(self.guild.id)])
                    del stack[str(self.guild.id)]
                    await display_cards(n, self.guild)
                elif self.games[str(self.guild.id)]['settings']['DrawUntilMatch']:
                    await draw(self.name, self.guild, 1, True)
                    await display_cards(self.name, self.guild)
                else:
                    await draw(self.name, self.guild, 1)
                    await display_cards(n, self.guild)

            else:
                if not d['settings']['Flip']:
                    if not all(t == '+4' for t in self.playables):
                        self.playables = [x for x in self.playables if x != '+4']
                    if not all(t == 'wild' for t in self.playables):
                        self.playables = [x for x in self.playables if x != 'wild']

                    if len(self.cards) == 1:
                        if self.playables[0] in {'wild', '+4'}:
                            best = 'blue' + self.playables[0]
                        else:
                            best = self.playables[0]
                    else:
                        color_change = 'blue'
                        optimals = []
                        self.reccount = 0

                        for card in self.playables:
                            tree = Tree()
                            tree.create_node(identifier=card, data=self.__get_score(self.__get_value(card)))
                            self.__build_tree(tree, card)

                            paths = tree.paths_to_leaves()

                            score = [sum(map(lambda x: tree.get_node(x).data * e ** (-path.index(x)), path)) for path in
                                     paths]
                            for c in paths[score.index(max(score))]:
                                if self.__get_color(c):
                                    color_change = self.__get_color(c)
                                    break

                            optimals.append(max(score))

                        best = self.playables[optimals.index(max(optimals))]
                        if not self.__get_color(best):
                            best = color_change + best

                elif not d['dark']:
                    if not all(t[0] == '+2' for t in self.playables):
                        self.playables = [x for x in self.playables if x[0] != '+2']
                    if not all(t[0] == 'flip' for t in self.playables):
                        self.playables = [x for x in self.playables if x[0] != 'flip']
                    if not all(t[0] == 'wild' for t in self.playables):
                        self.playables = [x for x in self.playables if x[0] != 'wild']

                    if len(self.cards) == 1:
                        if self.playables[0][0] in {'wild', '+2'}:
                            best = ('blue' + self.playables[0][0], self.playables[0][1])
                        else:
                            best = self.playables[0]
                    else:
                        color_change = 'blue'
                        optimals = []
                        self.reccount = 0

                        for card in self.playables:
                            tree = Tree()
                            tree.create_node(identifier=card[0] + '|' + card[1],
                                             data=self.__get_score(self.__get_value(card)))
                            self.__build_tree(tree, card[0] + '|' + card[1])

                            paths = tree.paths_to_leaves()

                            score = [sum(map(lambda x: tree.get_node(x).data * e ** (-path.index(x)), path)) for path in
                                     paths]
                            for c in paths[score.index(max(score))]:
                                if self.__get_color(tuple(c.split('|'))):
                                    color_change = self.__get_color(tuple(c.split('|')))
                                    break

                            optimals.append(max(score))

                        best = self.playables[optimals.index(max(optimals))]
                        if not self.__get_color(best):
                            best = (color_change + best[0], best[1])

                else:
                    if not all(t[1] == '+color' for t in self.playables):
                        self.playables = [x for x in self.playables if x[1] != '+color']
                    if not all(t[1] == 'flip' for t in self.playables):
                        self.playables = [x for x in self.playables if x[1] != 'flip']
                    if not all(t[1] == 'darkwild' for t in self.playables):
                        self.playables = [x for x in self.playables if x[1] != 'darkwild']

                    if len(self.cards) == 1:
                        if self.playables[0][1] == '+color':
                            best = (self.playables[0][0], 'teal+color')
                        elif self.playables[0][1] == 'darkwild':
                            best = (self.playables[0][0], 'tealwild')
                        else:
                            best = self.playables[0]
                    else:
                        color_change = 'teal'
                        optimals = []
                        self.reccount = 0

                        for card in self.playables:
                            tree = Tree()
                            if card[1] != 'darkwild':
                                tree.create_node(identifier=card[0] + '|' + card[1],
                                                 data=self.__get_score(self.__get_value(card)))
                                self.__build_tree(tree, card[0] + '|' + card[1])
                            else:
                                tree.create_node(identifier=card[0] + '|wild',
                                                 data=self.__get_score(self.__get_value(card)))
                                self.__build_tree(tree, card[0] + '|wild')

                            paths = tree.paths_to_leaves()

                            score = [sum(map(lambda x: tree.get_node(x).data * e ** (-path.index(x)), path)) for path in
                                     paths]
                            for c in paths[score.index(max(score))]:
                                if self.__get_color(tuple(c.split('|'))):
                                    color_change = self.__get_color(tuple(c.split('|')))
                                    break

                            optimals.append(max(score))

                        best = self.playables[optimals.index(max(optimals))]
                        if not self.__get_color(best):
                            if best[1] == 'darkwild':
                                best = (best[0], color_change + 'wild')
                            else:
                                best = (best[0], color_change + best[1])

                if self.__get_score(self.__get_value(best)) > 0 or (
                        self.__get_value(best) == 'flip' and len(self.cards) == 1) or len(self.cards) == 1:
                    await play_card(best, self.name, self.guild)
                    await self.__execute_card(self.__get_value(best))
                else:
                    if str(self.guild.id) in stack:
                        await draw(self.name, self.guild, stack[str(self.guild.id)])
                        del stack[str(self.guild.id)]
                        await display_cards(n, self.guild)
                    elif self.games[str(self.guild.id)]['settings']['DrawUntilMatch']:
                        await draw(self.name, self.guild, 1, True)
                        await display_cards(self.name, self.guild)
                    else:
                        await draw(self.name, self.guild, 1)
                        await display_cards(n, self.guild)


# Events
@client.event
async def on_ready():
    # Initialize UNOBot
    await initialize()

    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] Guilds:')
    for guild in client.guilds:
        print(f'{guild.id} | {guild.name}')
    # Print a ready message to the console once initialization is complete
    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] UNOBot is ready.')


@client.event
async def on_guild_join(guild):
    # Update the configuration files
    await initialize()

    # Create a category for all UNO games if there is none
    await guild.create_category('UNO-GAME')

    # Print a success message to the console
    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] UNOBot has joined the guild ' + str(
        guild) + '.')
    await guild.text_channels[0].send(
        f"**Thanks for adding UNOBot!** :thumbsup:\n• `{prefix}` is my prefix.\n• Use `{prefix}commands` for a list of commands.\n• Use `{prefix}help` if you need help.\n• Use `{prefix}guide` for an in-depth guide on me.\n"
    )


@client.event
async def on_guild_remove(guild):
    # Update the configuration files
    await initialize()

    # Print a success message to the console
    print(
        '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] UNOBot has left the guild ' + str(guild) + '.')


@client.event
async def on_member_join(member):
    # Add user data to user configuration file if the user is not a bot
    if not member.bot:
        users_file = s3_resource.Object('unobot-bucket', 'users.json')
        user_stuff = json.loads(users_file.get()['Body'].read().decode('utf-8'))

        if str(member.id) in user_stuff:
            user_stuff[str(member.id)][str(member.guild.id)] = {
                'Wins': 0,
                'Score': 0,
                'Played': 0
            }

        else:
            user_stuff[str(member.id)] = {
                str(member.guild.id): {
                    'Wins': 0,
                    'Score': 0,
                    'Played': 0
                }}

        users_file.put(Body=json.dumps(user_stuff).encode('utf-8'))


@client.event
async def on_member_remove(member):
    # Remove user data from user configuration file if the user is not a bot
    if not member.bot:
        users_file = s3_resource.Object('unobot-bucket', 'users.json')
        user_stuff = json.loads(users_file.get()['Body'].read().decode('utf-8'))

        for guild in [x for x in client.guilds if
                      not x.get_member(member.id) and str(x.id) in user_stuff[str(member.id)]]:
            del user_stuff[str(member.id)][str(guild.id)]

            if no_guild(member):
                del user_stuff[str(member.id)]

        users_file.put(Body=json.dumps(user_stuff).encode('utf-8'))


@client.event
async def on_user_update(before, after):
    # Change the names of a player's UNO channels and the player's name in the game invitation message
    # if they modify their name mid-game
    for guild_id in games:
        guild = client.get_guild(int(guild_id))

        if guild.get_member(before.id):
            channel = discord.utils.get(guild.text_channels, name=sub(r'[^\w -]', '', before.name.lower().replace(' ',
                                                                                                                  '-')) + '-uno-channel')

            if channel:
                await channel.edit(name=sub(r'[^\w -]', '', after.name.lower().replace(' ', '-')) + '-uno-channel')

        for channel in guild.text_channels:
            try:
                m = await channel.fetch_message(games[str(guild.id)]['message'])
            except (discord.NotFound, discord.Forbidden):
                continue
            else:
                break
        m_dict = m.embeds[0].to_dict()
        for field in m_dict['fields']:
            if field['name'] == 'Players:':
                field['value'] = field['value'].replace(f':small_blue_diamond: {before.name}',
                                                        f':small_blue_diamond: {after.name}')
                break

        await m.edit(embed=discord.Embed.from_dict(m_dict))


@client.event
async def on_message(message):
    """Handles resetting and all the card playing

    Args:
        message: The message sent by a Discord user
    """

    if message.content == 'CONFIRM':
        commands_file = s3_resource.Object('unobot-bucket', 'commands.json')
        commands = json.loads(commands_file.get()['Body'].read().decode('utf-8'))

        if message.guild.id in resets:
            if commands[str(message.guild.id)]['settings']['Whitelist'] and message.author.id in \
                    commands[str(message.guild.id)]['settings'][
                        'Whitelist'] or message.author == message.guild.owner:

                dgs_file = s3_resource.Object('unobot-bucket', 'dgs.json')
                dgs = json.loads(dgs_file.get()['Body'].read().decode('utf-8'))
                dgs[str(message.guild.id)] = default_dgs
                dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                users_file = s3_resource.Object('unobot-bucket', 'users.json')
                users = json.loads(users_file.get()['Body'].read().decode('utf-8'))
                for member in [x for x in message.guild.members if x.id != client.user.id and not x.bot]:
                    users[str(member.id)][str(message.guild.id)] = {
                        'Wins': 0,
                        'Score': 0,
                        'Played': 0
                    }
                users_file.put(Body=json.dumps(users).encode('utf-8'))

                commands[str(message.guild.id)] = default_command_settings
                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                await client.get_channel(message.channel.id).send(
                    embed=discord.Embed(description=':thumbsup: **UNOBot has been reset.**',
                                        color=discord.Color.red()))

            else:
                await client.get_channel(message.channel.id).send(
                    embed=discord.Embed(description=':lock: **You do not have permission to confirm the reset.**',
                                        color=discord.Color.red()))

    elif message.channel.category.name == 'UNO-GAME' and message.author != client.user and str(
            message.guild.id) not in ending and message.channel.name != 'spectator-uno-channel':

        try:
            n = None
            p = [x for x in games[str(message.guild.id)]['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in games[str(message.guild.id)]['players'][x]]

            temp = iter(p)
            for key in temp:
                if key == str(message.author.id):
                    n = next(temp, next(iter(p)))
                    if str.isdigit(n):
                        n = message.guild.get_member(int(n))
                    break

            card = message.content.lower()

            rprefix = prefix.replace('.', '\.')
            if search(rf'{rprefix}', card):
                await client.process_commands(message)

                return

            if not games[str(message.guild.id)]['settings']['Flip'] or not games[str(message.guild.id)]['dark']:
                color = search(r'^([cad]|(s|say)(?= )|cards*|alert|draw|[rbgy]|red|blue|green|yellow)', card)
            else:
                color = search(r'^([cad]|(s|say)(?= )|cards*|alert|draw|[ptoz]|pink|teal|orange|purple)', card)

            if not color:
                await message.channel.send(
                    embed=discord.Embed(
                        description=':x: **I don\'t understand your command.**',
                        color=discord.Color.red()))
            else:
                color = color.group(0)

            value = search(r'(?<=[a-z ])(skip|reverse|wild|flip|\d|[+d](raw)* *([c4251]|colou*r)|[srwf]$)', card)
            if value:
                value = value.group(0)

            if color == 'r':
                color = 'red'
            elif color == 'b':
                color = 'blue'
            elif color == 'g':
                color = 'green'
            elif color == 'y':
                color = 'yellow'
            elif color == 'p':
                color = 'pink'
            elif color == 't':
                color = 'teal'
            elif color == 'o':
                color = 'orange'
            elif color == 'z':
                color = 'purple'
            elif color and any(x in color for x in ('d', 'draw')) and games[str(message.guild.id)][
                'player'] == message.author.id:
                overwrite = message.channel.overwrites_for(message.author)
                overwrite.send_messages = False
                overwrite.read_messages = True
                await message.channel.set_permissions(message.author, overwrite=overwrite)

                if str(message.guild.id) in stack:
                    await draw(message.author, message.guild, stack[str(message.guild.id)])
                    del stack[str(message.guild.id)]
                    await display_cards(n, message.guild)
                elif games[str(message.guild.id)]['settings']['DrawUntilMatch']:
                    await draw(message.author, message.guild, 1, True)
                    await display_cards(message.author, message.guild)
                else:
                    await draw(message.author, message.guild, 1)
                    await display_cards(n, message.guild)

                overwrite.send_messages = True
                try:
                    await message.channel.set_permissions(message.author, overwrite=overwrite)
                except discord.NotFound:
                    pass

                return

            elif color in ('s', 'say'):
                say = sub(r'^s(ay)*', '', message.content, flags=I)

                await asyncio.gather(*[asyncio.create_task(
                    x.send(embed=discord.Embed(title=message.author.name + ' says:', description=say,
                                               color=discord.Color.red()))) for x in
                    message.channel.category.text_channels if x != message.channel])

                await message.add_reaction('\N{THUMBS UP SIGN}')

                return

            elif color in ('a', 'alert'):
                if 'alert' not in cooldowns[str(message.guild.id)]:
                    current_player = None
                    if isinstance(games[str(message.guild.id)]['player'], int):
                        current_player = message.guild.get_member(games[str(message.guild.id)]['player'])

                    if message.author != current_player:
                        await discord.utils.get(message.channel.category.text_channels,
                                                name=sub(r'[^\w -]', '',
                                                         current_player.name.lower().replace(' ',
                                                                                             '-')) + '-uno-channel').send(
                            embed=discord.Embed(
                                description=':warning: **' + current_player.mention + '! ' + message.author.name + ' alerted you!**',
                                color=discord.Color.red()))

                        await message.add_reaction('\N{THUMBS UP SIGN}')

                        cooldowns[str(message.guild.id)].append('alert')
                        await asyncio.sleep(30)
                        cooldowns[str(message.guild.id)].remove('alert')

                    else:
                        await message.channel.send(
                            embed=discord.Embed(
                                description=':x: **You can\'t alert yourself!**',
                                color=discord.Color.red()))

                else:
                    await message.channel.send(
                        embed=discord.Embed(
                            description=':lock: You can only alert the current player every 30 seconds.',
                            color=discord.Color.red()))

                return

            elif color in ('c', 'cards', 'card'):
                m = discord.Embed(title='Your cards:', color=discord.Color.red())

                if not games[str(message.guild.id)]['settings']['Flip']:
                    image = Image.new('RGBA', (
                        len(games[str(message.guild.id)]['players'][str(message.author.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))
                else:
                    image = Image.new('RGBA', (
                        len(games[str(message.guild.id)]['players'][str(message.author.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123 * 2)),
                                      (255, 0, 0, 0))

                for i in range(len(games[str(message.guild.id)]['players'][str(message.author.id)]['cards'])):
                    if not games[str(message.guild.id)]['settings']['Flip']:
                        card = Image.open(
                            'images/' + games[str(message.guild.id)]['players'][str(message.author.id)]['cards'][
                                i] + '.png')
                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)
                        image.paste(refined, (i * refined.size[0], 0))
                    else:
                        card = Image.open(
                            'images/' + games[str(message.guild.id)]['players'][str(message.author.id)]['cards'][i][
                                0] + '.png')
                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)
                        image.paste(refined, (i * refined.size[0], 0))

                        card = Image.open(
                            'images/' + games[str(message.guild.id)]['players'][str(message.author.id)]['cards'][
                                i][1] + '.png')
                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)),
                                              Image.ANTIALIAS)
                        image.paste(refined, (i * refined.size[0], refined.size[1]))

                with BytesIO() as image_binary:
                    image.save(image_binary, format='PNG', quality=100)
                    image_binary.seek(0)
                    file = discord.File(fp=image_binary, filename='image.png')

                m.set_image(url='attachment://image.png')

                await message.channel.send(file=file, embed=m)

                return

            else:
                return

            if games[str(message.guild.id)]['player'] == message.author.id and str(
                    message.guild.id) not in ending:
                overwrite = message.channel.overwrites_for(message.author)
                overwrite.send_messages = False
                overwrite.read_messages = True
                try:
                    await message.channel.set_permissions(message.author, overwrite=overwrite)
                except discord.NotFound:
                    pass

                if not games[str(message.guild.id)]['settings']['Flip']:
                    current_color = search(r'red|blue|green|yellow',
                                           games[str(message.guild.id)]['current']).group(0)
                    current_value = search(r'\+[42]|wild|skip|reverse|\d',
                                           games[str(message.guild.id)]['current']).group(0)

                elif not games[str(message.guild.id)]['dark']:
                    current_color = search(r'red|blue|green|yellow',
                                           games[str(message.guild.id)]['current'][0]).group(0)
                    current_value = search(r'\+[21]|wild|skip|reverse|flip|\d',
                                           games[str(message.guild.id)]['current'][0]).group(0)

                else:
                    current_color = search(r'pink|teal|orange|purple',
                                           games[str(message.guild.id)]['current'][1]).group(0)
                    current_value = search(r'\+(5|color)|wild|skip|reverse|flip|\d',
                                           games[str(message.guild.id)]['current'][1]).group(0)

                try:
                    if value in [str(x) for x in range(10)]:
                        if not games[str(message.guild.id)]['settings']['Flip']:
                            if color + value in games[str(message.guild.id)]['players'][str(message.author.id)][
                                'cards']:
                                if (current_color == color or current_value == value) and not (
                                        '+' in current_value and str(message.guild.id) in stack):
                                    await play_card(color + value, message.author, message.guild)

                                    if games[str(message.guild.id)]['settings']['7-0']:
                                        if value == '7':
                                            view = View()
                                            view.add_item(get_hands(message.guild, message.author, n))

                                            await message.channel.send(
                                                embed=discord.Embed(
                                                    description='**Who do you want to switch hands with?**',
                                                    color=discord.Color.red()), view=view)

                                        elif value == '0':
                                            d = deepcopy(games[str(message.guild.id)]['players'])

                                            player_ids = list(games[str(message.guild.id)]['players'].keys())
                                            for i in range(len(player_ids)):
                                                if player_ids[i] != str(client.user.id) and player_ids[
                                                    (i + 1) % len(player_ids)] != str(client.user.id):
                                                    games[str(message.guild.id)]['players'][
                                                        player_ids[(i + 1) % len(player_ids)]][
                                                        'cards'] = d[player_ids[i]]['cards']
                                                elif player_ids[i] == str(client.user.id):
                                                    games[str(message.guild.id)]['players'][
                                                        player_ids[(i + 1) % len(player_ids)]][
                                                        'cards'] = d[player_ids[i]].cards
                                                else:
                                                    games[str(message.guild.id)]['players'][
                                                        player_ids[(i + 1) % len(player_ids)]].cards = \
                                                        d[player_ids[i]]['cards']

                                            if str(message.guild.id) in games:
                                                await asyncio.gather(
                                                    *[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description='**Everyone switched hands!**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                await display_cards(n, message.guild)

                                        else:
                                            if str(message.guild.id) in games:
                                                await display_cards(n, message.guild)

                                    else:
                                        if str(message.guild.id) in games:
                                            await display_cards(n, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You can\'t play a ' + color.capitalize() + value + ' here!**',
                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a ' + color.capitalize() + value + '!**',
                                        color=discord.Color.red()))

                        else:
                            if not games[str(message.guild.id)]['dark']:
                                if color + value in [x[0] for x in
                                                     games[str(message.guild.id)]['players'][str(message.author.id)][
                                                         'cards']]:
                                    if (current_color == color or current_value == value) and not (
                                            '+' in current_value and str(message.guild.id) in stack):
                                        await play_card(
                                            choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[0] == color + value]),
                                            message.author, message.guild)

                                        if games[str(message.guild.id)]['settings']['7-0']:
                                            if value == '7':
                                                view = View()
                                                view.add_item(get_hands(message.guild, message.author, n))

                                                await message.channel.send(embed=discord.Embed(
                                                    description='**Who do you want to switch hands with?**',
                                                    color=discord.Color.red()
                                                ), view=view)

                                            else:
                                                if str(message.guild.id) in games:
                                                    await display_cards(n, message.guild)

                                        else:
                                            if str(message.guild.id) in games:
                                                await display_cards(n, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You can\'t play a ' + color.capitalize() + value + ' here!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + value + '!**',
                                            color=discord.Color.red()))

                            else:
                                if color + value in [x[1] for x in
                                                     games[str(message.guild.id)]['players'][str(message.author.id)][
                                                         'cards']]:
                                    if (current_color == color or current_value == value) and not (
                                            '+' in current_value and str(message.guild.id) in stack):
                                        await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[1] == color + value]),
                                                        message.author, message.guild)

                                        if games[str(message.guild.id)]['settings']['7-0']:
                                            if value == '7':
                                                view = View()
                                                view.add_item(get_hands(message.guild, message.author, n))

                                                await message.channel.send(embed=discord.Embed(
                                                    description='**Who do you want to switch hands with?**',
                                                    color=discord.Color.red()
                                                ), view=view)

                                            else:
                                                if str(message.guild.id) in games:
                                                    await display_cards(n, message.guild)

                                        else:
                                            if str(message.guild.id) in games:
                                                await display_cards(n, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You can\'t play a ' + color.capitalize() + value + ' here!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + value + '!**',
                                            color=discord.Color.red()))

                    elif value in ('reverse', 'r'):
                        if not games[str(message.guild.id)]['settings']['Flip']:
                            if color + 'reverse' in games[str(message.guild.id)]['players'][str(message.author.id)][
                                'cards']:
                                if (current_color == color or current_value == 'reverse') and not (
                                        '+' in current_value and str(message.guild.id) in stack):
                                    await play_card(color + 'reverse', message.author, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You can\'t play a ' + color.capitalize() + 'Reverse here!**',
                                            color=discord.Color.red()))

                                    overwrite.send_messages = True
                                    await message.channel.set_permissions(message.author, overwrite=overwrite)

                                    return

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a ' + color.capitalize() + 'Reverse!**',
                                        color=discord.Color.red()))

                                overwrite.send_messages = True
                                await message.channel.set_permissions(message.author, overwrite=overwrite)

                                return

                        else:
                            if not games[str(message.guild.id)]['dark']:
                                if color + 'reverse' in [x[0] for x in
                                                         games[str(message.guild.id)]['players'][
                                                             str(message.author.id)][
                                                             'cards']]:
                                    if (current_color == color or current_value == 'reverse') and not (
                                            '+' in current_value and str(message.guild.id) in stack):
                                        await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[0] == color + 'reverse']),
                                                        message.author, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You can\'t play a ' + color.capitalize() + 'Reverse here!**',
                                                color=discord.Color.red()))

                                        overwrite.send_messages = True
                                        await message.channel.set_permissions(message.author, overwrite=overwrite)

                                        return

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'Reverse!**',
                                            color=discord.Color.red()))

                                    overwrite.send_messages = True
                                    await message.channel.set_permissions(message.author, overwrite=overwrite)

                                    return

                            else:
                                if color + 'reverse' in [x[1] for x in
                                                         games[str(message.guild.id)]['players'][
                                                             str(message.author.id)][
                                                             'cards']]:
                                    if (current_color == color or current_value == 'reverse') and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[1] == color + 'reverse']),
                                                        message.author, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You can\'t play a ' + color.capitalize() + 'Reverse here!**',
                                                color=discord.Color.red()))

                                        overwrite.send_messages = True
                                        await message.channel.set_permissions(message.author,
                                                                              overwrite=overwrite)

                                        return

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'Reverse!**',
                                            color=discord.Color.red()))

                                    overwrite.send_messages = True
                                    await message.channel.set_permissions(message.author, overwrite=overwrite)

                                    return

                        if str(message.guild.id) in games:
                            d = games[str(message.guild.id)]
                            player_ids = [x for x in d['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in d['players'][x]]

                            if len(player_ids) > 2:
                                player_ids.reverse()

                                ordered_dict = OrderedDict()
                                for x in player_ids:
                                    ordered_dict[x] = d['players'][x]

                                d['players'] = dict(ordered_dict)

                                await asyncio.gather(*[asyncio.create_task(x.send(
                                    embed=discord.Embed(description='**The player order is reversed.**',
                                                        color=discord.Color.red()))) for x in
                                    message.channel.category.text_channels])

                                p = [x for x in d['players'] if not str.isdigit(x) or str.isdigit(x) and 'left' not in d['players'][x]]
                                m = None
                                temp = iter(p)
                                for key in temp:
                                    if key == str(message.author.id):
                                        m = next(temp, next(iter(p)))
                                        if str.isdigit(m):
                                            m = message.guild.get_member(int(m))
                                        break

                                await display_cards(m, message.guild)

                            else:
                                m = next(temp, next(iter(p)))
                                if str.isdigit(m):
                                    m = message.guild.get_member(int(m))
                                if m == n:
                                    iterable = iter(p)
                                    next(iterable)
                                    m = next(temp, next(iterable))
                                    if str.isdigit(m):
                                        m = message.guild.get_member(int(m))

                                if isinstance(n, Member):
                                    await asyncio.gather(*[asyncio.create_task(x.send(
                                        embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                            color=discord.Color.red()))) for x in
                                        message.channel.category.text_channels])
                                else:
                                    await asyncio.gather(*[asyncio.create_task(x.send(
                                        embed=discord.Embed(description='**' + n + ' is skipped.**',
                                                            color=discord.Color.red()))) for x in
                                        message.channel.category.text_channels])

                                await display_cards(m, message.guild)

                    elif value in ('skip', 's'):
                        if not games[str(message.guild.id)]['settings']['Flip']:
                            if color + 'skip' in games[str(message.guild.id)]['players'][str(message.author.id)][
                                'cards']:
                                if (current_color == color or current_value == 'skip') and not (
                                        '+' in current_value and str(message.guild.id) in stack):
                                    await play_card(color + 'skip', message.author, message.guild)

                                    if str(message.guild.id) in games:
                                        m = next(temp, next(iter(p)))
                                        if str.isdigit(m):
                                            m = message.guild.get_member(int(m))
                                        if m == n:
                                            iterable = iter(p)
                                            next(iterable)
                                            m = next(temp, next(iterable))
                                            if str.isdigit(m):
                                                m = message.guild.get_member(int(m))

                                        if isinstance(n, Member):
                                            await asyncio.gather(*[asyncio.create_task(x.send(
                                                embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                                    color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])
                                        else:
                                            await asyncio.gather(*[asyncio.create_task(x.send(
                                                embed=discord.Embed(description='**' + n + ' is skipped.**',
                                                                    color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])

                                        await display_cards(m, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You cannot play a ' + color.capitalize() + 'Skip here!**',
                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a ' + color.capitalize() + 'Skip!**',
                                        color=discord.Color.red()))

                        else:
                            if not games[str(message.guild.id)]['dark']:
                                if color + 'skip' in [x[0] for x in
                                                      games[str(message.guild.id)]['players'][str(message.author.id)][
                                                          'cards']]:
                                    if (current_color == color or current_value == 'skip') and not (
                                            '+' in current_value and str(message.guild.id) in stack):
                                        await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[0] == color + 'skip']),
                                                        message.author, message.guild)

                                        if str(message.guild.id) in games:
                                            m = next(temp, next(iter(p)))
                                            if str.isdigit(m):
                                                m = message.guild.get_member(int(m))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = next(temp, next(iterable))
                                                if str.isdigit(m):
                                                    m = message.guild.get_member(int(m))

                                            if isinstance(n, Member):
                                                await asyncio.gather(*[asyncio.create_task(x.send(
                                                    embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                                        color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])
                                            else:
                                                await asyncio.gather(*[asyncio.create_task(x.send(
                                                    embed=discord.Embed(description='**' + n + ' is skipped.**',
                                                                        color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])

                                            await display_cards(m, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You cannot play a ' + color.capitalize() + 'Skip here!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'Skip!**',
                                            color=discord.Color.red()))

                            else:
                                if color + 'skip' in [x[1] for x in
                                                      games[str(message.guild.id)]['players'][str(message.author.id)][
                                                          'cards']]:
                                    if (current_color == color or current_value == 'skip') and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[1] == color + 'skip']),
                                                        message.author, message.guild)

                                        if str(message.guild.id) in games:
                                            await asyncio.gather(*[asyncio.create_task(x.send(
                                                embed=discord.Embed(description='**Everyone is skipped!**',
                                                                    color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])

                                            await display_cards(message.author, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You cannot play a ' + color.capitalize() + 'Skip here!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'Skip!**',
                                            color=discord.Color.red()))

                    elif value in ('w', 'wild'):
                        if not games[str(message.guild.id)]['settings']['Flip']:
                            if 'wild' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                if not ('+' in current_value and str(message.guild.id) in stack):
                                    await play_card(color + 'wild', message.author, message.guild)

                                    if str(message.guild.id) in games:
                                        await display_cards(n, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(description=':x: **You can\'t play a Wild here!**',
                                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(description=':x: **You don\'t have a Wild!**',
                                                        color=discord.Color.red()))

                        else:
                            if not games[str(message.guild.id)]['dark']:
                                if any(x[0] == 'wild' for x in
                                       games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                    if color in ('red', 'blue', 'green', 'yellow'):
                                        if not ('+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(
                                                (color + 'wild',
                                                 choice([x for x in games[str(message.guild.id)]['players'][
                                                     str(message.author.id)]['cards'] if x[0] == 'wild'])[1]),
                                                message.author, message.guild)

                                            if str(message.guild.id) in games:
                                                await display_cards(n, message.guild)

                                        else:
                                            await message.channel.send(
                                                embed=discord.Embed(
                                                    description=':x: **You can\'t play a Wild here!**',
                                                    color=discord.Color.red()))

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(description=':x: **Invalid color!**',
                                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(description=':x: **You don\'t have a Wild!**',
                                                            color=discord.Color.red()))

                            else:
                                if any(x[1] == 'darkwild' for x in
                                       games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                    if color in ('pink', 'teal', 'orange', 'purple'):
                                        if not ('+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card((
                                                choice([x for x in games[str(message.guild.id)]['players'][
                                                    str(message.author.id)]['cards'] if x[1] == 'darkwild'])[
                                                    0], color + 'wild'),
                                                message.author, message.guild)

                                            if str(message.guild.id) in games:
                                                await display_cards(n, message.guild)

                                        else:
                                            await message.channel.send(
                                                embed=discord.Embed(
                                                    description=':x: **You can\'t play a Wild here!**',
                                                    color=discord.Color.red()))

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(description=':x: **Invalid color!**',
                                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(description=':x: **You don\'t have a Wild!**',
                                                            color=discord.Color.red()))

                    elif search(r'[+d](raw)* *4', value) and not games[str(message.guild.id)]['settings']['Flip']:
                        if '+4' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                            await play_card(color + '+4', message.author, message.guild)

                            if str(message.guild.id) in games:
                                if str(message.guild.id) not in stack:
                                    stack[str(message.guild.id)] = 4
                                else:
                                    stack[str(message.guild.id)] += 4

                                if isinstance(n, Member) and games[str(message.guild.id)]['settings']['StackCards'] and any(
                                        '+4' in card for card in
                                        games[str(message.guild.id)]['players'][str(n.id)]['cards']):
                                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                            stack[str(message.guild.id)]) + ' cards.**',
                                        color=discord.Color.red()))) for x in
                                        message.channel.category.text_channels])

                                    await display_cards(n, message.guild)

                                elif isinstance(n, str) and games[str(message.guild.id)]['settings']['StackCards'] and any(
                                            '+4' in card for card in
                                            games[str(message.guild.id)]['players'][n].cards):
                                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                            description=f'**{n} can choose to stack cards or draw ' + str(
                                                stack[str(message.guild.id)]) + ' cards.**',
                                            color=discord.Color.red()))) for x in
                                            message.channel.category.text_channels])

                                        await display_cards(n, message.guild)

                                else:
                                    await draw(n, message.guild, stack[str(message.guild.id)])

                                    del stack[str(message.guild.id)]

                                    m = next(temp, next(iter(p)))
                                    if str.isdigit(m):
                                        m = message.guild.get_member(int(m))
                                    if m == n:
                                        iterable = iter(p)
                                        next(iterable)
                                        m = next(temp, next(iterable))
                                        if str.isdigit(m):
                                            m = message.guild.get_member(int(m))

                                    await display_cards(m, message.guild)

                        else:
                            await message.channel.send(
                                embed=discord.Embed(description=':x: **You don\'t have a WildDraw4!**',
                                                    color=discord.Color.red()))

                    elif search(r'[+d](raw)* *2', value):
                        if not games[str(message.guild.id)]['settings']['Flip']:
                            if color + '+2' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                if (current_color == color or current_value == '+2') and not (
                                        current_value == '+4' and str(message.guild.id) in stack):
                                    await play_card(color + '+2', message.author, message.guild)

                                    if str(message.guild.id) in games:
                                        if str(message.guild.id) not in stack:
                                            stack[str(message.guild.id)] = 2
                                        else:
                                            stack[str(message.guild.id)] += 2

                                        if isinstance(n, Member) and games[str(message.guild.id)]['settings']['StackCards'] and (
                                                any('+2' in card for card in
                                                    games[str(message.guild.id)]['players'][str(n.id)][
                                                        'cards']) or any(
                                            '+4' in card for card in
                                            games[str(message.guild.id)]['players'][str(n.id)]['cards'])):
                                            await asyncio.gather(
                                                *[asyncio.create_task(x.send(embed=discord.Embed(
                                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                        stack[str(message.guild.id)]) + ' cards.**',
                                                    color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])

                                            await display_cards(n, message.guild)

                                        elif isinstance(n, str) and games[str(message.guild.id)]['settings']['StackCards'] and (
                                                    any('+2' in card for card in
                                                        games[str(message.guild.id)]['players'][n].cards) or any(
                                                '+4' in card for card in
                                                games[str(message.guild.id)]['players'][n].cards)):
                                                await asyncio.gather(
                                                    *[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description=f'**{n} can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                await display_cards(n, message.guild)

                                        else:
                                            await draw(n, message.guild, stack[str(message.guild.id)])

                                            del stack[str(message.guild.id)]

                                            m = next(temp, next(iter(p)))
                                            if str.isdigit(m):
                                                m = message.guild.get_member(int(m))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = next(temp, next(iterable))
                                                if str.isdigit(m):
                                                    m = message.guild.get_member(int(m))

                                            await display_cards(m, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You can\'t play a ' + color.capitalize() + '+2 here!**',
                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a ' + color.capitalize() + '+2!**',
                                        color=discord.Color.red()))

                        else:
                            if not games[str(message.guild.id)]['dark']:
                                if any(x[0] == '+2' for x in
                                       games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                    if color in ('red', 'blue', 'green', 'yellow'):
                                        await play_card(
                                            (color + '+2', choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[0] == '+2'])[
                                                1]), message.author, message.guild)

                                        if str(message.guild.id) in games:
                                            if str(message.guild.id) not in stack:
                                                stack[str(message.guild.id)] = 2
                                            else:
                                                stack[str(message.guild.id)] += 2

                                            if isinstance(n, Member) and games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                    card[0] == '+2' for card in
                                                    games[str(message.guild.id)]['players'][str(n.id)][
                                                        'cards']):
                                                await asyncio.gather(
                                                    *[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                await display_cards(n, message.guild)

                                            elif isinstance(n, str) and games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                        card[0] == '+2' for card in
                                                        games[str(message.guild.id)]['players'][n].cards):
                                                await asyncio.gather(
                                                    *[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description='**' + n + ' can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                await display_cards(n, message.guild)

                                            else:
                                                await draw(n, message.guild, stack[str(message.guild.id)])

                                                del stack[str(message.guild.id)]

                                                m = next(temp, next(iter(p)))
                                                if str.isdigit(m):
                                                    m = message.guild.get_member(int(m))
                                                if m == n:
                                                    iterable = iter(p)
                                                    next(iterable)
                                                    m = next(temp, next(iterable))
                                                    if str.isdigit(m):
                                                        m = message.guild.get_member(int(m))

                                                await display_cards(m, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **Invalid color!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + '+2!**',
                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You can\'t play a +2 here!**',
                                        color=discord.Color.red()))

                    elif search(r'[+d](raw)* *1', value):
                        if games[str(message.guild.id)]['settings']['Flip'] and not games[str(message.guild.id)][
                            'dark']:
                            if any(color + '+1' in card[0] for card in
                                   games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                if (current_color == color or current_value == '+1') and not (
                                        current_value == '+2' and str(message.guild.id) in stack):
                                    await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                        str(message.author.id)]['cards'] if x[0] == color + '+1']), message.author,
                                                    message.guild)

                                    if str(message.guild.id) in games:
                                        if str(message.guild.id) not in stack:
                                            stack[str(message.guild.id)] = 1
                                        else:
                                            stack[str(message.guild.id)] += 1

                                        if isinstance(n, Member) and games[str(message.guild.id)]['settings']['StackCards'] and (
                                                any('+1' in card[0] for card in
                                                    games[str(message.guild.id)]['players'][str(n.id)][
                                                        'cards']) or any(
                                            card[0] == '+2' for card in
                                            games[str(message.guild.id)]['players'][str(n.id)]['cards'])):
                                            await asyncio.gather(
                                                *[asyncio.create_task(x.send(embed=discord.Embed(
                                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                        stack[str(message.guild.id)]) + ' cards.**',
                                                    color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])

                                            await display_cards(n, message.guild)

                                        elif isinstance(n, str) and games[str(message.guild.id)]['settings']['StackCards'] and (
                                                    any('+1' in card[0] for card in
                                                        games[str(message.guild.id)]['players'][n].cards) or any(
                                                card[0] == '+2' for card in
                                                games[str(message.guild.id)]['players'][n].cards)):
                                                await asyncio.gather(
                                                    *[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description=f'**{n} can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                await display_cards(n, message.guild)

                                        else:
                                            await draw(n, message.guild, stack[str(message.guild.id)])

                                            del stack[str(message.guild.id)]

                                            m = next(temp, next(iter(p)))
                                            if str.isdigit(m):
                                                m = message.guild.get_member(int(m))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = next(temp, next(iterable))
                                                if str.isdigit(m):
                                                    m = message.guild.get_member(int(m))

                                            await display_cards(m, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You can\'t play a ' + color.capitalize() + '+1 here!**',
                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a ' + color.capitalize() + '+1!**',
                                        color=discord.Color.red()))

                        else:
                            await message.channel.send(
                                embed=discord.Embed(
                                    description=':x: **You can\'t play a +1 here!**',
                                    color=discord.Color.red()))

                    elif search(r'[+d](raw)* *5', value):
                        if games[str(message.guild.id)]['settings']['Flip'] and games[str(message.guild.id)][
                            'dark']:
                            if any(color + '+5' in card[1] for card in
                                   games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                if current_color == color or current_value == '+5':
                                    await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                        str(message.author.id)]['cards'] if x[1] == color + '+5']), message.author,
                                                    message.guild)

                                    if str(message.guild.id) in games:
                                        if str(message.guild.id) not in stack:
                                            stack[str(message.guild.id)] = 5
                                        else:
                                            stack[str(message.guild.id)] += 5

                                        if isinstance(n, Member) and games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                '+5' in card[1] for card in
                                                games[str(message.guild.id)]['players'][str(n.id)]['cards']):
                                            await asyncio.gather(
                                                *[asyncio.create_task(x.send(embed=discord.Embed(
                                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                        stack[str(message.guild.id)]) + ' cards.**',
                                                    color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])

                                            await display_cards(n, message.guild)

                                        elif isinstance(n, str) and games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                    '+5' in card[1] for card in
                                                    games[str(message.guild.id)]['players'][n].cards):
                                                await asyncio.gather(
                                                    *[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description=f'**{n} can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                await display_cards(n, message.guild)

                                        else:
                                            await draw(n, message.guild, stack[str(message.guild.id)])

                                            del stack[str(message.guild.id)]

                                            m = next(temp, next(iter(p)))
                                            if str.isdigit(m):
                                                m = message.guild.get_member(int(m))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = next(temp, next(iterable))
                                                if str.isdigit(m):
                                                    m = message.guild.get_member(int(m))

                                            await display_cards(m, message.guild)

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You can\'t play a ' + color.capitalize() + '+5 here!**',
                                            color=discord.Color.red()))

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a ' + color.capitalize() + '+5!**',
                                        color=discord.Color.red()))

                        else:
                            await message.channel.send(
                                embed=discord.Embed(
                                    description=':x: **You can\'t play a +5 here!**',
                                    color=discord.Color.red()))

                    elif search(r'[+d](raw)* *c(olor)*', value):
                        if games[str(message.guild.id)]['settings']['Flip'] and games[str(message.guild.id)][
                            'dark'] and not ('+' in current_value and str(message.guild.id) in stack):
                            if any('+color' in x[1] for x in
                                   games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                await play_card((choice([x for x in games[str(message.guild.id)]['players'][
                                    str(message.author.id)]['cards'] if x[1] == '+color'])[
                                                     0], color + '+color'), message.author, message.guild)

                                if str(message.guild.id) in games:
                                    await draw(n, message.guild, 1, False, True)

                                    m = next(temp, next(iter(p)))
                                    if str.isdigit(m):
                                        m = message.guild.get_member(int(m))
                                    if m == n:
                                        iterable = iter(p)
                                        next(iterable)
                                        m = next(temp, next(iterable))
                                        if str.isdigit(m):
                                            m = message.guild.get_member(int(m))
                                    await display_cards(m, message.guild)

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(
                                        description=':x: **You don\'t have a +color!**',
                                        color=discord.Color.red()))

                        else:
                            await message.channel.send(
                                embed=discord.Embed(
                                    description=':x: **You can\'t play a +color here!**',
                                    color=discord.Color.red()))

                    elif value in ('f', 'flip'):
                        if games[str(message.guild.id)]['settings']['Flip'] and not (
                                '+' in current_value and str(message.guild.id) in stack):
                            if not games[str(message.guild.id)]['dark']:
                                if color + 'flip' in [x[0] for x in
                                                      games[str(message.guild.id)]['players'][str(message.author.id)][
                                                          'cards']]:
                                    if color == current_color or current_value == 'flip':
                                        c = choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[0] == color + 'flip'])

                                        await play_card(c, message.author, message.guild)

                                        if str(message.guild.id) in games:
                                            games[str(message.guild.id)]['dark'] = not games[str(message.guild.id)][
                                                'dark']
                                            games[str(message.guild.id)]['current'] = games[str(message.guild.id)][
                                                'current_opposite']
                                            games[str(message.guild.id)]['current_opposite'] = c

                                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                description='**Everything is flipped!**',
                                                color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])

                                            await display_cards(n, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You can\'t play a ' + color.capitalize() + 'flip here!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'flip here!**',
                                            color=discord.Color.red()))

                            else:
                                if color + 'flip' in [x[1] for x in
                                                      games[str(message.guild.id)]['players'][str(message.author.id)][
                                                          'cards']]:
                                    if color == current_color or current_value == 'flip':
                                        c = choice([x for x in games[str(message.guild.id)]['players'][
                                            str(message.author.id)]['cards'] if x[1] == color + 'flip'])

                                        await play_card(c, message.author, message.guild)

                                        if str(message.guild.id) in games:
                                            games[str(message.guild.id)]['dark'] = not games[str(message.guild.id)][
                                                'dark']
                                            games[str(message.guild.id)]['current'] = games[str(message.guild.id)][
                                                'current_opposite']
                                            games[str(message.guild.id)]['current_opposite'] = c

                                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                description='**Everything is flipped!**',
                                                color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])

                                            await display_cards(n, message.guild)

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You can\'t play a ' + color.capitalize() + 'flip here!**',
                                                color=discord.Color.red()))

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'flip here!**',
                                            color=discord.Color.red()))

                        else:
                            await message.channel.send(
                                embed=discord.Embed(
                                    description=':x: **You aren\'t playing UNO Flip!**',
                                    color=discord.Color.red()))

                except IndexError:
                    pass
                except TypeError:
                    pass

                overwrite.send_messages = True
                try:
                    await message.channel.set_permissions(message.author, overwrite=overwrite)
                except discord.NotFound:
                    pass

            else:

                await message.channel.send(
                    embed=discord.Embed(description=':x: **It\'s not your turn yet!**', color=discord.Color.red()))

        except KeyError as e:
            if str(message.guild.id) not in games:
                pass
            else:
                raise e

    else:
        await client.process_commands(message)


# Commands
@client.slash_command(name='u-help',
                      description='Shows the command usage, an in-depth guide on using UNOBot and a link to the rules of UNO.')
@has_permissions(read_messages=True)
async def help(ctx):
    UNOBotPNG = discord.File('images/UNOBot.png', filename='bot.png')

    message = discord.Embed(title='UNO Bot Help', color=discord.Color.red())
    message.set_thumbnail(url='attachment://bot.png')
    message.add_field(name=':exclamation: Command List', value='`/u.commands`\nGet a list of commands.\n' + chr(173),
                      inline=False)
    message.add_field(name=':closed_book: Guide',
                      value='`/u.guide`\nRead an in-depth guide on using UNO Bot.\n' + chr(173), inline=False)
    message.add_field(name=':scroll: UNO Rules', value='`/u.rules`\nRead the rules of the original UNO.', inline=False)

    await ctx.respond(file=UNOBotPNG, embed=message)


@client.slash_command(name='u-cmds', description='Shows you how to use UNOBot\'s commands.')
@has_permissions(read_messages=True)
async def commands(ctx, command: Option(str, 'The command you want to learn', required=False, default='')):
    if not command:
        UNOBotPNG = discord.File('images/UNOBot.png', filename='bot.png')
        message = discord.Embed(title='UNO Bot Commands', color=discord.Color.red())
        message.set_thumbnail(url='attachment://bot.png')
        message.add_field(name=prefix + 'sg', value='Starts a game of UNO.\n' + chr(173))
        message.add_field(name=prefix + 'eg', value='Ends the ongoing UNO game.\n' + chr(173))
        message.add_field(name=prefix + 'leave', value='Lets you leave the UNO game.\n' + chr(173))
        message.add_field(name=prefix + 'kick', value='Kicks a player from an UNO game.\n' + chr(173))
        message.add_field(name=prefix + 'spectate', value='Spectate games of UNO.\n' + chr(173))
        message.add_field(name=prefix + 'stats',
                          value='Gives you a user\'s stats from this Discord server.\n' + chr(173))
        message.add_field(name=prefix + 'gstats', value='Gives you a user\'s stats from all servers.\n' + chr(173))
        message.add_field(name=prefix + 'lb',
                          value='Gives you a leaderboard only from this Discord server.\n' + chr(173))
        message.add_field(name=prefix + 'glb',
                          value='Gives you a leaderboard for all servers.\n' + chr(173))
        message.add_field(name=prefix + 'settings',
                          value='Adjusts how UNOBot works for the entire server.\n' + chr(173))
        message.set_footer(text='• Use ' + prefix + 'commands <command> to get more help on that command.')

        await ctx.respond(file=UNOBotPNG, embed=message)

    else:
        if command == 'sg':
            message = discord.Embed(title=prefix + 'sg', color=discord.Color.red())
            message.add_field(name='Description:',
                              value='Start a game of UNO. Play with those mentioned in the message. Players can play their cards in their auto-created UNO channels.',
                              inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'sg (list of @user-mentions) (game settings)`',
                              inline=False)
            message.add_field(name=chr(173),
                              value='**Note:** You must have at least 2 players to start a game, bots do not count.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Tips:',
                              value='• You can change the default game settings using `' + prefix + 'settings dgs`.',
                              inline=False)
            message.add_field(name='Examples:',
                              value='• `' + prefix + 'sg @VTiS @CoffinMan`\n• `' + prefix + 'sg QuickStart`')

            await ctx.respond(embed=message)

        elif command == 'eg':
            message = discord.Embed(title=prefix + 'eg', color=discord.Color.red())
            message.add_field(name='Description:', value='Ends the ongoing UNO game.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'eg`', inline=False)
            message.add_field(name=chr(173),
                              value='**Note:** Only the game creator, admins, and whitelisted roles from the settings can use this.\n' + chr(
                                  173), inline=False)

            await ctx.respond(embed=message)

        elif command == 'leave':
            message = discord.Embed(title=prefix + 'leave', color=discord.Color.red())
            message.add_field(name='Description:', value='Lets you leave the UNO game.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'leave`', inline=False)

            await ctx.respond(embed=message)

        elif command == 'kick':
            message = discord.Embed(title=prefix + 'kick', color=discord.Color.red())
            message.add_field(name='Description:', value='Kicks a player from an UNO game.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'kick <@user-mention>`', inline=False)
            message.add_field(name=chr(173),
                              value='**Note:** Only the game creator, admins, and whitelisted roles from the settings can use this.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Examples:', value='`' + prefix + 'kick @CoffinMan`')

            await ctx.respond(embed=message)

        elif command == 'spectate':
            message = discord.Embed(title=prefix + 'spectate', color=discord.Color.red())
            message.add_field(name='Description:', value='Spectate games of UNO.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'spectate (on|off)`', inline=False)

            await ctx.respond(embed=message)

        elif command == 'stats':
            message = discord.Embed(title=prefix + 'stats', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a user\'s stats only from this Discord server.',
                              inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'stats (@user-mention)`', inline=False)
            message.add_field(name='Examples:', value='`' + prefix + 'stats @VTiS`')

            await ctx.respond(embed=message)

        elif command == 'gstats':
            message = discord.Embed(title=prefix + 'gstats', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a user\'s stats from all servers.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'gstats (@user-mention)`', inline=False)
            message.add_field(name='Examples:', value='• `' + prefix + 'gstats @VTiS`')

            await ctx.respond(embed=message)

        elif command == 'lb':
            message = discord.Embed(title=prefix + 'lb', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a leaderboard only from this Discord server.',
                              inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'lb`', inline=False)

            await ctx.respond(embed=message)

        elif command == 'glb':
            message = discord.Embed(title=prefix + 'glb', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a leaderboard for all servers.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'glb`', inline=False)

            await ctx.respond(embed=message)

        elif command == 'settings':
            message = discord.Embed(title='UNOBot Settings', color=discord.Color.red(),
                                    description='Adjusts how UNOBot works for the entire server.')
            message.add_field(name=':wrench: Command Customization:', value=prefix + '`settings commands`')
            message.add_field(name=':game_die: Default Game Settings:', value=prefix + '`settings dgs`')
            message.add_field(name=':arrows_counterclockwise: Reset UNOBot:', value=prefix + '`settings reset`',
                              inline=False)

            await ctx.respond(embed=message)


@client.slash_command(name='u-guide', description='Shows you how to use UNOBot in general.')
@has_permissions(read_messages=True)
async def guide(ctx, area: Option(str, 'The area you want a guide on', required=False, default='')):
    if not area:
        UNOBotPNG = discord.File('images/UNOBot.png', filename='bot.png')
        message = discord.Embed(title='UNOBot Guide', color=discord.Color.red())
        message.set_thumbnail(url='attachment://bot.png')
        message.add_field(name=':arrow_forward: Starting a game:',
                          value='`' + prefix + 'guide start`\nHow to start a game of UNO.\n' + chr(173), inline=False)
        message.add_field(name=':round_pushpin: Playing your cards:',
                          value='`' + prefix + 'guide play`\nHow to play your cards in a game of UNO.\n' + chr(173),
                          inline=False)
        message.add_field(name=':speech_balloon: Changing command settings:',
                          value='`' + prefix + 'guide commands`\nChange the server\'s individual command settings.\n' + chr(
                              173), inline=False)
        message.add_field(name=':gear: Changing server settings:',
                          value='`' + prefix + 'guide settings`\nChange the server settings like the prefix and default game settings.\n' + chr(
                              173), inline=False)
        message.add_field(name=':wrench: Changing user options:',
                          value='`' + prefix + 'guide options`\nChange your personal options to tailor your experience.')

        await ctx.respond(file=UNOBotPNG, embed=message)

    else:
        if area == 'start':
            message = discord.Embed(title='How to Start a Game', color=discord.Color.red())
            message.add_field(name='Creating a game:',
                              value='• Start a game using `u!startgame`. (Use `u!startgame help` for more command info.)\n'
                                    '• Add game settings by typing a list of game settings separated by spaces. (A list of game settings can be found with `u!gamesettings list`.)\n'
                                    '• Your command might look like this: `u!startgame StackCards, DisableJoin`.\n'
                                    '• A startgame message will be sent which allows you to join, start, and end the game using the reactions, :hand_splayed:, :arrow_forward:, and :x: respectively.\n'
                                    '• After 30 seconds or a force start, your game will start.\n' + chr(173),
                              inline=False)
            message.add_field(name='Navigating to your channel:',
                              value='• A category named \'uno-category\' will be created after your game begins.\n'
                                    '• A text channel will be created in this category for each player you mentioned.\n'
                                    '• The channel is where the player will play their cards.')

            await ctx.respond(embed=message)

        elif area == 'play':
            message = discord.Embed(title='How to Play Your Cards', color=discord.Color.red())
            message.add_field(name='Reading Embeds:',
                              value='• Open the uno-channel with your username after you have started a game (using `u!startgame`).\n'
                                    '• The pinned message will show some basic commands to play, the options you have enabled, and the game settings that are enabled.\n'
                                    '• A message will be sent, telling you the current player and the current card.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Playing a card:',
                              value='• Use the `u!play` command to play your card. (Use `u!play help` for more command info.)\n'
                                    '• The play command requires a color and a number/type of card.\n'
                                    '• Use `u!cards` for the names of your cards.\n'
                                    '• Your command should look something like this: `u!play red 5`.\n'
                                    '• If you are playing a wild card, make sure to add the color you want. `u!play blue wild`\n' + chr(
                                  173), inline=False)
            message.add_field(name='Drawing a card:',
                              value='• If you don\'t have a card to play, use `u!draw` to draw a card from the deck.\n'
                                    '• After drawing your turn will be over, unless the game setting DrawUntilMatch is on.')

            await ctx.respond(embed=message)

        elif area == 'commands':
            message = discord.Embed(title='How to Change the Server\'s command settings', color=discord.Color.red())
            message.add_field(name='Turn commands on/off:',
                              value='• Use `u!settings commands <command> <on|off>` to toggle the command.\n'
                                    '• Replace "<command>" with the name of the command, excluding the prefix.\n'
                                    '• Replace "<on|off>", with on or off.\n' + chr(173), inline=False)
            message.add_field(name='Change command cooldowns:',
                              value='• Use `u!settings commands <command> cooldown set <time>` to set a cooldown for the command.\n'
                                    '• Replace "<time>" with how long (in seconds) you would like the cooldown to last.'
                                    '• You can view the command\'s current cooldown by using `u!settings commands <command> cooldown view`.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Whitelist or blacklist commands:',
                              value='• Use `u!settings commands <command> <whitelist|blacklist> <on|off>` to turn the whitelist/blacklist on or off.\n'
                                    '• Use `u!settings commands <command> <whitelist|blacklist> <add|remove> <user|role>` to add or remove a user or role to the whitelist/blacklist.\n'
                                    '• A whitelist only allows the people on the list to use the command.\n'
                                    '• A blacklist stops only the people on the list from using the command.\n'
                                    '• Disabling both will allow anyone to use the command.\n' + chr(173), inline=False)
            message.add_field(name='View command settings:',
                              value='• Use `u!settings commands <command> view` to see command info like the state, whitelist, and blacklist.')

            await ctx.respond(embed=message)

        elif area == 'settings':
            message = discord.Embed(title='How to Change the Server\'s Settings', color=discord.Color.red())
            message.add_field(name='Changing the prefix:',
                              value='• Use `u!settings prefix <new prefix>` to change the prefix.'
                                    '• Replace "<new prefix>" with your new prefix.\n' + chr(173), inline=False)
            message.add_field(name='Add or remove default game settings:',
                              value='• Default game settings (DGS) are game settings that will be applied to every game with no game settings automatically.\n'
                                    '• Changing DGS require you to vote, which may take a few minutes to update.\n'
                                    '• Use `u!settings dgs <game setting> <on|off|view>` to turn DGS on or off.\n'
                                    '• Replace "<game setting>" with a game setting from `u!gamesettings list`.\n'
                                    '• Replace "<on|off>" with on or off, depending on if you want to turn the DGS on or off.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Reset UNOBot:', value='• Use `u!settings reset` to reset UnoBot.\n'
                                                          '• This will reset all of the data UnoBot has on your server.\n'
                                                          '• When prompted, respond only with "CONFIRM" in all caps to confirm the reset.')

            await ctx.respond(embed=message)

        elif area == 'options':
            message = discord.Embed(title='How to Change Your User Options', color=discord.Color.red(),
                                    description='User options only affect the user\'s experience, not the entire server\'s.\n' + chr(
                                        173))
            message.add_field(name='Enabling and disabling options:',
                              value='• Use `u!options <option name> <on|off>` to turn an option on or off.\n'
                                    '• Replace "<option name>" with the name of the option, a list can be found using `u!options list`.\n'
                                    '• Replace "<on|off>", with on or off, depending on which you would like.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Navigating to your channel:',
                              value='• Use `u!options view` to view your enabled options.')

            await ctx.respond(embed=message)


@client.slash_command(name='u-rules', description='Gives you a link to the rules of UNO.')
@has_permissions(read_messages=True)
async def rules(ctx):
    await ctx.respond("https://github.com/VTiS15/UNOBot#game-rule")


@client.slash_command(name='u-stats',
                      description='Gives you a user\'s or your (if no user is specified) UNO stats in the current Discord server.')
@has_permissions(read_messages=True)
async def stats(ctx,
                user: Option(discord.User, 'The user whose local stats you wish to see', required=False, default='')):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'stats' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['stats']['Enabled']:
            if not user or user == client.user:
                user = ctx.author

            if ((not commands[str(ctx.guild.id)]['stats']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['stats']['Blacklist'])
                or user.id not in commands[str(ctx.guild.id)]['stats']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['stats']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['stats']['Whitelist'] and user.id in
                         commands[str(ctx.guild.id)]['stats']['Whitelist']) or user == ctx.guild.owner:

                users = json.loads(
                    s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                if users[str(user.id)][str(ctx.guild.id)]['Played'] > 0:
                    message = discord.Embed(title=user.name + '\'s Stats in ' + ctx.guild.name,
                                            color=discord.Color.red())
                    message.set_thumbnail(url=user.display_avatar.url)
                    ranking = rank(user, ctx.guild)
                    message.add_field(name='Rank', value='Rank **' + str(ranking[0]) + '** out of ' + str(ranking[1]),
                                      inline=False)
                    dict = users[str(user.id)][str(ctx.guild.id)]
                    if dict['Score'] == 1:
                        message.add_field(name='Score', value='**1** pt')
                    else:
                        message.add_field(name='Score', value=f'**{dict["Score"]}** pts')
                    message.add_field(name='Win Percentage',
                                      value='Won **' + str(
                                          round(dict['Wins'] / dict['Played'] * 100)) + '%** of games',
                                      inline=False)
                    if dict['Played'] == 1:
                        message.add_field(name='Total Games', value='**1** game played',
                                          inline=False)
                    else:
                        message.add_field(name='Total Games', value='**' + str(dict['Played']) + '** games played',
                                          inline=False)
                    if dict['Wins'] == 1:
                        message.add_field(name='Total Wins', value='**1** game won',
                                          inline=False)
                    else:
                        message.add_field(name='Total Wins', value='**' + str(dict['Wins']) + '** games won',
                                          inline=False)

                    await ctx.respond(embed=message)

                else:
                    await ctx.respond(embed=discord.Embed(color=discord.Color.red(),
                                                          description=':x: **' + user.name + ' has not played UNO yet.**'))

                if commands[str(ctx.guild.id)]['stats']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('stats')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting',
                                   prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'stats' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(commands[str(ctx.guild.id)]['stats']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('stats')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('stats')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['stats']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-gstats',
                      description='Gives you a user\'s or your (if no user is specified) global stats.')
@has_permissions(read_messages=True)
async def globalstats(ctx, user: Option(discord.User, 'The user whose global stats you wish to see', required=False,
                                        default='')):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'globalstats' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['globalstats']['Enabled']:
            if not user or user == client.user:
                user = ctx.author

            if ((not commands[str(ctx.guild.id)]['globalstats']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['globalstats']['Blacklist'])
                or user.id not in commands[str(ctx.guild.id)]['globalstats']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['globalstats']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['globalstats']['Whitelist'] and user.id in
                         commands[str(ctx.guild.id)]['globalstats'][
                             'Whitelist']) or user == ctx.guild.owner:

                users = json.loads(
                    s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                if has_played(user):
                    message = discord.Embed(title=user.name + '\'s Global Stats', color=discord.Color.red())
                    message.set_thumbnail(url=user.display_avatar.url)
                    ranking = rank(user)
                    message.add_field(name='Rank', value='Rank **' + str(ranking[0]) + '** out of ' + str(ranking[1]),
                                      inline=False)

                    p = 0
                    w = 0
                    s = 0
                    for guild in [x for x in client.guilds if x.get_member(user.id)]:
                        p += users[str(user.id)][str(guild.id)]['Played']
                        w += users[str(user.id)][str(guild.id)]['Wins']
                        s += users[str(user.id)][str(guild.id)]['Score']

                    if s == 1:
                        message.add_field(name='Score', value='**1** pt')
                    else:
                        message.add_field(name='Score', value=f'**{s}** pts')
                    message.add_field(name='Win Percentage', value='Won **' + str(round(w / p * 100)) + '%** of games.',
                                      inline=False)
                    if p == 1:
                        message.add_field(name='Total Games', value='**1** game played.', inline=False)
                    else:
                        message.add_field(name='Total Games', value='**' + str(p) + '** games played.', inline=False)
                    if w == 1:
                        message.add_field(name='Total Wins', value='**1** game won.', inline=False)
                    else:
                        message.add_field(name='Total Wins', value='**' + str(w) + '** games won.', inline=False)

                    await ctx.respond(embed=message)

                else:
                    await ctx.respond(embed=discord.Embed(color=discord.Color.red(),
                                                          description=':x: **' + user.name + ' has not played UNO yet.**'))

                if commands[str(ctx.guild.id)]['globalstats']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('globalstats')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting',
                                   prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'globalstats' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(commands[str(ctx.guild.id)]['globalstats']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('globalstats')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('globalstats')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['globalstats']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-lb', description='Presents you with the UNO leaderboard in the current Discord server.')
@has_permissions(read_messages=True)
async def leaderboard(ctx):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'leaderboard' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['leaderboard']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['leaderboard']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['leaderboard']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['leaderboard']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['leaderboard']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['leaderboard']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['leaderboard'][
                             'Whitelist']) or ctx.author == ctx.guild.owner:
                message = discord.Embed(title=ctx.guild.name + '\'s UNO Leaderboard', color=discord.Color.red())

                users = json.loads(
                    s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                leaderboard = rank(None, ctx.guild)

                count = 0
                for i in range(1, len(leaderboard) + 1):
                    for index in list_duplicates_of(leaderboard, i):
                        user = client.get_user(
                            int([x for x in list(users.keys()) if ctx.guild.get_member(int(x))][index]))

                        if users[str(user.id)][str(ctx.guild.id)]['Played'] > 0:
                            message.add_field(name='Rank ' + str(i), value='**' + str(user) + '**\n' + str(
                                users[str(user.id)][str(ctx.guild.id)]['Score']) + ' pts', inline=False)

                            count += 1

                        if count >= 5:
                            break

                    if count >= 5:
                        break

                if ctx.guild.icon:
                    message.set_thumbnail(url=ctx.guild.icon.url)

                if count > 0:
                    message.set_footer(text='Use "' + prefix + 'stats" to check your local rank.')
                    await ctx.respond(embed=message)
                else:
                    message = discord.Embed(color=discord.Color.red(),
                                            description=':x: **No one has played UNO in this server yet!**')
                    await ctx.respond(embed=message)

                if commands[str(ctx.guild.id)]['leaderboard']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('leaderboard')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] == prefix + 'settings' \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'leaderboard' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(commands[str(ctx.guild.id)]['leaderboard']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('leaderboard')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('leaderboard')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['leaderboard']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-glb', description='Presents you with the global UNO leaderboard.')
@has_permissions(read_messages=True)
async def globalleaderboard(ctx):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'globalleaderboard' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['globalleaderboard']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['globalleaderboard']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['globalleaderboard']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['globalleaderboard']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['globalleaderboard']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['globalleaderboard']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['globalleaderboard'][
                             'Whitelist']) or ctx.author == ctx.guild.owner:
                users = json.loads(
                    s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                message = discord.Embed(title='Global UNO Leaderboard', color=discord.Color.red())

                leaderboard = rank()
                count = 0

                for i in range(1, len(leaderboard) + 1):
                    for index in list_duplicates_of(leaderboard, i):
                        user = client.get_user(int(list(users.keys())[index]))
                        p = 0

                        if not user:
                            continue

                        for guild in client.guilds:
                            if guild.get_member(user.id):
                                p += users[str(user.id)][str(guild.id)]['Played']

                        if p > 0:
                            s = 0
                            for g in [x for x in client.guilds if x.get_member(user.id)]:
                                s += users[str(user.id)][str(g.id)]['Score']

                            message.add_field(name='Rank ' + str(i),
                                              value='**' + str(user) + '**\n' + str(s) + ' pts', inline=False)

                            count += 1

                        if count >= 5:
                            break

                    if count >= 5:
                        break

                if count > 0:
                    message.set_footer(text='Use "' + prefix + 'gstats" to check your global rank.')
                    await ctx.respond(embed=message)
                else:
                    message = discord.Embed(color=discord.Color.red(), description=':x: **No one has played UNO yet!**')
                    await ctx.respond(embed=message)

                if commands[str(ctx.guild.id)]['globalleaderboard']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('globalleaderboard')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting',
                                   prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'globalleaderboard' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(
                                                      commands[str(ctx.guild.id)]['globalleaderboard']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('globalleaderboard')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('globalleaderboard')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**',
                                    color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['globalleaderboard']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-settings', description='Allows you to change the settings of UNOBot.')
@has_permissions(read_messages=True)
async def settings(ctx, setting: Option(str, 'The setting you wish to change'), *,
                   args: Option(str, 'some arguments', required=False, default='')):
    if not setting:
        message = discord.Embed(title='UNOBot Settings', color=discord.Color.red(),
                                description='Adjusts how UNOBot works for the entire server.')
        message.add_field(name=':wrench: Command Customization:', value=prefix + '`settings commands`')
        message.add_field(name=':game_die: Default Game Settings:', value=prefix + '`settings dgs`')
        message.add_field(name=':arrows_counterclockwise: Reset UNOBot:', value=prefix + '`settings reset`',
                          inline=False)
        message.add_field(name='Aliases: ', value='set, sett, stngs, setting, stng')

        await ctx.respond(embed=message)

        return

    commands_file = s3_resource.Object('unobot-bucket', 'commands.json')
    commands = json.loads(commands_file.get()['Body'].read().decode('utf-8'))

    if 'settings' not in cooldowns[str(ctx.guild.id)]:
        if ((not commands[str(ctx.guild.id)]['settings']['BlacklistEnabled'] or not
        commands[str(ctx.guild.id)]['settings']['Blacklist'])
            or ctx.author.id not in commands[str(ctx.guild.id)]['settings']['Blacklist']) \
                and (not commands[str(ctx.guild.id)]['settings']['WhitelistEnabled'] or
                     commands[str(ctx.guild.id)]['settings']['Whitelist'] and ctx.author.id in
                     commands[str(ctx.guild.id)]['settings']['Whitelist']) or ctx.author == ctx.guild.owner:

            if setting == 'commands':
                if not args:
                    message = discord.Embed(title=prefix + 'settings commands', color=discord.Color.red())
                    message.add_field(name=':level_slider: Toggle Command',
                                      value='Turns a specific command on or off.\n\n`' + prefix + 'settings commands <command> <on|off>`\n' + chr(
                                          173), inline=False)
                    message.add_field(name=':stopwatch: Set Cooldown',
                                      value='Sets a cooldown for using a specific command.\n\n`' + prefix + 'settings commands <command> cooldown <set|view> (time in seconds)`\n' + chr(
                                          173), inline=False)
                    message.add_field(name=':clipboard: Whitelist or Blacklist',
                                      value='Whitelist or blacklist certain roles of users from using a command. Also toggles between whitelist of blacklist modes.\n\n'
                                            '`' + prefix + 'settings commands <command> <whitelist|blacklist> <add|remove|enable|disable|view> (user|role)`\n' + chr(
                                          173), inline=False)
                    message.add_field(name=':mag: View Command Info',
                                      value='Gives you info on a specific command\'s settings.\n\n'
                                            '`' + prefix + 'settings commands <command> view`')
                    message.set_footer(text='You can get a list of commands using "u!commands"')

                    await ctx.respond(embed=message)

                elif len(args.split()) == 1:
                    if args in cmds:
                        await cmd_info(ctx, args)
                    else:
                        await ctx.respond(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings help`',
                            color=discord.Color.red()))

                elif len(args.split()) == 2:
                    s = args.split()[0]
                    b = args.split()[1]

                    if s in cmds:
                        if b == 'on':
                            commands[str(ctx.guild.id)][s]['Enabled'] = True
                            commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                        elif b == 'off':
                            commands[str(ctx.guild.id)][s]['Enabled'] = False
                            commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                        elif b == 'view':
                            if commands[str(ctx.guild.id)][s]['Enabled']:
                                message = discord.Embed(title=s.capitalize() + ' Command Settings',
                                                        description='Enabled :white_check_mark:',
                                                        color=discord.Color.red())
                            else:
                                message = discord.Embed(title=s.capitalize() + ' Command Settings',
                                                        description='Disabled :x:')

                            message.add_field(name='Cooldown',
                                              value=str(commands[str(ctx.guild.id)][s]['Cooldown']) + ' seconds',
                                              inline=False)

                            lst = []
                            if commands[str(ctx.guild.id)][s]['Whitelist']:
                                for item in commands[str(ctx.guild.id)][s]['Whitelist']:
                                    if not ctx.guild.get_role(int(item)):
                                        lst.append(str(ctx.guild.get_member(item)))
                                    else:
                                        lst.append(str(ctx.guild.get_role(item)))

                                if commands[str(ctx.guild.id)][s]['WhitelistEnabled']:
                                    message.add_field(name='Whitelist',
                                                      value='Enabled :white_check_mark:\n\n' + '\n'.join(lst),
                                                      inline=False)

                                else:
                                    message.add_field(name='Whitelist', value='Disabled :x:\n\n' + '\n'.join(lst),
                                                      inline=False)

                            else:
                                if commands[str(ctx.guild.id)][s]['WhitelistEnabled']:
                                    message.add_field(name='Whitelist', value='Enabled :white_check_mark:\n\nNone',
                                                      inline=False)
                                else:
                                    message.add_field(name='Whitelist', value='Disabled :x:\n\nNone', inline=False)

                            lst = []
                            if commands[str(ctx.guild.id)][s]['Blacklist']:
                                for item in commands[str(ctx.guild.id)][s]['Blacklist']:
                                    if not ctx.guild.get_role(int(item)):
                                        lst.append(str(ctx.guild.get_member(int(item))))
                                    else:
                                        lst.append(str(ctx.guild.get_role(int(item))))

                                if commands[str(ctx.guild.id)][s]['BlacklistEnabled']:
                                    message.add_field(name='Blacklist',
                                                      value='Enabled :white_check_mark:\n\n' + '\n'.join(lst),
                                                      inline=False)

                                else:
                                    message.add_field(name='Blacklist', value='Disabled :x:\n\n' + '\n'.join(lst),
                                                      inline=False)

                            else:
                                if commands[str(ctx.guild.id)][s]['BlacklistEnabled']:
                                    message.add_field(name='Blacklist', value='Enabled :white_check_mark:\n\nNone',
                                                      inline=False)
                                else:
                                    message.add_field(name='Blacklist', value='Disabled :x:\n\nNone', inline=False)

                            await ctx.respond(embed=message)

                        else:
                            await ctx.respond(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.respond(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

                elif len(args.split()) == 3:
                    s = args.split()[0].lower()
                    x = args.split()[1].lower()
                    y = args.split()[2].lower()

                    if s in cmds:
                        if x == 'cooldown':
                            if y == 'view':
                                await ctx.respond(
                                    embed=discord.Embed(description='The **' + s + '** command has a cooldown of **'
                                                                    + str(
                                        commands[str(ctx.guild.id)][s]['Cooldown']) + ' seconds**.',
                                                        color=discord.Color.red()))
                            else:
                                await ctx.respond(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings help`',
                                    color=discord.Color.red()))

                        elif x == 'whitelist' or x == 'blacklist':
                            if y == 'enable':
                                commands[str(ctx.guild.id)][s][x.capitalize() + 'Enabled'] = True
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.respond(embed=discord.Embed(
                                    description=':thumbsup: **The settings have been updated.**',
                                    color=discord.Color.red()))

                            elif y == 'disable':
                                commands[str(ctx.guild.id)][s][x.capitalize() + 'Enabled'] = False
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.respond(embed=discord.Embed(
                                    description=':thumbsup: **The settings have been updated.**',
                                    color=discord.Color.red()))

                            elif y == 'view':
                                if commands[str(ctx.guild.id)][s][x.capitalize() + 'Enabled']:
                                    message = discord.Embed(title=s.capitalize() + ' ' + x.capitalize(),
                                                            description='Enabled :white_check_mark:',
                                                            color=discord.Color.red())
                                else:
                                    message = discord.Embed(title=s.capitalize() + ' ' + x.capitalize(),
                                                            description='Disabled :x:', color=discord.Color.red())

                                lst = []

                                if commands[str(ctx.guild.id)][s][x.capitalize()]:
                                    for item in commands[str(ctx.guild.id)][s][x.capitalize()]:
                                        if not ctx.guild.get_role(item):
                                            lst.append(str(ctx.guild.get_member(item)))
                                        else:
                                            lst.append('@' + str(ctx.guild.get_role(item)))
                                    message.add_field(name='User and Role List', value='\n'.join(lst))

                                else:
                                    message.add_field(name='User and Role List', value='None')

                                await ctx.respond(embed=message)

                            else:
                                await ctx.respond(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                    color=discord.Color.red()))

                        else:
                            await ctx.respond(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.respond(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

                elif len(args.split()) >= 4:
                    s = args.split()[0].lower()
                    x = args.split()[1].lower()
                    y = args.split()[2].lower()
                    z = args.split()[3]

                    if s in cmds:
                        if x == 'cooldown':
                            if y == 'set':
                                try:
                                    commands[str(ctx.guild.id)][s]['Cooldown'] = int(z)
                                    commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                    await ctx.respond(embed=discord.Embed(
                                        description=':thumbsup: **The settings have been updated.**',
                                        color=discord.Color.red()))

                                except ValueError:
                                    await ctx.respond(embed=discord.Embed(
                                        description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                        color=discord.Color.red()))

                            else:
                                await ctx.respond(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                    color=discord.Color.red()))

                        elif x == 'whitelist' or x == 'blacklist':
                            if y == 'add':
                                user_converter = UserConverter()
                                role_converter = RoleConverter()

                                try:
                                    user = await user_converter.convert(ctx, z)
                                except BadArgument:
                                    try:
                                        user = await role_converter.convert(ctx, z)
                                    except BadArgument:
                                        await ctx.respond(embed=discord.Embed(
                                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                            color=discord.Color.red()))

                                        return

                                if commands[str(ctx.guild.id)][s][x.capitalize()]:
                                    commands[str(ctx.guild.id)][s][x.capitalize()].append(user.id)
                                else:
                                    commands[str(ctx.guild.id)][s][x.capitalize()] = [user.id]
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.respond(embed=discord.Embed(
                                    description=':thumbsup: **The settings have been updated.**',
                                    color=discord.Color.red()))

                            elif y == 'remove':
                                user_converter = UserConverter()
                                role_converter = RoleConverter()

                                try:
                                    user = await user_converter.convert(ctx, z)
                                except BadArgument:
                                    try:
                                        user = await role_converter.convert(ctx, z)
                                    except BadArgument:
                                        await ctx.respond(embed=discord.Embed(
                                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                            color=discord.Color.red()))

                                        return

                                if commands[str(ctx.guild.id)][s][x.capitalize()]:
                                    commands[str(ctx.guild.id)][s][x.capitalize()].remove(user.id)

                                    if not commands[str(ctx.guild.id)][s][x.capitalize()]:
                                        commands[str(ctx.guild.id)][s][x.capitalize()] = None
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.respond(embed=discord.Embed(
                                    description=':thumbsup: **The settings have been updated.**',
                                    color=discord.Color.red()))

                            else:
                                await ctx.respond(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                    color=discord.Color.red()))

                        else:
                            await ctx.respond(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.respond(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

                else:
                    await ctx.respond(embed=discord.Embed(
                        description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                        color=discord.Color.red()))

            elif setting in ('defaultgamesettings', 'dgs'):

                dgs_file = s3_resource.Object('unobot-bucket', 'dgs.json')
                dgs = json.loads(dgs_file.get()['Body'].read().decode('utf-8'))

                if not args:
                    message = discord.Embed(title=prefix + 'settings defaultgamesettings', color=discord.Color.red())
                    message.add_field(name=':pencil2: Add & Remove Default Game Settings',
                                      value='Add game settings that are automatically applied to a game.\n\n'
                                            '`' + prefix + 'settings dgs <game setting> <on|off|set|view>`\n' + chr(
                                          173), inline=False)
                    message.add_field(name=':mag: View Default Game Settings',
                                      value='View the default game settings\n\n'
                                            '`' + prefix + 'settings dgs view`')

                    await ctx.respond(embed=message)

                elif args == 'view':
                    message = discord.Embed(title='Default Game Settings', color=discord.Color.red())

                    for s in dgs[str(ctx.guild.id)].keys():
                        if type(dgs[str(ctx.guild.id)][s]) == int:
                            message.add_field(name=s, value=str(dgs[str(ctx.guild.id)][s]))
                        elif dgs[str(ctx.guild.id)][s]:
                            message.add_field(name=s, value='Enabled :white_check_mark:')
                        else:
                            message.add_field(name=s, value='Disabled :x:')

                    await ctx.respond(embed=message)

                elif len(args.split()) == 2:
                    s = args.split()[0]
                    x = args.split()[1].lower()

                    if s in default_dgs:
                        if x == 'on':
                            dgs[str(ctx.guild.id)][s] = True
                            dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                            await ctx.respond(embed=discord.Embed(
                                description=':thumbsup: **The settings have been updated.**',
                                color=discord.Color.red()))

                        elif x == 'off':
                            dgs[str(ctx.guild.id)][s] = False
                            dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                            await ctx.respond(embed=discord.Embed(
                                description=':thumbsup: **The settings have been updated.**',
                                color=discord.Color.red()))

                        elif x == 'view':
                            if type(dgs[str(ctx.guild.id)][s]) == int:
                                message = discord.Embed(title=s + ' Game Setting',
                                                        description='`' + str(dgs[str(ctx.guild.id)][s]) + '`',
                                                        color=discord.Color.red())
                            elif dgs[ctx.guild.id][s]:
                                message = discord.Embed(title=s + ' Game Setting',
                                                        description='Enabled :white_check_mark:',
                                                        color=discord.Color.red())
                            else:
                                message = discord.Embed(title=s + ' Game Setting', description='Disabled :x:',
                                                        color=discord.Color.red())

                            if s.lower == 'drawuntilmatch':
                                message.add_field(name='Description:',
                                                  value='This will make the player keep drawing cards until they can play one.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' <on|off>`')
                            elif s.lower() == 'quickstart':
                                message.add_field(name='Description:',
                                                  value='Start a game quickly without an embed.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' <on|off>`')
                            elif s.lower() == 'spectategame':
                                message.add_field(name='Description:',
                                                  value='Creates a spectator channel accessible to users with the UNO Spectator role.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' <on|off>`')
                            elif s.lower() == 'stackcards':
                                message.add_field(name='Description:',
                                                  value='Stack draw 2 cards and wild draw 4 cards with each other.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' <on|off>`')
                            elif s.lower() == 'startingcards':
                                message.add_field(name='Description:',
                                                  value='Change the amount of cards players start with.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' set <integer>`')

                            elif s.lower() == 'flip':
                                message.add_field(name='Description:',
                                                  value='Changes the game mode to UNO Flip.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' <on|off>`')

                            elif s.lower() == '7-0':
                                message.add_field(name='Description:',
                                                  value='Applies the 7-0 rule to UNO.\n\n'
                                                        'Enable or disable it using `' + prefix + 'settings dgs ' + s + ' <on|off>`')

                            else:
                                await ctx.respond(
                                    embed=discord.Embed(description=':x: **' + s + '** is not a valid game setting.',
                                                        color=discord.Color.red()))

                                return

                            await ctx.respond(embed=message)

                    else:
                        await ctx.respond(embed=discord.Embed(
                            description=':x: **' + s + '** is not a game setting. Use `' + prefix + 'settings dgs view` for a list of settings.',
                            color=discord.Color.red()))

                elif len(args.split()) >= 3:
                    s = args.split()[0]
                    x = args.split()[1]
                    y = args.split()[2]

                    if s == 'StartingCards':
                        if x == 'set':
                            try:
                                if 3 <= int(y) <= 15:
                                    dgs[str(ctx.guild.id)][s] = int(y)
                                    dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                                    await ctx.respond(embed=discord.Embed(
                                        description=':thumbsup: **The settings have been updated.**',
                                        color=discord.Color.red()))
                                else:

                                    await ctx.respond(
                                        embed=discord.Embed(description=':x: **You can only start with 3-15 cards.**',
                                                            color=discord.Color.red()))

                            except ValueError:
                                await ctx.respond(embed=discord.Embed(
                                    description=':x: Please enter an integer.',
                                    color=discord.Color.red()))

                        else:
                            await ctx.respond(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.respond(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

            elif setting == 'reset':
                message = discord.Embed(description=':warning: Are you sure you want to reset UNOBot?'
                                                    ' **Settings including command settings, server stats, and ongoing games will be lost.**\n\n'
                                                    'Respond with **CONFIRM** in 30 seconds to confirm and reset UNOBot.',
                                        color=discord.Color.red())
                resets.append(ctx.guild.id)
                await ctx.respond(embed=message)

                def check(m):
                    return m.content == 'CONFIRM' and (
                            not commands[str(ctx.guild.id)]['settings']['WhitelistEnabled'] or (
                            commands[str(ctx.guild.id)]['settings']['Whitelist'] and ctx.author.id in
                            commands[str(ctx.guild.id)]['settings'][
                                'Whitelist'] or ctx.author == ctx.guild.owner))

                try:
                    await client.wait_for('message', check=check, timeout=30.0)
                except asyncio.TimeoutError:
                    await ctx.respond(embed=discord.Embed(description=':ok_hand: **OK, UNOBot will not reset.**',
                                                          color=discord.Color.red()))

            if commands[str(ctx.guild.id)]['settings']['Cooldown'] > 0:
                cooldowns[str(ctx.guild.id)].append('settings')

                def check(message):
                    return len(message.content.split()) == 6 \
                           and message.content.split()[0] in (
                               prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                               prefix + 'setting',
                               prefix + 'stng') \
                           and message.content.split()[1].lower() == 'commands' \
                           and message.content.split()[2].lower() == 'settings' \
                           and message.content.split()[3].lower() == 'cooldown' \
                           and message.content.split()[4].lower() == 'set'

                try:
                    m = await client.wait_for('message', check=check,
                                              timeout=float(commands[str(ctx.guild.id)]['settings']['Cooldown']))
                    await client.process_commands(m)
                    cooldowns[str(ctx.guild.id)].remove('settings')

                except asyncio.TimeoutError:
                    cooldowns[str(ctx.guild.id)].remove('settings')

        else:
            await ctx.respond(
                embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                    color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['settings']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-sg', description='Starts a game of UNO.')
@has_permissions(read_messages=True)
async def startgame(ctx, *, args: Option(str, 'Game settings you wish to apply', required=False, default='')):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if ctx.channel.category.name != 'UNO-GAME':
        if 'startgame' not in cooldowns[str(ctx.guild.id)] and ctx.channel.category.name != 'UNO-GAME':
            if commands[str(ctx.guild.id)]['startgame']['Enabled']:
                if ((not commands[str(ctx.guild.id)]['startgame']['BlacklistEnabled'] or not
                commands[str(ctx.guild.id)]['startgame']['Blacklist'])
                    or ctx.author.id not in commands[str(ctx.guild.id)]['startgame']['Blacklist']) \
                        and (not commands[str(ctx.guild.id)]['startgame']['WhitelistEnabled'] or
                             commands[str(ctx.guild.id)]['startgame']['Whitelist'] and ctx.author.id in
                             commands[str(ctx.guild.id)]['startgame'][
                                 'Whitelist']) or ctx.author == ctx.guild.owner:
                    if str(ctx.guild.id) not in games or games[str(ctx.guild.id)]['seconds'] == 40:
                        dgs = json.loads(
                            s3_resource.Object('unobot-bucket', 'dgs.json').get()['Body'].read().decode('utf-8'))

                        games[str(ctx.guild.id)] = {'seconds': 40}
                        games[str(ctx.guild.id)]['settings'] = dgs[str(ctx.guild.id)]
                        games[str(ctx.guild.id)]['players'] = {}
                        games[str(ctx.guild.id)]['creator'] = ctx.author.id

                        user_options = json.loads(
                            s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                        if args:
                            a = args.split()
                            for i in range(len(a)):
                                if a[i] in (
                                        'DrawUntilMatch', 'DisableJoin', 'SpectateGame', 'StackCards',
                                        'Flip'):
                                    games[str(ctx.guild.id)]['settings'][a[i]] = True

                                elif a[i] == '7-0':
                                    games[str(ctx.guild.id)]['settings'][a[i]] = True

                                elif a[i] == 'StartingCards':
                                    continue

                                elif a[i] == 'set':
                                    if a[i - 1] == 'StartingCards':
                                        try:
                                            if 3 <= int(a[i + 1]) <= 15:
                                                games[str(ctx.guild.id)]['settings']['StartingCards'] = int(
                                                    a[i + 1])

                                                break

                                            else:
                                                await ctx.respond(
                                                    embed=discord.Embed(
                                                        description=':x: **You can only start with 3-15 cards.**',
                                                        color=discord.Color.red()))

                                                del games[str(ctx.guild.id)]

                                                return

                                        except ValueError:
                                            await ctx.respond(embed=discord.Embed(
                                                description=':x: Please enter an integer for the number of starting cards.',
                                                color=discord.Color.red()))

                                            del games[str(ctx.guild.id)]

                                            return

                                    else:
                                        await ctx.respond(embed=discord.Embed(
                                            description=':x: I don\'t understand your command, use `' + prefix + 'commands startgame`',
                                            color=discord.Color.red()))

                                        del games[str(ctx.guild.id)]

                                        return

                                else:
                                    await ctx.respond(embed=discord.Embed(
                                        description=':x: I don\'t understand your command, use `' + prefix + 'commands startgame`',
                                        color=discord.Color.red()))

                                    del games[str(ctx.guild.id)]

                                    return

                        if not games[str(ctx.guild.id)]['settings']['Flip']:
                            message = discord.Embed(title='A game of UNO is going to start!',
                                                    description='Less than 30 seconds left!',
                                                    color=discord.Color.red())
                        else:
                            message = discord.Embed(title='A game of UNO is going to start!',
                                                    description='Less than 30 seconds left!',
                                                    color=discord.Color.from_rgb(102, 51, 153))

                        message.add_field(name='Players:', value='None', inline=False)

                        s = ""
                        for setting in games[str(ctx.guild.id)]['settings']:
                            if setting == 'StartingCards':
                                if games[str(ctx.guild.id)]['settings']['StartingCards'] != 7:
                                    s += ('• ' + setting + "\n")
                            elif games[str(ctx.guild.id)]['settings'][setting]:
                                s += ('• ' + setting + "\n")

                        if s:
                            message.add_field(name='Game Settings:', value=s, inline=False)
                        else:
                            message.add_field(name='Game Settings:', value='None', inline=False)

                        message.add_field(name='Game Creator:', value=str(ctx.author), inline=False)

                        join = Button(label='Join!/Leave', style=discord.ButtonStyle.green, emoji='✋')
                        async def join_callback(interaction):
                            await interaction.response.defer()

                            message = interaction.message
                            guild = interaction.guild
                            user = interaction.user

                            if str(user.id) not in games[str(guild.id)]['players']:
                                for g in client.guilds:
                                    user_options[str(user.id)].pop(str(g.id), None)

                                games[str(guild.id)]['players'][str(user.id)] = user_options[
                                    str(user.id)]
                                games[str(guild.id)]['players'][str(user.id)]['cards'] = []

                            else:
                                del games[str(guild.id)]['players'][str(user.id)]

                            p = ""
                            for key in games[str(guild.id)]['players']:
                                if str.isdigit(key):
                                    p += (':small_blue_diamond:' + (client.get_user(int(key))).name + "\n")
                                else:
                                    p += (':small_blue_diamond:' + key + "\n")
                            if not p:
                                p = 'None'

                            message.embeds[0].set_field_at(0, name='Players:',
                                                           value=p,
                                                           inline=False)

                            await message.edit(embed=message.embeds[0])
                        join.callback = join_callback

                        start = Button(label='Start now!', style=discord.ButtonStyle.blurple, emoji='▶️')
                        async def start_callback(interaction):
                            await interaction.response.defer()

                            if interaction.user == interaction.guild.owner or interaction.user.id == \
                                    games[str(interaction.guild.id)]['creator']:

                                n = len(games[str(interaction.guild.id)]['players'].keys())

                                if n > 1:
                                    await interaction.message.edit(view=None)

                                    games[str(interaction.guild.id)]['seconds'] = -2

                                    p = ""
                                    for key in games[str(ctx.guild.id)]['players']:
                                        if str.isdigit(key):
                                            p += (':small_blue_diamond:' + (client.get_user(int(key))).name + "\n")
                                        else:
                                            p += (':small_blue_diamond:' + key + "\n")

                                    interaction.message.embeds[0].set_field_at(0, name='Players:', value=p,
                                                                               inline=False)

                                    await interaction.message.edit(embed=interaction.message.embeds[0])

                                    message_dict = interaction.message.embeds[0].to_dict()

                                    message_dict['title'] = 'A game of UNO has started!'
                                    message_dict[
                                        'description'] = ':white_check_mark: Go to your UNO channel titled with your username.'

                                    try:
                                        await interaction.message.edit(embed=discord.Embed.from_dict(message_dict),
                                                                       view=None)

                                        await game_setup(await client.get_context(interaction.message),
                                                         games[str(interaction.guild.id)])
                                    except discord.NotFound:
                                        pass
                        start.callback = start_callback

                        cancel = Button(label='Cancel', style=discord.ButtonStyle.red)
                        async def cancel_callback(interaction):
                            if interaction.user == interaction.guild.owner or str(interaction.user) == \
                                    interaction.message.embeds[0].to_dict()['fields'][2][
                                        'value']:

                                await interaction.message.edit(view=None)

                                games[str(interaction.guild.id)]['seconds'] = -1

                                message_dict = interaction.message.embeds[0].to_dict()
                                message_dict['title'] = 'A game of UNO was cancelled!'

                                if interaction.user == interaction.guild.owner:
                                    message_dict['description'] = ':x: The server owner cancelled the game.'
                                elif str(interaction.user) == interaction.message.embeds[0].to_dict()['fields'][2][
                                    'value']:
                                    message_dict['description'] = ':x: The game creator cancelled the game.'

                                p = ""
                                for key in games[str(ctx.guild.id)]['players']:
                                    if str.isdigit(key):
                                        p += (':small_blue_diamond:' + (client.get_user(int(key))).name + "\n")
                                    else:
                                        p += (':small_blue_diamond:' + key + "\n")
                                if not p:
                                    p = 'None'

                                try:
                                    del games[str(interaction.guild.id)]
                                except ValueError:
                                    pass

                                message_dict['fields'][0]['value'] = p

                                await interaction.message.edit(embed=discord.Embed.from_dict(message_dict))

                                print('[' + datetime.now().strftime(
                                    '%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game is cancelled in ' + str(
                                    interaction.guild) + '.')
                        cancel.callback = cancel_callback

                        add = Button(label='Add bot', emoji='➕')
                        async def add_callback(interaction):
                            if interaction.user == interaction.guild.owner or str(interaction.user) == \
                                    interaction.message.embeds[0].to_dict()['fields'][2][
                                        'value']:
                                await interaction.response.defer()

                                message = interaction.message
                                field = message.embeds[0].to_dict()['fields'][0]
                                bot_lst = [x for x in bot_names if x not in field['value']]

                                if len(bot_lst) <= 1:
                                    v = View()
                                    v.add_item(join)
                                    v.add_item(start)
                                    v.add_item(cancel)
                                    await message.edit(view=v)

                                bot = choice(bot_lst)

                                games[str(interaction.guild.id)]['players'][bot] = None

                                p = ""
                                for key in games[str(ctx.guild.id)]['players']:
                                    if str.isdigit(key):
                                        p += (':small_blue_diamond:' + (client.get_user(int(key))).name + "\n")
                                    else:
                                        p += (':small_blue_diamond:' + key + "\n")

                                message.embeds[0].set_field_at(0, name='Players:',
                                                               value=p,
                                                               inline=False)

                                await message.edit(embed=message.embeds[0])
                        add.callback = add_callback

                        view = View()
                        view.add_item(join)
                        if not games[str(ctx.guild.id)]['settings']['7-0']:
                            view.add_item(add)
                        view.add_item(start)
                        view.add_item(cancel)

                        response = await ctx.respond(embed=message, view=view)
                        e = await response.original_message()
                        games[str(ctx.guild.id)]['message'] = e.id

                        while True:
                            if str(ctx.guild.id) not in games or games[str(ctx.guild.id)]['seconds'] == -2:
                                break

                            if games[str(ctx.guild.id)]['seconds'] == -1:
                                del games[str(ctx.guild.id)]

                                break

                            games[str(ctx.guild.id)]['seconds'] -= 10
                            m = (await ctx.fetch_message(e.id)).embeds[0]

                            if games[str(ctx.guild.id)]['seconds'] == 0:
                                await e.edit(view=None)

                                n = len(games[str(ctx.guild.id)]['players'].keys())
                                if n > 1:
                                    message_dict = m.to_dict()
                                    message_dict['title'] = 'A game of UNO has started!'
                                    message_dict[
                                        'description'] = ':white_check_mark: Go to your UNO channel titled with your username.'

                                    p = ""
                                    for key in games[str(ctx.guild.id)]['players']:
                                        if str.isdigit(key):
                                            p += (':small_blue_diamond:' + (client.get_user(int(key))).name + "\n")
                                        else:
                                            p += (':small_blue_diamond:' + key + "\n")

                                    for field in message_dict['fields']:
                                        if field['name'] == 'Players:':
                                            field['value'] = p
                                            break

                                    await e.edit(embed=discord.Embed.from_dict(message_dict))

                                    await game_setup(ctx, games[str(ctx.guild.id)])

                                else:
                                    message_dict = m.to_dict()
                                    message_dict['title'] = 'A game of UNO failed to start!'
                                    message_dict[
                                        'description'] = ':x: Not enough players! At least 2 players are needed.'

                                    p = ""
                                    for key in games[str(ctx.guild.id)]['players']:
                                        if str.isdigit(key):
                                            p += (':small_blue_diamond:' + (client.get_user(int(key))).name + "\n")
                                        else:
                                            p += (':small_blue_diamond:' + key + "\n")
                                    if not p:
                                        p = 'None'

                                    message_dict['fields'][0]['value'] = p

                                    await e.edit(embed=discord.Embed.from_dict(message_dict), view=None)

                                    del games[str(ctx.guild.id)]

                                    print('[' + datetime.now().strftime(
                                        '%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game failed to start in ' + str(
                                        ctx.guild) + '.')

                                break

                            message_dict = m.to_dict()
                            message_dict['description'] = 'Less than ' + str(
                                games[str(ctx.guild.id)]['seconds']) + ' seconds left!'

                            await e.edit(embed=discord.Embed.from_dict(message_dict))
                            await asyncio.sleep(10)

                        if commands[str(ctx.guild.id)]['startgame']['Cooldown'] > 0:
                            cooldowns[str(ctx.guild.id)].append('startgame')

                            def check(message):
                                return len(message.content.split()) == 6 \
                                       and message.content.split()[0] == prefix + 'settings' \
                                       and message.content.split()[1].lower() == 'commands' \
                                       and message.content.split()[2].lower() == 'startgame' \
                                       and message.content.split()[3].lower() == 'cooldown' \
                                       and message.content.split()[4].lower() == 'set'

                            try:
                                m = await client.wait_for('message', check=check,
                                                          timeout=float(
                                                              commands[str(ctx.guild.id)]['startgame']['Cooldown']))

                                await client.process_commands(m)

                                raise asyncio.TimeoutError("Countdown cancelled.")

                            except asyncio.TimeoutError:
                                cooldowns[str(ctx.guild.id)].remove('startgame')

                    else:
                        await ctx.respond(embed=discord.Embed(description=':x: **A game is already underway!**',
                                                              color=discord.Color.red()))

                else:
                    await ctx.respond(
                        embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                            color=discord.Color.red()))

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
                    commands[str(ctx.guild.id)]['startgame']['Cooldown']) + ' seconds.**', color=discord.Color.red()))

    else:
        await ctx.respond(
            embed=discord.Embed(description=':x: **You can\'t use this command here!**', color=discord.Color.red()))


@client.slash_command(name='u-eg', description='Forcefully ends a game of UNO.')
@has_permissions(read_messages=True)
async def endgame(ctx):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'endgame' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['endgame']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['endgame']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['endgame']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['endgame']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['endgame']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['endgame']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['endgame'][
                             'Whitelist']) or ctx.author == ctx.guild.owner or ctx.author == ctx.guild.get_member(
                games[str(ctx.guild.id)]['creator']):
                if ctx.channel.category.name != 'UNO-GAME':
                    if str(ctx.guild.id) in games and str(ctx.guild.id) not in ending:
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description=':warning: **' + ctx.author.name + ' is ending the game!**',
                            color=discord.Color.red()))) for x in ctx.guild.text_channels if
                            x.category.name == 'UNO-GAME'])

                        ending.append(str(ctx.guild.id))
                        try:
                            await game_shutdown(games[str(ctx.guild.id)], ctx.guild, None)
                        except:
                            pass

                        await ctx.respond(
                            embed=discord.Embed(description=':thumbsup: **The game has been shut down.**',
                                                color=discord.Color.red()))

                    else:
                        await ctx.respond(
                            embed=discord.Embed(description=':x: **The game doesn\'t exist.**',
                                                color=discord.Color.red()))

                else:
                    await ctx.respond(
                        embed=discord.Embed(description=':x: **You can\'t use this command here!**',
                                            color=discord.Color.red()))

                if commands[str(ctx.guild.id)]['endgame']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('endgame')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting', prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'endgame' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(commands[str(ctx.guild.id)]['engame']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('endgame')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('endgame')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['endgame']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-leave', description='Gets you out of an ongoing game of UNO')
@has_permissions(read_messages=True)
async def leavegame(ctx):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'leavegame' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['leavegame']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['leavegame']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['leavegame']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['leavegame']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['leavegame']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['leavegame']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['leavegame'][
                             'Whitelist']) or ctx.author == ctx.guild.owner:
                if ctx.channel.category.name == 'UNO-GAME' and ctx.channel.name != 'spectator-uno-channel':
                    if str(ctx.guild.id) in games and str(ctx.author.id) in games[str(ctx.guild.id)]['players']:
                        games[str(ctx.guild.id)]['players'][str(ctx.author.id)]['left'] = True

                        await asyncio.gather(*[asyncio.create_task(x.send(
                            embed=discord.Embed(description=':warning: **' + ctx.author.name + '** left.',
                                                color=discord.Color.red()))) for x
                            in ctx.channel.category.text_channels])

                        p = [x for x in games[str(ctx.guild.id)]['players']]

                        if len([x for x in p if not str.isdigit(x) or str.isdigit(x) and 'left' not in
                                                games[str(ctx.guild.id)]['players'][x]]) >= 2:
                            n = None

                            temp = iter(p)
                            for key in temp:
                                if key == str(ctx.author.id):
                                    n = next(temp, next(iter(p)))
                                    if str.isdigit(n):
                                        n = ctx.guild.get_member(int(n))
                                    break

                            for bot in [x for x in games[str(ctx.guild.id)]['players'] if not str.isdigit(x)]:
                                games[str(ctx.guild.id)]['players'][bot].channels.remove(ctx.channel)

                            await ctx.channel.delete()

                            if ctx.author.id == games[str(ctx.guild.id)]['player']:
                                await display_cards(n, ctx.guild)

                        else:
                            await ctx.defer()

                            await asyncio.gather(*[asyncio.create_task(x.send(
                                embed=discord.Embed(
                                    description=':x: **Since not enough players are left, ending game...**',
                                    color=discord.Color.red()))) for x in ctx.channel.category.text_channels])

                            ending.append(str(ctx.guild.id))

                            p = [x for x in games[str(ctx.guild.id)]['players'] if
                                 not str.isdigit(x) or str.isdigit(x) and 'left' not in
                                 games[str(ctx.guild.id)]['players'][x]]
                            if p:
                                if str.isdigit(p[0]):
                                    await game_shutdown(games[str(ctx.guild.id)], ctx.guild,
                                                        ctx.guild.get_member(int(p[0])))
                                else:
                                    await game_shutdown(games[str(ctx.guild.id)], ctx.guild, p[0])
                            else:
                                await game_shutdown(games[str(ctx.guild.id)], ctx.guild)

                else:
                    await ctx.respond(
                        embed=discord.Embed(description=':x: **You can\'t use this command here!**',
                                            color=discord.Color.red()))

                if commands[str(ctx.guild.id)]['leavegame']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('leavegame')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting', prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'leavegame' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(
                                                      commands[str(ctx.guild.id)]['leavegame']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('leavegame')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('leavegame')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['leavegame']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-kick', description='Kicks someone out of an ongoing game of UNO')
@has_permissions(read_messages=True)
async def kick(ctx, user):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'kick' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['kick']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['kick']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['kick']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['kick']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['kick']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['kick']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['kick']['Whitelist']) or ctx.author == ctx.guild.owner:
                user_converter = UserConverter()

                try:
                    player = await user_converter.convert(ctx, user)
                except BadArgument:
                    await ctx.respond(embed=discord.Embed(
                        description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                        color=discord.Color.red()))

                    return

                if str(ctx.guild.id) in games and str(player.id) in games[str(ctx.guild.id)]['players'] and str(
                        ctx.guild.id) not in ending:
                    games[str(ctx.guild.id)]['players'][str(player.id)]['left'] = True

                    await asyncio.gather(*[asyncio.create_task(x.send(
                        embed=discord.Embed(description=':warning: **' + player.name + '** was kicked.',
                                            color=discord.Color.red()))) for x in
                        ctx.guild.text_channels if x.category.name == 'UNO-GAME'])

                    p = [x for x in games[str(ctx.guild.id)]['players']]

                    if len([x for x in p if not str.isdigit(x) or str.isdigit(x) and 'left' not in
                                            games[str(ctx.guild.id)]['players'][x]]) >= 2:
                        n = None

                        temp = iter(p)
                        for key in temp:
                            if key == str(player.id):
                                n = next(temp, next(iter(p)))
                                if str.isdigit(n):
                                    n = ctx.guild.get_member(int(n))
                                break

                        channel = discord.utils.get(ctx.guild.text_channels,
                                                    name=sub(r'[^\w -]', '',
                                                             player.name.lower().replace(' ',
                                                                                         '-')) + '-uno-channel')

                        for bot in [x for x in games[str(ctx.guild.id)]['players'] if not str.isdigit(x)]:
                            games[str(ctx.guild.id)]['players'][bot].channels.remove(channel)

                        await channel.delete()

                        if player.id == games[str(ctx.guild.id)]['player']:
                            await display_cards(n, ctx.guild)

                    else:
                        for channel in [x for x in ctx.guild.text_channels if x.category.name == 'UNO-GAME']:
                            await channel.send(
                                embed=discord.Embed(description=':x: Since not enough players are left, ending game...',
                                                    color=discord.Color.red()))

                        ending.append(str(ctx.guild.id))

                        p = [x for x in games[str(ctx.guild.id)]['players'] if
                             not str.isdigit(x) or str.isdigit(x) and 'left' not in games[str(ctx.guild.id)]['players'][
                                 x]]
                        if p:
                            if str.isdigit(p[0]):
                                await game_shutdown(games[str(ctx.guild.id)], ctx.guild, ctx.guild.get_member(int(p[0])))
                            else:
                                await game_shutdown(games[str(ctx.guild.id)], ctx.guild, p[0])
                        else:
                            await game_shutdown(games[str(ctx.guild.id)], ctx.guild)

                    await ctx.respond(embed=discord.Embed(
                        description=':thumbsup: **The player has been kicked.**',
                        color=discord.Color.red()))

                else:
                    await ctx.respond(embed=discord.Embed(
                        description=':x: **No game exists.**',
                        color=discord.Color.red()))

                if commands[str(ctx.guild.id)]['kick']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('kick')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting', prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'kick' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(
                                                      commands[str(ctx.guild.id)]['kick']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('kick')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('kick')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['kick']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-spectate', description='Turns your ability to spectate any game of UNO on or off')
@has_permissions(read_messages=True)
async def spectate(ctx, option: Option(str, 'on or off', required=True)):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'spectate' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['spectate']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['spectate']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['spectate']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['spectate']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['spectate']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['spectate']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['spectate']['Whitelist']) or ctx.author == ctx.guild.owner:
                role = discord.utils.get(ctx.guild.roles, name='UNO Spectator')

                if option.lower() == 'on' and role not in ctx.author.roles:
                    await ctx.author.add_roles(role)

                    await ctx.respond(embed=discord.Embed(
                        description=':thumbsup: **You now have the UNO Spectator role.**\nYou can now spectate any UNO game with the **SpectateGame** setting on.',
                        color=discord.Color.red()))

                elif option.lower() == 'off' and role in ctx.author.roles:
                    await ctx.author.remove_roles(role)

                if commands[str(ctx.guild.id)]['spectate']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('spectate')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting', prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'spectate' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(commands[str(ctx.guild.id)]['spectate']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('spectate')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('spectate')

            else:
                await ctx.respond(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.respond(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['spectate']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


if __name__ == '__main__':
    main()