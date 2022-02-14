import asyncio
import discord
import json
import boto3
import sys
from os import getenv
from treelib import Tree
from math import comb
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

prefix = '/u-'
client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
client.remove_command('help')
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
    'allowalerts': {
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
cmds = ('startgame', 'endgame', 'joingame', 'leavegame', 'kick', 'spectate', 'stats', 'globalstats', 'leaderboard',
        'globalleaderboard', 'options', 'commands', 'allowalerts')
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
resets = []
cooldowns = {}
games = {}
stack = {}
ending = []
last_run = datetime.now()
s3_client = boto3.client('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))
s3_resource = boto3.resource('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))
sys.setrecursionlimit(10**5)


def main():
    client.run(getenv('BOT_TOKEN'))


async def initialize():
    try:
        s3_resource.Object('unobot-bucket', 'dgs.json').load()
    except ClientError:
        s3_client.put_object(Bucket='unobot-bucket', Key='dgs.json', Body=b'{}')
    dgs_file = s3_resource.Object('unobot-bucket', 'dgs.json')
    dgs = json.loads(dgs_file.get()['Body'].read().decode('utf-8'))

    try:
        s3_resource.Object('unobot-bucket', 'users.json').load()
    except ClientError:
        s3_client.put_object(Bucket='unobot-bucket', Key='users.json', Body=b'{}')
    users_file = s3_resource.Object('unobot-bucket', 'users.json')
    user_stuff = json.loads(users_file.get()['Body'].read().decode('utf-8'))

    try:
        s3_resource.Object('unobot-bucket', 'commands.json').load()
    except ClientError:
        s3_client.put_object(Bucket='unobot-bucket', Key='commands.json', Body=b'{}')
    commands_file = s3_resource.Object('unobot-bucket', 'commands.json')
    commands = json.loads(commands_file.get()['Body'].read().decode('utf-8'))

    if client.guilds:

        if not dgs:
            for guild in client.guilds:
                dgs[str(guild.id)] = default_dgs

        else:
            for guild in client.guilds:
                if str(guild.id) not in dgs:
                    dgs[str(guild.id)] = default_dgs

        dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

        if not user_stuff:
            for member in [x for x in client.get_all_members() if x.id != client.user.id and not x.bot]:
                default_user_stuff = {"AllowAlerts": True}
                for guild in [x for x in client.guilds if x.get_member(member.id)]:
                    default_user_stuff[str(guild.id)] = {
                        'Wins': 0,
                        'Score': 0,
                        'Played': 0
                    }
                user_stuff[str(member.id)] = default_user_stuff

        else:
            for member in [x for x in client.get_all_members() if
                           str(x.id) not in user_stuff and x.id != client.user.id and not x.bot]:
                for guild in [x for x in client.guilds if x.get_member(member.id)]:
                    user_stuff[str(member.id)] = {"AllowAlerts": True}
                    user_stuff[str(member.id)][str(guild.id)] = {
                        'Wins': 0,
                        'Score': 0,
                        'Played': 0
                    }

        users_file.put(Body=json.dumps(user_stuff).encode('utf-8'))

        if not commands:
            for guild in client.guilds:
                commands[str(guild.id)] = default_command_settings

        else:
            for guild in client.guilds:
                if str(guild.id) not in commands:
                    commands[str(guild.id)] = default_command_settings

        commands_file.put(Body=json.dumps(commands).encode('utf-8'))

        for guild in client.guilds:
            cooldowns[str(guild.id)] = []

    else:
        dgs_file.put(Body=b'{}')
        users_file.put(Body=b'{}')
        commands_file.put(Body=b'{}')

    for guild in client.guilds:
        if not discord.utils.get(guild.roles, name='UNO Spectator'):
            await guild.create_role(name='UNO Spectator', color=discord.Color.red())

    await client.change_presence(activity=discord.Game(name=f'UNO | Use {prefix}help'))


def rank(user=None, guild=None):
    scores = []
    users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

    if guild:
        for id in [x for x in list(users.keys()) if guild.get_member(int(x))]:
            scores.append(users[id][str(guild.id)]['Score'])

    else:
        s = 0
        for id in users:
            for g in [x for x in client.guilds if x.get_member(int(id))]:
                s += users[id][str(g.id)]['Score']
            scores.append(s)
            s = 0

    leaderboard = len(scores) - rankdata(scores, method='max') + 1
    if user:
        if guild:
            return round(leaderboard[[x for x in list(users.keys()) if guild.get_member(int(x))].index(str(user.id))]), len(leaderboard)
        else:
            return round(leaderboard[list(users.keys()).index(str(user.id))]), len(leaderboard)
    else:
        return [round(x) for x in leaderboard]


def has_played(user):
    for guild in [x for x in client.guilds if x.get_member(user.id)]:
        if json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))[
            str(user.id)][str(guild.id)]['Played'] > 0:
            return True

    return False


def no_guild(user):
    return any(guild.get_member(user.id) for guild in client.guilds)


def list_duplicates_of(seq, item):
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


async def cmd_info(ctx, cmd):
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


async def game_setup(ctx, d, bot):
    guild = ctx.guild

    flip = d['settings']['Flip']

    category = await guild.create_category('UNO-GAME')

    if d['settings']['Flip']:
        d['cards'] = flip_cards
    else:
        d['cards'] = cards

    if bot:
        hand = sample(d['cards'], d['settings']['StartingCards'])
        b = Bot(ctx.guild, games, hand)
        d['players'][str(b.id)] = b
        d['cards'] = [card for card in d['cards'] if card not in hand]

    player_ids = list(d['players'].keys())

    order = sample(player_ids, len(player_ids))
    ordered_dict = OrderedDict()
    for x in order:
        ordered_dict[x] = d['players'][x]

    d['players'] = dict(ordered_dict)

    async def set_channel(id):
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
        for key in [x for x in d['settings'] if d['settings'][x] and x != 'StartingCards' or d['settings'][x] != 7 and x == 'StartingCards']:
            gcontents += f'• {key}\n'
        gsettings = await channel.send(content=gcontents)
        await gsettings.pin()

    await asyncio.gather(*[asyncio.create_task(set_channel(x)) for x in player_ids if x != str(client.user.id)])

    if d['settings']['SpectateGame']:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.roles, name='UNO Spectator'): discord.PermissionOverwrite(read_messages=True)
        }
        await category.create_text_channel('Spectator-UNO-Channel', overwrites=overwrites)

    if bot:
        b.channels = [x for x in guild.text_channels if x.category.name == 'UNO-GAME']

    for id in [x for x in player_ids if x != str(client.user.id)]:
        while len(d['cards']) <= d['settings']['StartingCards']:
            if flip:
                d['cards'] += flip_cards
            else:
                d['cards'] += cards

        hand = sample(d['cards'], d['settings']['StartingCards'])
        d['players'][id]['cards'] = hand
        d['cards'] = [card for card in d['cards'] if card not in hand]

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
                                       round(card.size[1] / 6.0123456790123456790123456790123)),
                                      Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))

                card = Image.open(
                    'images/' + d['players'][id]['cards'][
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

        await discord.utils.get(guild.text_channels,
                                name=sub(r'[^\w -]', '',
                                         guild.get_member(int(id)).name.lower().replace(' ',
                                                                                        '-')) + '-uno-channel').send(
            file=file, embed=m)

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

    if d['settings']['Flip']:
        color = search(r'red|blue|green|yellow', d['current'][0]).group(0)
    else:
        color = search(r'red|blue|green|yellow', d['current']).group(0)

    if color == 'red':
        message = discord.Embed(title='Top card:', color=discord.Color.red())
    elif color == 'blue':
        message = discord.Embed(title='Top card:', color=discord.Color.blue())
    elif color == 'green':
        message = discord.Embed(title='Top card:', color=discord.Color.green())
    else:
        message = discord.Embed(title='Top card:', color=discord.Color.from_rgb(255, 255, 0))

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

        message.set_image(url='attachment://topcard.png')
        await channel.send(file=file, embed=message)

    d['player'] = int(order[0])
    cplayer = order[0]

    if flip:
        d['dark'] = False

    try:
        del stack[str(guild.id)]
    except KeyError:
        pass

    print(
        '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game has started in ' + str(guild) + '.')

    if cplayer != str(client.user.id):
        hand = d['players'][cplayer]['cards']
    else:
        hand = d['players'][cplayer].cards

    if not d['settings']['Flip']:
        if '+2' in d['current']:
            if d['settings']['StackCards'] and any('+2' in card for card in hand) or any('+4' in card for card in hand):
                stack[str(guild.id)] = 2

                await asyncio.gather(
                    *[asyncio.create_task(x.send(embed=discord.Embed(description='**' + guild.get_member(
                        int(cplayer)).name + ' can choose to stack cards or draw 2 cards.**',
                                                                     color=discord.Color.red()))) for x in
                      category.text_channels])

                await display_cards(guild.get_member(int(cplayer)))

            else:
                await draw(guild.get_member(int(cplayer)), 2)
                await display_cards(guild.get_member(int(order[1])))

        else:
            await display_cards(guild.get_member(int(cplayer)))

    else:
        if '+1' in d['current'][0]:
            if d['settings']['StackCards'] and any('+2' in card for card in hand):
                stack[str(guild.id)] = 1

                await asyncio.gather(
                    *[asyncio.create_task(x.send(embed=discord.Embed(description='**' + guild.get_member(
                        int(cplayer)).name + ' can choose to stack cards or draw 1 card.**',
                                                                     color=discord.Color.red()))) for x in
                      category.text_channels])

                if cplayer == str(client.user.id):
                    await display_cards(d['players'][str(client.user.id)].member)
                else:
                    await display_cards(guild.get_member(int(cplayer)))

            else:
                if cplayer == str(client.user.id):
                    await draw(d['players'][str(client.user.id)].member, 1)
                else:
                    await draw(guild.get_member(int(cplayer)), 1)
                await display_cards(guild.get_member(int(order[1])))

        else:
            if cplayer == str(client.user.id):
                await display_cards(d['players'][str(client.user.id)].member)
            else:
                await display_cards(guild.get_member(int(cplayer)))


async def game_shutdown(d, winner: discord.Member = None, guild=None):
    player_ids = list(d['players'].keys())

    if winner and not guild:
        guild = winner.guild

        if winner.id != client.user.id:
            users_file = s3_resource.Object('unobot-bucket', 'users.json')
            users = json.loads(users_file.get()['Body'].read().decode('utf-8'))

            score = 0
            for key in [x for x in player_ids if x != str(winner.id)]:
                if key != str(client.user.id):
                    cards = games[str(guild.id)]['players'][key]['cards']
                else:
                    cards = games[str(guild.id)]['players'][key].cards

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

            if score == 1:
                message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +1 pt', color=discord.Color.red())
            else:
                message = discord.Embed(title=f'{winner.name} Won! 🎉 🥳 +{score} pts', color=discord.Color.red())
            message.set_image(url=winner.display_avatar.url)

            await asyncio.gather(
                *[asyncio.create_task(x.send(embed=message)) for x in guild.text_channels if x.category.name == 'UNO-GAME'])

            users[str(winner.id)][str(guild.id)]['Score'] += score
            users[str(winner.id)][str(guild.id)]['Wins'] += 1
            for i in [x for x in player_ids if x != str(client.user.id)]:
                users[i][str(guild.id)]['Played'] += 1

            users_file.put(Body=json.dumps(users).encode('utf-8'))

        else:
            message = discord.Embed(title=f'UNOBot Won! 🎉 🥳', color=discord.Color.red())
            message.set_image(url=client.user.display_avatar.url)

            await asyncio.gather(
                *[asyncio.create_task(x.send(embed=message)) for x in guild.text_channels if x.category.name == 'UNO-GAME'])

        await asyncio.sleep(10)

    for channel in [x for x in guild.text_channels if x.category.name == 'UNO-GAME']:
        await channel.delete()
    await discord.utils.get(guild.categories, name='UNO-GAME').delete()

    del games[str(guild.id)]
    ending.remove(str(guild.id))
    try:
        del stack[str(guild.id)]
    except KeyError:
        pass

    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game has ended in ' + str(guild))


async def draw(player: discord.Member, number, DUM=False, color=False):
    guild = player.guild
    bot = None

    if player.id == client.user.id:
        bot = games[str(guild.id)]['players'][str(client.user.id)]

    if color:
        draw = []

        current_color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)
        c = choice(games[str(guild.id)]['cards'])

        if not bot:
            games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                             card not in games[str(guild.id)]['players'][str(player.id)]['cards']]
        else:
            bot.cards.append(c)
            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if card not in bot.cards]

        if not games[str(guild.id)]['cards']:
            games[str(guild.id)]['cards'] += cards

        draw.append(c)

        color = search(r'pink|teal|orange|purple', c[1])
        while not color or color.group(0) != current_color:
            c = choice(games[str(guild.id)]['cards'])

            if not bot:
                games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                 card not in games[str(guild.id)]['players'][str(player.id)]['cards']]
            else:
                bot.cards.append(c)
                games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                 card not in bot.cards]

            if not games[str(guild.id)]['cards']:
                games[str(guild.id)]['cards'] += cards

            draw.append(c)

            color = search(r'pink|teal|orange|purple', c[1])

    else:
        if not DUM:
            draw = []

            for i in range(number):
                c = choice(games[str(guild.id)]['cards'])

                if not bot:
                    games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                    games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                     card not in games[str(guild.id)]['players'][str(player.id)][
                                                         'cards']]
                else:
                    bot.cards.append(c)
                    games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                 card not in bot.cards]

                if not games[str(guild.id)]['cards']:
                    if not games[str(guild.id)]['settings']['Flip']:
                        games[str(guild.id)]['cards'] += cards
                    else:
                        games[str(guild.id)]['cards'] += flip_cards

                draw.append(c)

        else:
            draw = []
            c = choice(games[str(guild.id)]['cards'])

            if not bot:
                games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                 card not in games[str(guild.id)]['players'][str(player.id)][
                                                     'cards']]
            else:
                bot.cards.append(c)
                games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                 card not in bot.cards]

            if not games[str(guild.id)]['cards']:
                games[str(guild.id)]['cards'] += cards

            draw.append(c)

            if not games[str(guild.id)]['settings']['Flip']:
                current_color = search(r'red|blue|green|yellow', games[str(guild.id)]['current']).group(0)
                current_value = search(r'\+[42]|wild|skip|reverse|\d', games[str(guild.id)]['current']).group(0)

                color = search(r'red|blue|green|yellow', c).group(0)
                value = search(r'\+[42]|wild|skip|reverse|\d', c).group(0)

                while color != current_color and value != current_value or not any(x in c for x in ('+4', 'wild')):
                    c = choice(games[str(guild.id)]['cards'])

                    if not bot:
                        games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                        games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                         card not in games[str(guild.id)]['players'][str(player.id)][
                                                             'cards']]
                    else:
                        bot.cards.append(c)
                        games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                         card not in bot.cards]

                    if not games[str(guild.id)]['cards']:
                        games[str(guild.id)]['cards'] += cards

                    draw.append(c)

                    color = search(r'red|blue|green|yellow', c).group(0)
                    value = search(r'\+[42]|wild|skip|reverse|\d', c).group(0)

            else:
                if not games[str(guild.id)]['dark']:
                    current_color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][0]).group(0)
                    current_value = search(r'\+[42]|wild|skip|reverse|\d', games[str(guild.id)]['current'][0]).group(0)

                    color = search(r'red|blue|green|yellow', c[0]).group(0)
                    value = search(r'\+[42]|wild|skip|reverse|\d', c[0]).group(0)

                    while color != current_color and value != current_value or not any(
                            x in c[0] for x in ('+2', 'wild')):
                        c = choice(games[str(guild.id)]['cards'])

                        if not bot:
                            games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                             card not in
                                                             games[str(guild.id)]['players'][str(player.id)][
                                                                 'cards']]
                        else:
                            bot.cards.append(c)
                            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                             card not in bot.cards]

                        if not games[str(guild.id)]['cards']:
                            games[str(guild.id)]['cards'] += cards

                        draw.append(c)

                        color = search(r'red|blue|green|yellow', c[0]).group(0)
                        value = search(r'\+[42]|wild|skip|reverse|\d', c[0]).group(0)

                else:
                    current_color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][1]).group(0)
                    current_value = search(r'\+[42]|wild|skip|reverse|\d', games[str(guild.id)]['current'][1]).group(0)

                    color = search(r'pink|teal|orange|purple', c[1]).group(0)
                    value = search(r'\+([251]|color)|wild|skip|reverse|flip|\d', c[1]).group(0)

                    while color != current_color and value != current_value or not any(
                            x in c[1] for x in ('+color', 'wild')):
                        c = choice(games[str(guild.id)]['cards'])

                        if not bot:
                            games[str(guild.id)]['players'][str(player.id)]['cards'].append(c)
                            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                             card not in
                                                             games[str(guild.id)]['players'][str(player.id)][
                                                                 'cards']]
                        else:
                            bot.cards.append(c)
                            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                             card not in bot.cards]

                        if not games[str(guild.id)]['cards']:
                            games[str(guild.id)]['cards'] += cards

                        draw.append(c)

                        color = search(r'red|blue|green|yellow', c[1]).group(0)
                        value = search(r'\+[42]|wild|skip|reverse|\d', c[1]).group(0)

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
                     round(card.size[1] / 6.0123456790123456790123456790123)),
                    Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))
        else:
            if not games[str(guild.id)]['dark']:
                for i in range(len(draw)):
                    card = Image.open('images/' + draw[i][0] + '.png')
                    refined = card.resize(
                        (round(card.size[0] / 6.0123456790123456790123456790123),
                         round(card.size[1] / 6.0123456790123456790123456790123)),
                        Image.ANTIALIAS)
                    image.paste(refined, (i * refined.size[0], 0))
            else:
                for i in range(len(draw)):
                    card = Image.open('images/' + draw[i][1] + '.png')
                    refined = card.resize(
                        (round(card.size[0] / 6.0123456790123456790123456790123),
                         round(card.size[1] / 6.0123456790123456790123456790123)),
                        Image.ANTIALIAS)
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
                                                                    player.name.lower().replace(' ', '-')) + '-uno-channel']
            )
        else:
            await asyncio.gather(
                *[asyncio.create_task(x.send(
                    embed=discord.Embed(description='**UNOBot** drew a card.',
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
                                                                    player.name.lower().replace(' ', '-')) + '-uno-channel']
            )
        else:
            await asyncio.gather(
                *[asyncio.create_task(x.send(
                    embed=discord.Embed(description='**UNOBot** drew **' + str(len(draw)) + '** cards.',
                                        color=discord.Color.red()))) for x in guild.text_channels if
                    x.category.name == 'UNO-GAME'])


async def display_cards(player: discord.Member):
    guild = player.guild

    if str(guild.id) not in ending:
        async def send_cards(channel):
            if channel.name == sub(r'[^\w -]', '',
                                   player.name.lower().replace(' ', '-')) + '-uno-channel':
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
                        card = Image.open('images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i] + '.png')
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
                            card = Image.open('images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][0] + '.png')
                        else:
                            card = Image.open('images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][1] + '.png')

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

                if player.id != client.user.id:
                    image = Image.new('RGBA', (
                        len(games[str(guild.id)]['players'][str(player.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)]['players'][str(player.id)]['cards'])):
                        if games[str(guild.id)]['settings']['Flip']:
                            if not games[str(guild.id)]['dark']:
                                card = Image.open('images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][1] + '.png')
                            else:
                                card = Image.open('images/' + games[str(guild.id)]['players'][str(player.id)]['cards'][i][0] + '.png')
                        else:
                            card = Image.open('images/back.png')

                        refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                               round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)

                        image.paste(refined, (i * refined.size[0], 0))

                else:
                    image = Image.new('RGBA', (
                        len(games[str(guild.id)]['players'][str(player.id)].cards) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)]['players'][str(player.id)].cards)):
                        if games[str(guild.id)]['settings']['Flip']:
                            if not games[str(guild.id)]['dark']:
                                card = Image.open(
                                    'images/' + games[str(guild.id)]['players'][str(player.id)].cards[i][1] + '.png')
                            else:
                                card = Image.open(
                                    'images/' + games[str(guild.id)]['players'][str(player.id)].cards[i][0] + '.png')
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
            p = list(games[str(guild.id)]['players'].keys())

            temp = iter(p)
            for key in temp:
                if key == str(player.id):
                    n = guild.get_member(int(next(temp, next(iter(p)))))
                    break

            message.set_footer(text=n.name + ' is next!')

            try:
                await channel.send(files=[thumbnail, file], embed=message)
            except ClientOSError:
                pass

        await asyncio.gather(
            *[asyncio.create_task(send_cards(x)) for x in guild.text_channels if x.category.name == 'UNO-GAME'])

        games[str(guild.id)]['player'] = player.id

        if player.id == client.user.id:
            await games[str(guild.id)]['players'][str(client.user.id)].play()

    else:
        ending.remove(str(guild.id))

        return


def get_hands(guild, player: discord.Member, n: discord.Member):
    options = []

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

            await display_cards(n)
        select.callback = select_callback

        return select


async def play_card(card, player: discord.Member):
    guild = player.guild
    bot = None

    if player.id == client.user.id:
        bot = games[str(guild.id)]['players'][str(client.user.id)]

    if not games[str(guild.id)]['settings']['Flip']:
        if not bot:
            if '+4' in card:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove('+4')
            elif 'wild' in card:
                games[str(guild.id)]['players'][str(player.id)]['cards'].remove('wild')
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

    games[str(guild.id)]['current'] = card

    if games[str(guild.id)]['settings']['Flip']:
        if not games[str(guild.id)]['dark']:
            color = search(r'red|blue|green|yellow', card[0]).group(0)

            if color == 'red':
                message = discord.Embed(title=player.name + ':', color=discord.Color.red())
            elif color == 'blue':
                message = discord.Embed(title=player.name + ':', color=discord.Color.blue())
            elif color == 'green':
                message = discord.Embed(title=player.name + ':', color=discord.Color.green())
            else:
                message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 255, 0))

        else:
            color = search(r'pink|teal|orange|purple', card[1]).group(0)

            if color == 'pink':
                message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 20, 147))
            elif color == 'teal':
                message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(0, 128, 128))
            elif color == 'orange':
                message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 140, 0))
            else:
                message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(102, 51, 153))

    else:
        color = search(r'red|blue|green|yellow', card).group(0)

        if color == 'red':
            message = discord.Embed(title=player.name + ':', color=discord.Color.red())
        elif color == 'blue':
            message = discord.Embed(title=player.name + ':', color=discord.Color.blue())
        elif color == 'green':
            message = discord.Embed(title=player.name + ':', color=discord.Color.green())
        else:
            message = discord.Embed(title=player.name + ':', color=discord.Color.from_rgb(255, 255, 0))

    if not games[str(guild.id)]['settings']['Flip']:
        image = Image.open('images/' + card + '.png')
    else:
        if not games[str(guild.id)]['dark']:
            image = Image.open('images/' + card[0] + '.png')
        else:
            image = Image.open('images/' + card[1] + '.png')
    refined = image.resize(
        (round(image.size[0] / 6.0123456790123456790123456790123),
         round(image.size[1] / 6.0123456790123456790123456790123)),
        Image.ANTIALIAS)

    async def send_card(channel):
        with BytesIO() as image_binary:
            refined.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='card.png')

        message.set_image(url='attachment://card.png')

        await channel.send(file=file, embed=message)

    await asyncio.gather(
        *[asyncio.create_task(send_card(x)) for x in guild.text_channels if x.category.name == 'UNO-GAME'])

    n = None
    p = list(games[str(guild.id)]['players'].keys())

    temp = iter(p)
    for key in temp:
        if key == str(player.id):
            n = guild.get_member(int(next(temp, next(iter(p)))))
            break

    if player.id != client.user.id and not games[str(guild.id)]['players'][str(player.id)]['cards'] or bot and not bot.cards:
        ending.append(str(guild.id))

        if any('+' in x for x in (card, card[0], card[1])):
            if '4' in card:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 4
                    await draw(n, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, 4)

            elif '2' in card or '2' in card[0] and not games[str(guild.id)]['dark']:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 2
                    await draw(n, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, 2)
            elif '1' in card[0] and not games[str(guild.id)]['dark']:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 1
                    await draw(n, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, 1)
            elif '5' in card[1] and games[str(guild.id)]['dark']:
                if str(guild.id) in stack:
                    stack[str(guild.id)] += 5
                    await draw(n, stack[str(guild.id)])
                    del stack[str(guild.id)]
                else:
                    await draw(n, 5)
            elif 'color' in card[1] and games[str(guild.id)]['dark']:
                await draw(n, 1, False, True)

        await game_shutdown(games[str(guild.id)], player)


class Bot:
    def __init__(self, guild, games, cards):
        self.name = 'UNOBot'
        self.id = client.user.id
        self.guild = guild
        self.channels = self.playables = []
        self.member = guild.get_member(self.id)
        self.games = games
        self.cards = cards
        self.reccount = 0

    def __get_color_and_value(self, card):
        d = self.games[str(self.guild.id)]

        if not d['settings']['Flip']:
            color = search(r'red|blue|green|yellow', card)
            if color:
                color = color.group(0)
            value = search(r'\+[42]|wild|skip|reverse|\d', card).group(0)

        elif not d['dark']:
            color = search(r'red|blue|green|yellow', card[0])
            if color:
                color = color.group(0)
            value = search(r'\+[21]|wild|skip|reverse|flip|\d', card[0]).group(0)

        else:
            color = search(r'pink|teal|orange|purple', card[1])
            if color:
                color = color.group(0)
            value = search(r'\+(5|color)|wild|skip|reverse|flip|\d', card[1]).group(0)

        return color, value

    def __get_color(self, card):
        return self.__get_color_and_value(card)[0]

    def __get_value(self, card):
        return self.__get_color_and_value(card)[1]

    def __get_score(self, value):
        d = self.games[str(self.guild.id)]

        if not d['settings']['Flip']:
            if value in ( 'skip', 'reverse'):
                return 20
            elif value == '+2':
                least = sum(1 for x in self.cards if self.__get_value(x) in ('+2', '+4'))
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != str(self.id)]:
                    total += len(d['players'][player]['cards'])
                    n += 1

                prob = 0
                if n * least <= 12 * (total % 108 + 1):
                    for i in range(n * least):
                        if i <= total:
                            prob += comb(12 * (total % 108 + 1), i) * comb(96 * (total % 108 + 1) - len(self.cards),
                                                       total - i) / comb(
                                108 * (total % 108 + 1) - len(self.cards), total)

                if prob > 0.4:
                    return 20 * prob
                else:
                    return -1
            elif value == 'wild':
                return 0
            elif value == '+4':
                least = sum(1 for x in self.cards if self.__get_value(x) == '+4')
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != str(self.id)]:
                    total += len(d['players'][player]['cards'])
                    n += 1

                prob = 0
                if n * least <= 4 * (total % 108 + 1):
                    for i in range(n * least):
                        prob += comb(4 * (total % 108 + 1), i) * comb(104 * (total % 108 + 1) - len(self.cards),
                                                   total - i) / comb(
                            108 * (total % 108 + 1) - len(self.cards), total)

                if prob > 0.5:
                    return 50 * prob
                else:
                    return -1
            else:
                return int(value)

        elif not d['dark']:
            if value == '+1':
                return 10
            elif value in ('reverse', 'skip'):
                return 20
            elif value in ('wild', 'flip'):
                return 0
            elif value == '+2':
                least = sum(1 for x in self.cards if self.__get_value(x) == '+2')
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != str(self.id)]:
                    total += len(d['players'][player]['cards'])
                    n += 1

                prob = 0
                if n * least <= 4 * (total % 112 + 1):
                    for i in range(n * least):
                        prob += comb(4 * (total % 112 + 1), i) * comb(108 * (total % 112 + 1) - len(self.cards),
                                                   total - i) / comb(
                            112 * (total % 112 + 1) - len(self.cards), total)

                if prob > 0.5:
                    return 50 * prob
                else:
                    return -1
            else:
                return int(value)

        else:
            if value == 'reverse':
                return 20
            elif value == '+5':
                least = sum(1 for x in self.cards if self.__get_value(x) == '+5')
                total = 0
                n = 0
                for player in [x for x in d['players'] if x != str(self.id)]:
                    total += len(d['players'][player]['cards'])
                    n += 1

                prob = 0
                if n * least <= 8 * (total % 112 + 1):
                    for i in range(n * least):
                        prob += comb(8 * (total % 112 + 1), i) * comb(104 * (total % 112 + 1) - len(self.cards),
                                                   total - i) / comb(
                            112 * (total % 112 + 1) - len(self.cards), total)

                if prob > 0.5:
                    return 20 * prob
                else:
                    return -1
            elif value == 'skip':
                return 30
            elif value in ('wild', 'flip', '+color'):
                return 0
            else:
                return int(value)

    def __is_similar(self, x, y):
        return self.__get_color(x) == self.__get_color(y) or self.__get_value(x) == self.__get_value(
            y) or any(t in ('+4', 'wild') or t[0] in ('+2', 'wild') and not
        self.games[str(self.guild.id)]['dark'] or t[1] in ('+color', 'wild') and self.games[str(self.guild.id)]['dark']
                      for t in (x, y))

    def __build_tree(self, tree, root):
        self.reccount += 1

        d = self.games[str(self.guild.id)]

        if not d['settings']['Flip']:
            for card in [x for x in self.cards if not any(x in c for c in tree.rsearch(root)) and self.__is_similar(x, root)]:
                value = self.__get_value(card)
                count = 0

                while True:
                    try:
                        tree.create_node(identifier=card + str(count), tag=str(count), data=self.__get_score(value), parent=root)
                    except DuplicatedNodeIdError:
                        count += 1
                        continue
                    else:
                        break

                if self.reccount <= 1000:
                    self.__build_tree(tree, card + str(count))

        elif not d['dark']:
            rcard = tuple(root.split('|'))

            for card in [x for x in self.cards if not any(x[0] + '|' + x[1] in c for c in tree.rsearch(root)) and self.__is_similar(x, rcard)]:
                value = self.__get_value(card)
                count = 0

                while True:
                    try:
                        tree.create_node(identifier=card[0] + '|' + card[1] + str(count), tag=str(count), data=self.__get_score(value), parent=root)
                    except DuplicatedNodeIdError:
                        count += 1
                        continue
                    else:
                        break

                if self.reccount <= 1000:
                    self.__build_tree(tree, card[0] + '|' + card[1] + str(count))

        else:
            rcard = tuple(root.split('|'))

            for card in [x for x in self.cards if not any(x[0] + '|' + x[1].replace('dark', '') in c for c in tree.rsearch(root)) and self.__is_similar(x, rcard)]:
                value = self.__get_value(card)
                count = 0

                while True:
                    try:
                        tree.create_node(identifier=card[0] + '|' + card[1] + str(count), tag=str(count), data=self.__get_score(value), parent=root)
                    except DuplicatedNodeIdError:
                        count += 1
                        continue
                    else:
                        break

                if self.reccount <= 1000:
                    self.__build_tree(tree, card[0] + '|' + card[1] + str(count))

    async def __execute_card(self, value):
        n = None
        p = list(self.games[str(self.guild.id)]['players'].keys())

        temp = iter(p)
        for key in temp:
            if key == str(self.id):
                n = self.guild.get_member(int(next(temp, next(iter(p)))))
                break

        if value in [str(x) for x in range(10)]:
            if str(self.guild.id) in self.games:
                await display_cards(n)

        elif value == '+4':
            if str(self.guild.id) in self.games:
                if str(self.guild.id) not in stack:
                    stack[str(self.guild.id)] = 4
                else:
                    stack[str(self.guild.id)] += 4

                if self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                        '+4' in card for card in self.games[str(self.guild.id)]['players'][str(n.id)]['cards']):
                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                            stack[str(self.guild.id)]) + ' cards.**',
                        color=discord.Color.red()))) for x in self.channels])

                    await display_cards(n)

                else:
                    await draw(n, stack[str(self.guild.id)])

                    del stack[str(self.guild.id)]

                    m = self.guild.get_member(int(next(temp, next(iter(p)))))
                    if m == n:
                        iterable = iter(p)
                        next(iterable)
                        m = self.guild.get_member(int(next(iterable)))

                    await display_cards(m)

        elif value == 'reverse':
            if str(self.guild.id) in self.games:
                d = self.games[str(self.guild.id)]
                player_ids = list(d['players'].keys())

                if len(player_ids) > 2:
                    player_ids.reverse()

                    ordered_dict = OrderedDict()
                    for x in player_ids:
                        ordered_dict[x] = d['players'][x]

                    d['players'] = dict(ordered_dict)

                    await asyncio.gather(*[asyncio.create_task(x.send(
                        embed=discord.Embed(description='**The player order is reversed.**',
                                            color=discord.Color.red()))) for x in self.channels])

                    p = list(d['players'].keys())
                    m = None
                    temp = iter(p)
                    for key in temp:
                        if key == str(client.user.id):
                            m = self.guild.get_member(int(next(temp, next(iter(p)))))
                            break

                    await display_cards(m)

                else:
                    m = self.guild.get_member(int(next(temp, next(iter(p)))))
                    if m == n:
                        iterable = iter(p)
                        next(iterable)
                        m = self.guild.get_member(int(next(iterable)))

                    await asyncio.gather(*[asyncio.create_task(x.send(
                        embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                            color=discord.Color.red()))) for x in self.channels])

                    await display_cards(m)

        elif value == 'skip':
            if str(self.guild.id) in self.games:
                if not self.games[str(self.guild.id)]['settings']['Flip'] or not self.games[str(self.guild.id)]['dark']:
                    m = self.guild.get_member(int(next(temp, next(iter(p)))))
                    if m == n:
                        iterable = iter(p)
                        next(iterable)
                        m = self.guild.get_member(int(next(iterable)))

                    await asyncio.gather(*[asyncio.create_task(x.send(
                        embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                            color=discord.Color.red()))) for x in
                        self.channels])

                    await display_cards(m)

                else:
                    await asyncio.gather(*[asyncio.create_task(x.send(
                        embed=discord.Embed(description='**Everyone is skipped!**',
                                            color=discord.Color.red()))) for x in
                        self.channels])

                    await display_cards(self.member)

        elif value == 'wild':
            if str(self.guild.id) in self.games:
                await display_cards(n)

        elif value == '+2':
            if str(self.guild.id) in self.games:
                if str(self.guild.id) not in stack:
                    stack[str(self.guild.id)] = 2
                else:
                    stack[str(self.guild.id)] += 2

                if self.games[str(self.guild.id)]['settings']['StackCards'] and (
                        any('+2' in card for card in
                            self.games[str(self.guild.id)]['players'][str(n.id)]['cards']) or any(
                    '+4' in card for card in self.games[str(self.guild.id)]['players'][str(n.id)]['cards'])):
                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                            stack[str(self.guild.id)]) + ' cards.**',
                        color=discord.Color.red()))) for x in
                        self.channels])

                    await display_cards(n)

                else:
                    await draw(n, stack[str(self.guild.id)])

                    del stack[str(self.guild.id)]

                    m = self.guild.get_member(int(next(temp, next(iter(p)))))
                    if m == n:
                        iterable = iter(p)
                        next(iterable)
                        m = self.guild.get_member(int(next(iterable)))

                    await display_cards(m)

            else:
                if not self.games[str(self.guild.id)]['dark']:
                    if str(self.guild.id) in self.games:
                        if str(self.guild.id) not in stack:
                            stack[str(self.guild.id)] = 2
                        else:
                            stack[str(self.guild.id)] += 2

                        if self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                                card[0] == '+2' for card in
                                self.games[str(self.guild.id)]['players'][str(n.id)]['cards']):
                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                    stack[str(self.guild.id)]) + ' cards.**',
                                color=discord.Color.red()))) for x in
                                self.channels])

                            await display_cards(n)

                        else:
                            await draw(n, stack[str(self.guild.id)])

                            del stack[str(self.guild.id)]

                            m = self.guild.get_member(int(next(temp, next(iter(p)))))
                            if m == n:
                                iterable = iter(p)
                                next(iterable)
                                m = self.guild.get_member(int(next(iterable)))
                            await display_cards(m)

        elif value == '+1':
            if self.games[str(self.guild.id)]['settings']['Flip'] and not self.games[str(self.guild.id)][
                'dark']:
                if str(self.guild.id) in self.games:
                    if str(self.guild.id) not in stack:
                        stack[str(self.guild.id)] = 1
                    else:
                        stack[str(self.guild.id)] += 1

                    if self.games[str(self.guild.id)]['settings']['StackCards'] and (
                            any('+1' in card[0] for card in
                                self.games[str(self.guild.id)]['players'][str(n.id)]['cards']) or any(
                        card[0] == '+2' for card in
                        self.games[str(self.guild.id)]['players'][str(n.id)]['cards'])):
                        await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                            description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                stack[str(self.guild.id)]) + ' cards.**',
                            color=discord.Color.red()))) for x in
                            self.channels])

                        await display_cards(n)

                    else:
                        await draw(n, stack[str(self.guild.id)])

                        del stack[str(self.guild.id)]

                        m = self.guild.get_member(int(next(temp, next(iter(p)))))
                        if m == n:
                            iterable = iter(p)
                            next(iterable)
                            m = self.guild.get_member(int(next(iterable)))

                        await display_cards(m)

        elif value == '+5':
            if str(self.guild.id) in self.games:
                if str(self.guild.id) not in stack:
                    stack[str(self.guild.id)] = 5
                else:
                    stack[str(self.guild.id)] += 5

                if self.games[str(self.guild.id)]['settings']['StackCards'] and any(
                        '+5' in card[1] for card in
                        self.games[str(self.guild.id)]['players'][str(n.id)]['cards']):
                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                            stack[str(self.guild.id)]) + ' cards.**',
                        color=discord.Color.red()))) for x in
                        self.channels])

                    await display_cards(n)

                else:
                    await draw(n, stack[str(self.guild.id)])

                    del stack[str(self.guild.id)]

                    m = self.guild.get_member(int(next(temp, next(iter(p)))))
                    if m == n:
                        iterable = iter(p)
                        next(iterable)
                        m = self.guild.get_member(int(next(iterable)))

                    await display_cards(m)

        elif value == '+color':
            if str(self.guild.id) in self.games:
                await draw(n, 1, False, True)

                m = self.guild.get_member(int(next(temp, next(iter(p)))))
                if m == n:
                    iterable = iter(p)
                    next(iterable)
                    m = self.guild.get_member(int(next(iterable)))
                await display_cards(m)

        elif value == 'flip':
            if str(self.guild.id) in self.games:
                self.games[str(self.guild.id)]['dark'] = not self.games[str(self.guild.id)][
                    'dark']
                self.games[str(self.guild.id)]['current'], self.games[str(self.guild.id)]['current_opposite'] = \
                self.games[str(self.guild.id)]['current_opposite'], self.games[str(self.guild.id)]['current']

                await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                    description='**Everything is flipped!**',
                    color=discord.Color.red()))) for x in self.channels])

                await display_cards(n)

    async def play(self):
        d = self.games[str(self.guild.id)]

        if not d['settings']['Flip']:
            if str(self.guild.id) not in stack:
                self.playables = list(set(x for x in self.cards if
                                          self.__is_similar(x, d['current']) or self.__get_value(x) in (
                                              '+4', 'wild')))
            elif '+2' in d['current']:
                self.playables = list(set(x for x in self.cards if self.__get_value(x) in ('+4', '+2')))
            else:
                self.playables = list(set(x for x in self.cards if self.__get_value(x) == '+4'))
            self.playables.sort(key=lambda x: self.__get_score(self.__get_value(x)), reverse=True)
        elif not d['dark']:
            if str(self.guild.id) not in stack:
                self.playables = [x for x in self.cards if
                                          self.__is_similar(x, d['current']) or self.__get_value(x) in (
                                              '+2', 'wild')]
            elif '+1' in d['current']:
                self.playables = list(set(x for x in self.cards if self.__get_value(x) in ('+1', '+2')))
            else:
                self.playables = list(set(x for x in self.cards if self.__get_value(x) == '+2'))
            self.playables.sort(key=lambda x: self.__get_score(self.__get_value(x)), reverse=True)
        else:
            if str(self.guild.id) not in stack:
                self.playables = [x for x in self.cards if
                                          self.__is_similar(x, d['current']) or self.__get_value(x) in (
                                              '+color', 'wild')]
            else:
                self.playables = list(set(x for x in self.cards if self.__get_value(x) == '+5'))
            self.playables.sort(key=lambda x: self.__get_score(self.__get_value(x)), reverse=True)

        n = None
        p = list(self.games[str(self.guild.id)]['players'].keys())

        temp = iter(p)
        for key in temp:
            if key == str(self.id):
                n = self.guild.get_member(int(next(temp, next(iter(p)))))
                break

        if not self.playables:
            if str(self.guild.id) in stack:
                await draw(self.member, stack[str(self.guild.id)])
                del stack[str(self.guild.id)]
            else:
                await draw(self.member, 1)
            await display_cards(n)

        else:
            if not d['settings']['Flip']:
                if len(self.cards) == 1:
                    if self.playables[0] in ('wild', '+4'):
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

                        score = [sum(map(lambda x: tree.get_node(x).data, path)) for path in paths]
                        for c in paths[score.index(max(score))]:
                            if self.__get_color(c):
                                color_change = self.__get_color(c)
                                break

                        optimals.append(max(score))

                    best = self.playables[optimals.index(max(optimals))]
                    if not self.__get_color(best):
                        best = color_change + best

            elif not d['dark']:
                if len(self.cards) == 1:
                    if self.playables[0][0] in ('wild', '+2'):
                        best = ('blue' + self.playables[0][0], self.playables[0][1])
                    else:
                        best = self.playables[0]
                else:
                    color_change = 'blue'
                    optimals = []
                    self.reccount = 0
                    for card in self.playables:
                        tree = Tree()
                        tree.create_node(identifier=card[0] + '|' + card[1], data=self.__get_score(self.__get_value(card)))
                        self.__build_tree(tree, card[0] + '|' + card[1])

                        paths = tree.paths_to_leaves()

                        score = [sum(map(lambda x: tree.get_node(x).data, path)) for path in paths]
                        for c in paths[score.index(max(score))]:
                            if self.__get_color(tuple(c.split('|'))):
                                color_change = self.__get_color(tuple(c.split('|')))
                                break

                        optimals.append(max(score))

                    best = self.playables[optimals.index(max(optimals))]
                    if not self.__get_color(best):
                        best = (color_change + best[0], best[1])

            else:
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
                            tree.create_node(identifier=card[0] + '|' + card[1], data=self.__get_score(self.__get_value(card)))
                            self.__build_tree(tree, card[0] + '|' + card[1])
                        else:
                            tree.create_node(identifier=card[0] + '|wild',
                                             data=self.__get_score(self.__get_value(card)))
                            self.__build_tree(tree, card[0] + '|wild')

                        paths = tree.paths_to_leaves()

                        score = [sum(map(lambda x: tree.get_node(x).data, path)) for path in paths]
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

            if self.__get_score(self.__get_value(best)) >= 0:
                await play_card(best, self.member)
                await self.__execute_card(self.__get_value(best))
            else:
                if str(self.guild.id) in stack:
                    await draw(self.member, stack[str(self.guild.id)])
                else:
                    await draw(self.member, 1)
                await display_cards(n)


@client.event
async def on_ready():
    await initialize()

    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] UNOBot is ready.')


@client.event
async def on_guild_join(guild):
    await initialize()

    print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] UNOBot has joined the guild ' + str(
        guild) + '.')
    await guild.text_channels[0].send(
        f"**Thanks for adding UNOBot!** :thumbsup:\n• `{prefix}` is my prefix.\n• Use `{prefix}commands` for a list of commands.\n• Use `{prefix}help` if you need help.\n• Use `{prefix}guide` for an in-depth guide on me.\n"
    )


@client.event
async def on_guild_remove(guild):
    await initialize()
    print(
        '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] UNOBot has left the guild ' + str(guild) + '.')


@client.event
async def on_member_join(member):
    if not member.bot:
        users_file = s3_resource.Object('unobot-bucket', 'users.json')
        user_stuff = json.loads(users_file.get()['Body'].read().decode('utf-8'))

        if str(member.id) in user_stuff:
            user_stuff[str(member.id)][str(member.guild.id)] = {
                'Score': 0,
                'Played': 0
            }

        else:
            user_stuff[str(member.id)] = {
                "AllowAlerts": True,
                str(member.guild.id): {
                    'Score': 0,
                    'Played': 0
                }}

        users_file.put(Body=json.dumps(user_stuff).encode('utf-8'))


@client.event
async def on_member_remove(member):
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
async def on_message(message):
    global last_run
    timestamp = datetime.now()

    if (timestamp - last_run).total_seconds() >= 0.5:

        if message.content == 'CONFIRM':
            last_run = timestamp

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
                p = list(games[str(message.guild.id)]['players'].keys())

                temp = iter(p)
                for key in temp:
                    if key == str(message.author.id):
                        n = message.guild.get_member(int(next(temp, next(iter(p)))))
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
                    return
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
                elif any(x in color for x in ('d', 'draw')) and int(
                        games[str(message.guild.id)]['player']) == message.author.id:

                    last_run = timestamp

                    overwrite = message.channel.overwrites_for(message.author)
                    overwrite.send_messages = False
                    overwrite.read_messages = True
                    await message.channel.set_permissions(message.author, overwrite=overwrite)

                    if str(message.guild.id) in stack:
                        await draw(message.author, stack[str(message.guild.id)])
                        del stack[str(message.guild.id)]
                    elif games[str(message.guild.id)]['settings']['DrawUntilMatch']:
                        await draw(message.author, 1, True)
                    else:
                        await draw(message.author, 1)

                    await display_cards(n)

                    overwrite.send_messages = True
                    await message.channel.set_permissions(message.author, overwrite=overwrite)

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
                        current_player = message.guild.get_member(int(games[str(message.guild.id)]['player']))

                        if current_player != message.author:
                            users = json.loads(
                                s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                            if users[str(current_player.id)]['AllowAlerts']:
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
                                    embed=discord.Embed(description=':x: The current player has disabled alerts.',
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
                                'images/' + games[str(message.guild.id)]['players'][str(message.author.id)]['cards'][i] + '.png')
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

                if int(games[str(message.guild.id)]['player']) == message.author.id and str(
                        message.guild.id) not in ending:

                    last_run = timestamp

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
                                if color + value in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == value) and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(color + value, message.author)

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
                                                    if player_ids[i] != str(client.user.id) and player_ids[(i + 1) % len(player_ids)] != str(client.user.id):
                                                        games[str(message.guild.id)]['players'][player_ids[(i + 1) % len(player_ids)]][
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

                                                    await display_cards(n)

                                            else:
                                                if str(message.guild.id) in games:
                                                    await display_cards(n)

                                        else:
                                            if str(message.guild.id) in games:
                                                await display_cards(n)

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
                                                         games[str(message.guild.id)]['players'][str(message.author.id)]['cards']]:
                                        if (current_color == color or current_value == value) and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(
                                                choice([x for x in games[str(message.guild.id)]['players'][
                                                    str(message.author.id)]['cards'] if x[0] == color + value]),
                                                message.author)

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
                                                        await display_cards(n)

                                            else:
                                                if str(message.guild.id) in games:
                                                    await display_cards(n)

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
                                                         games[str(message.guild.id)]['players'][str(message.author.id)]['cards']]:
                                        if (current_color == color or current_value == value) and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[1] == color + value]),
                                                            message.author)

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
                                                        await display_cards(n)

                                            else:
                                                if str(message.guild.id) in games:
                                                    await display_cards(n)

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

                        elif search(r'[+d](raw)* *4', value) and not games[str(message.guild.id)]['settings']['Flip']:
                            if '+4' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                await play_card(color + '+4', message.author)

                                if str(message.guild.id) in games:
                                    if str(message.guild.id) not in stack:
                                        stack[str(message.guild.id)] = 4
                                    else:
                                        stack[str(message.guild.id)] += 4

                                    if n.id != client.user.id:
                                        if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                '+4' in card for card in games[str(message.guild.id)]['players'][str(n.id)]['cards']):
                                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                    stack[str(message.guild.id)]) + ' cards.**',
                                                color=discord.Color.red()))) for x in message.channel.category.text_channels])

                                            await display_cards(n)

                                        else:
                                            await draw(n, stack[str(message.guild.id)])

                                            del stack[str(message.guild.id)]

                                            m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = message.guild.get_member(int(next(iterable)))

                                            await display_cards(m)

                                    else:
                                        if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                '+4' in card for card in
                                                games[str(message.guild.id)]['players'][str(n.id)].cards):
                                            await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                description='**UNOBot can choose to stack cards or draw ' + str(
                                                    stack[str(message.guild.id)]) + ' cards.**',
                                                color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])

                                            await display_cards(n)

                                        else:
                                            await draw(n, stack[str(message.guild.id)])

                                            del stack[str(message.guild.id)]

                                            m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = message.guild.get_member(int(next(iterable)))

                                            await display_cards(m)

                            else:
                                await message.channel.send(
                                    embed=discord.Embed(description=':x: **You don\'t have a WildDraw4!**',
                                                        color=discord.Color.red()))

                        elif value in ('reverse', 'r'):
                            if not games[str(message.guild.id)]['settings']['Flip']:
                                if color + 'reverse' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == 'reverse') and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(color + 'reverse', message.author)

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
                                                             games[str(message.guild.id)]['players'][str(message.author.id)][
                                                                 'cards']]:
                                        if (current_color == color or current_value == 'reverse') and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[0] == color + 'reverse']),
                                                            message.author)

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
                                                             games[str(message.guild.id)]['players'][str(message.author.id)][
                                                                 'cards']]:
                                        if (current_color == color or current_value == 'reverse') and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[1] == color + 'reverse']),
                                                            message.author)

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
                                player_ids = list(d['players'].keys())

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

                                    p = list(d['players'].keys())
                                    m = None
                                    temp = iter(p)
                                    for key in temp:
                                        if key == str(message.author.id):
                                            m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                            break

                                    await display_cards(m)

                                else:
                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                    if m == n:
                                        iterable = iter(p)
                                        next(iterable)
                                        m = message.guild.get_member(int(next(iterable)))

                                    await asyncio.gather(*[asyncio.create_task(x.send(
                                        embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                            color=discord.Color.red()))) for x in
                                        message.channel.category.text_channels])

                                    await display_cards(m)

                        elif value in ('skip', 's'):
                            if not games[str(message.guild.id)]['settings']['Flip']:
                                if color + 'skip' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == 'skip') and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(color + 'skip', message.author)

                                        if str(message.guild.id) in games:
                                            m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = message.guild.get_member(int(next(iterable)))

                                            await asyncio.gather(*[asyncio.create_task(x.send(
                                                embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                                    color=discord.Color.red()))) for x in
                                                message.channel.category.text_channels])

                                            await display_cards(m)

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
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[0] == color + 'skip']),
                                                            message.author)

                                            if str(message.guild.id) in games:
                                                m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                if m == n:
                                                    iterable = iter(p)
                                                    next(iterable)
                                                    m = message.guild.get_member(int(next(iterable)))

                                                await asyncio.gather(*[asyncio.create_task(x.send(
                                                    embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                                        color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])

                                                await display_cards(m)

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
                                                            message.author)

                                            if str(message.guild.id) in games:
                                                await asyncio.gather(*[asyncio.create_task(x.send(
                                                    embed=discord.Embed(description='**Everyone is skipped!**',
                                                                        color=discord.Color.red()))) for x in
                                                    message.channel.category.text_channels])

                                                await display_cards(message.author)

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
                                    if not ('+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(color + 'wild', message.author)

                                        if str(message.guild.id) in games:
                                            await display_cards(n)

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
                                                    (color + 'wild', choice([x for x in games[str(message.guild.id)]['players'][
                                                        str(message.author.id)]['cards'] if x[0] == 'wild'])[1]),
                                                    message.author)

                                                if str(message.guild.id) in games:
                                                    await display_cards(n)

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
                                                    message.author)

                                                if str(message.guild.id) in games:
                                                    await display_cards(n)

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

                        elif search(r'[+d](raw)* *2', value):
                            if not games[str(message.guild.id)]['settings']['Flip']:
                                if color + '+2' in games[str(message.guild.id)]['players'][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == '+2') and not (
                                            current_value == '+4' and str(message.guild.id) in stack):
                                        await play_card(color + '+2', message.author)

                                        if str(message.guild.id) in games:
                                            if str(message.guild.id) not in stack:
                                                stack[str(message.guild.id)] = 2
                                            else:
                                                stack[str(message.guild.id)] += 2

                                            if n.id != client.user.id:
                                                if games[str(message.guild.id)]['settings']['StackCards'] and (
                                                        any('+2' in card for card in
                                                            games[str(message.guild.id)]['players'][str(n.id)]['cards']) or any(
                                                    '+4' in card for card in games[str(message.guild.id)]['players'][str(n.id)]['cards'])):
                                                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                    await display_cards(n)

                                                else:
                                                    await draw(n, stack[str(message.guild.id)])

                                                    del stack[str(message.guild.id)]

                                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                    if m == n:
                                                        iterable = iter(p)
                                                        next(iterable)
                                                        m = message.guild.get_member(int(next(iterable)))

                                                    await display_cards(m)

                                            else:
                                                if games[str(message.guild.id)]['settings']['StackCards'] and (
                                                        any('+2' in card for card in
                                                            games[str(message.guild.id)]['players'][str(n.id)].cards) or any(
                                                    '+4' in card for card in
                                                    games[str(message.guild.id)]['players'][str(n.id)].cards)):
                                                    await asyncio.gather(
                                                        *[asyncio.create_task(x.send(embed=discord.Embed(
                                                            description='**UNOBot can choose to stack cards or draw ' + str(
                                                                stack[str(message.guild.id)]) + ' cards.**',
                                                            color=discord.Color.red()))) for x in
                                                            message.channel.category.text_channels])

                                                    await display_cards(n)

                                                else:
                                                    await draw(n, stack[str(message.guild.id)])

                                                    del stack[str(message.guild.id)]

                                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                    if m == n:
                                                        iterable = iter(p)
                                                        next(iterable)
                                                        m = message.guild.get_member(int(next(iterable)))

                                                    await display_cards(m)

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
                                                    1]), message.author)

                                            if str(message.guild.id) in games:
                                                if str(message.guild.id) not in stack:
                                                    stack[str(message.guild.id)] = 2
                                                else:
                                                    stack[str(message.guild.id)] += 2

                                                if n.id != client.user.id:
                                                    if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                            card[0] == '+2' for card in
                                                            games[str(message.guild.id)]['players'][str(n.id)][
                                                                'cards']):
                                                        await asyncio.gather(
                                                            *[asyncio.create_task(x.send(embed=discord.Embed(
                                                                description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                                    stack[str(message.guild.id)]) + ' cards.**',
                                                                color=discord.Color.red()))) for x in
                                                                message.channel.category.text_channels])

                                                        await display_cards(n)

                                                    else:
                                                        await draw(n, stack[str(message.guild.id)])

                                                        del stack[str(message.guild.id)]

                                                        m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                        if m == n:
                                                            iterable = iter(p)
                                                            next(iterable)
                                                            m = message.guild.get_member(int(next(iterable)))

                                                        await display_cards(m)

                                                else:
                                                    if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                            card[0] == '+2' for card in
                                                            games[str(message.guild.id)]['players'][
                                                                str(n.id)].cards):
                                                        await asyncio.gather(
                                                            *[asyncio.create_task(x.send(embed=discord.Embed(
                                                                description='**UNOBot can choose to stack cards or draw ' + str(
                                                                    stack[str(message.guild.id)]) + ' cards.**',
                                                                color=discord.Color.red()))) for x in
                                                                message.channel.category.text_channels])

                                                        await display_cards(n)

                                                    else:
                                                        await draw(n, stack[str(message.guild.id)])

                                                        del stack[str(message.guild.id)]

                                                        m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                        if m == n:
                                                            iterable = iter(p)
                                                            next(iterable)
                                                            m = message.guild.get_member(int(next(iterable)))

                                                        await display_cards(m)

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
                                            str(message.author.id)]['cards'] if x[0] == color + '+1']), message.author)

                                        if str(message.guild.id) in games:
                                            if str(message.guild.id) not in stack:
                                                stack[str(message.guild.id)] = 1
                                            else:
                                                stack[str(message.guild.id)] += 1

                                            if n.id != client.user.id:
                                                if games[str(message.guild.id)]['settings']['StackCards'] and (
                                                        any('+1' in card[0] for card in
                                                            games[str(message.guild.id)]['players'][str(n.id)]['cards']) or any(
                                                    card[0] == '+2' for card in
                                                    games[str(message.guild.id)]['players'][str(n.id)]['cards'])):
                                                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                    await display_cards(n)

                                                else:
                                                    await draw(n, stack[str(message.guild.id)])

                                                    del stack[str(message.guild.id)]

                                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                    if m == n:
                                                        iterable = iter(p)
                                                        next(iterable)
                                                        m = message.guild.get_member(int(next(iterable)))

                                                    await display_cards(m)

                                            else:
                                                if games[str(message.guild.id)]['settings']['StackCards'] and (
                                                        any('+1' in card[0] for card in
                                                            games[str(message.guild.id)]['players'][str(n.id)].cards) or any(
                                                    card[0] == '+2' for card in
                                                    games[str(message.guild.id)]['players'][str(n.id)].cards)):
                                                    await asyncio.gather(
                                                        *[asyncio.create_task(x.send(embed=discord.Embed(
                                                            description='**UNOBot can choose to stack cards or draw ' + str(
                                                                stack[str(message.guild.id)]) + ' cards.**',
                                                            color=discord.Color.red()))) for x in
                                                            message.channel.category.text_channels])

                                                    await display_cards(n)

                                                else:
                                                    await draw(n, stack[str(message.guild.id)])

                                                    del stack[str(message.guild.id)]

                                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                    if m == n:
                                                        iterable = iter(p)
                                                        next(iterable)
                                                        m = message.guild.get_member(int(next(iterable)))

                                                    await display_cards(m)

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
                                            str(message.author.id)]['cards'] if x[1] == color + '+5']), message.author)

                                        if str(message.guild.id) in games:
                                            if str(message.guild.id) not in stack:
                                                stack[str(message.guild.id)] = 5
                                            else:
                                                stack[str(message.guild.id)] += 5

                                            if n.id != client.user.id:
                                                if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                        '+5' in card[1] for card in
                                                        games[str(message.guild.id)]['players'][str(n.id)]['cards']):
                                                    await asyncio.gather(*[asyncio.create_task(x.send(embed=discord.Embed(
                                                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))) for x in
                                                        message.channel.category.text_channels])

                                                    await display_cards(n)

                                                else:
                                                    await draw(n, stack[str(message.guild.id)])

                                                    del stack[str(message.guild.id)]

                                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                    if m == n:
                                                        iterable = iter(p)
                                                        next(iterable)
                                                        m = message.guild.get_member(int(next(iterable)))

                                                    await display_cards(m)

                                            else:
                                                if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                        '+5' in card[1] for card in
                                                        games[str(message.guild.id)]['players'][str(n.id)].cards):
                                                    await asyncio.gather(
                                                        *[asyncio.create_task(x.send(embed=discord.Embed(
                                                            description='**UNOBot can choose to stack cards or draw ' + str(
                                                                stack[str(message.guild.id)]) + ' cards.**',
                                                            color=discord.Color.red()))) for x in
                                                            message.channel.category.text_channels])

                                                    await display_cards(n)

                                                else:
                                                    await draw(n, stack[str(message.guild.id)])

                                                    del stack[str(message.guild.id)]

                                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                                    if m == n:
                                                        iterable = iter(p)
                                                        next(iterable)
                                                        m = message.guild.get_member(int(next(iterable)))

                                                    await display_cards(m)

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
                                'dark'] or not (
                                    '+' in current_value and games[str(message.guild.id)]['settings'][
                                'StackCards'] and str(message.guild.id) in stack):
                                if any('+color' in x[1] for x in
                                       games[str(message.guild.id)]['players'][str(message.author.id)]['cards']):
                                    await play_card((choice([x for x in games[str(message.guild.id)]['players'][
                                        str(message.author.id)]['cards'] if x[1] == '+color'])[
                                                         0], color + '+color'), message.author)

                                    if str(message.guild.id) in games:
                                        await draw(n, 1, False, True)

                                        m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                        if m == n:
                                            iterable = iter(p)
                                            next(iterable)
                                            m = message.guild.get_member(int(next(iterable)))
                                        await display_cards(m)

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
                            if games[str(message.guild.id)]['settings']['Flip']:
                                if not games[str(message.guild.id)]['dark']:
                                    if color + 'flip' in [x[0] for x in
                                                          games[str(message.guild.id)]['players'][str(message.author.id)][
                                                              'cards']]:
                                        if color == current_color or current_value == 'flip':
                                            c = choice([x for x in games[str(message.guild.id)]['players'][
                                                str(message.author.id)]['cards'] if x[0] == color + 'flip'])

                                            await play_card(c, message.author)

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

                                                await display_cards(n)

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

                                            await play_card(c, message.author)

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

                                                await display_cards(n)

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

            except KeyError:
                pass

        else:
            await client.process_commands(message)


@client.slash_command(name='u-help', description='Shows the command usage, an in-depth guide on using UNOBot and a link to the rules of UNO.')
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
        message.add_field(name=prefix + 'startgame', value='Starts a game of UNO.\n' + chr(173))
        message.add_field(name=prefix + 'endgame', value='Ends the ongoing UNO game.\n' + chr(173))
        message.add_field(name=prefix + 'leavegame', value='Lets you leave the UNO game.\n' + chr(173))
        message.add_field(name=prefix + 'kick', value='Kicks a player from an UNO game.\n' + chr(173))
        message.add_field(name=prefix + 'spectate', value='Spectate games of UNO.\n' + chr(173))
        message.add_field(name=prefix + 'stats',
                          value='Gives you a user\'s stats from this Discord server.\n' + chr(173))
        message.add_field(name=prefix + 'globalstats', value='Gives you a user\'s stats from all servers.\n' + chr(173))
        message.add_field(name=prefix + 'leaderboard',
                          value='Gives you a leaderboard only from this Discord server.\n' + chr(173))
        message.add_field(name=prefix + 'globalleaderboard',
                          value='Gives you a leaderboard for all servers.\n' + chr(173))
        message.add_field(name=prefix + 'allowalerts', value='Allows alerts just for you.\n' + chr(173))
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

        elif command == 'alerts':
            message = discord.Embed(title=prefix + 'alerts', color=discord.Color.red())
            message.add_field(name='Description:', value='Allows alerts just for you.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'alerts <on|off|view>`', inline=False)
            message.add_field(name='Examples:', value='• `' + prefix + 'aa on`')

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


@client.slash_command(name='u-stats', description='Gives you a user\'s or your (if no user is specified) UNO stats in the current Discord server.')
@has_permissions(read_messages=True)
async def stats(ctx, user: Option(discord.User, 'The user whose local stats you wish to see', required=False, default='')):
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
                    if round(dict["Score"] / dict["Played"], 2) == 1:
                        message.add_field(name='Average score per game', value='**1** pt')
                    else:
                        message.add_field(name='Average score per game',
                                          value=f'**{round(dict["Score"] / dict["Played"], 2)}** pts')
                    message.add_field(name='Win Percentage',
                                      value='Won **' + str(
                                          round(dict['Wins'] / dict['Played'] * 100)) + '%** of games',
                                      inline=False)
                    if dict['Played'] == 1:
                        message.add_field(name='Total Games', value='**1 game played',
                                          inline=False)
                    else:
                        message.add_field(name='Total Games', value='**' + str(dict['Played']) + '** games played',
                                          inline=False)
                    if dict['Wins'] == 1:
                        message.add_field(name='Total Wins', value='**1 game won',
                                          inline=False)
                    else:
                        message.add_field(name='Total Wins', value='**' + str(dict['Wins']) + '** games won', inline=False)

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


@client.slash_command(name='u-gstats', description='Gives you a user\'s or your (if no user is specified) global stats.')
@has_permissions(read_messages=True)
async def globalstats(ctx, user: Option(discord.User, 'The user whose global stats you wish to see', required=False, default='')):
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
                    if round(s / p, 2) == 1:
                        message.add_field(name='Average score per game', value='**1** pts')
                    else:
                        message.add_field(name='Average score per game',
                                      value=f'**{round(s / p, 2)}** pts')
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
                message = discord.Embed(title=ctx.guild.name + '\'s Leaderboard', color=discord.Color.red(),
                                        description='The top UNO players in your Discord server.')

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

                message = discord.Embed(title='Global Leaderboard', color=discord.Color.red(),
                                        description='The top UNO players from all Discord servers.')

                leaderboard = rank()
                count = 0

                for i in range(1, len(leaderboard) + 1):
                    for index in list_duplicates_of(leaderboard, i):
                        user = client.get_user(int(list(users.keys())[index]))
                        p = 0

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


@client.slash_command(name='u-alerts', description='Turns your alerts on or off.')
@has_permissions(read_messages=True)
async def allowalerts(ctx, option: Option(str, 'on, off, or view', required=True)):
    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'allowalerts' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['allowalerts']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['allowalerts']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['allowalerts']['Blacklist'])
                or ctx.author.id not in commands[str(ctx.guild.id)]['allowalerts']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['allowalerts']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['allowalerts']['Whitelist'] and ctx.author.id in
                         commands[str(ctx.guild.id)]['allowalerts'][
                             'Whitelist']) or ctx.author == ctx.guild.owner:
                users_file = s3_resource.Object('unobot-bucket', 'users.json')
                users = json.loads(users_file.get()['Body'].read().decode('utf-8'))

                if option in ('view', 'list'):
                    if users[str(ctx.author.id)]['AllowAlerts']:
                        description = 'Enabled :white_check_mark:'
                    else:
                        description = 'Disabled :x:'

                    await ctx.respond(embed=discord.Embed(title=ctx.author.name + '\'s alerts', description=description,
                                            color=discord.Color.red()))

                elif option.lower() == 'on':
                    users[str(ctx.author.id)]['AllowAlerts'] = True

                    users_file.put(Body=json.dumps(users).encode('utf-8'))

                    await ctx.respond(embed=discord.Embed(description=':thumbsup: **Your alerts have been enabled.**',
                                            color=discord.Color.red()))

                elif option.lower() == 'off':
                    users[str(ctx.author.id)]['AllowAlerts'] = False

                    users_file.put(Body=json.dumps(users).encode('utf-8'))

                    await ctx.respond(embed=discord.Embed(description=':thumbsup: **Your alerts have been disabled.**',
                                                          color=discord.Color.red()))

                if commands[str(ctx.guild.id)]['allowalerts']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('allowalerts')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting',
                                   prefix + 'stng') \
                               and message.content.split()[1].lower() == 'commands' \
                               and message.content.split()[2].lower() == 'allowalerts' \
                               and message.content.split()[3].lower() == 'cooldown' \
                               and message.content.split()[4].lower() == 'set'

                    try:
                        m = await client.wait_for('message', check=check,
                                                  timeout=float(commands[str(ctx.guild.id)]['allowalerts']['Cooldown']))
                        await client.process_commands(m)
                        cooldowns[str(ctx.guild.id)].remove('allowalerts')

                    except asyncio.TimeoutError:
                        cooldowns[str(ctx.guild.id)].remove('allowalerts')

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
            commands[str(ctx.guild.id)]['options']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.slash_command(name='u-settings', description='Allows you to change the settings of UNOBot.')
@has_permissions(read_messages=True)
async def settings(ctx, setting: Option(str, 'The setting you wish to change'), *, args: Option(str, 'some arguments', required=False, default='')):

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

                        bot = False

                        if args:
                            a = args.split()
                            for i in range(len(a)):
                                user_converter = UserConverter()

                                try:
                                    user = await user_converter.convert(ctx, a[i])

                                    if user != client.user:
                                        for guild in client.guilds:
                                            user_options[str(user.id)].pop(str(guild.id), None)
                                        games[str(ctx.guild.id)]['players'][str(user.id)] = user_options[str(user.id)]
                                        games[str(ctx.guild.id)]['players'][str(user.id)]['cards'] = []
                                    else:
                                        bot = True

                                except BadArgument:
                                    if a[i] in (
                                            'DrawUntilMatch', 'DisableJoin', 'QuickStart', 'SpectateGame', 'StackCards',
                                            'Flip'):
                                        games[str(ctx.guild.id)]['settings'][a[i]] = True

                                    elif a[i] == '7-0':
                                        bot = False
                                        games[str(ctx.guild.id)]['settings'][a[i]] = True

                                    elif a[i] == 'StartingCards':
                                        continue

                                    elif a[i] == 'set':
                                        if a[i - 1] == 'StartingCards':
                                            try:
                                                if 3 < int(a[i + 1]) < 15:
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

                        if not games[str(ctx.guild.id)]['settings']['QuickStart']:
                            if not games[str(ctx.guild.id)]['settings']['Flip']:
                                message = discord.Embed(title='A game of UNO is going to start!',
                                                        description='Less than 30 seconds left!',
                                                        color=discord.Color.red())
                            else:
                                message = discord.Embed(title='A game of UNO is going to start!',
                                                        description='Less than 30 seconds left!',
                                                        color=discord.Color.from_rgb(102, 51, 153))

                            if len(games[str(ctx.guild.id)]['players'].keys()) < 1:
                                if bot:
                                    message.add_field(name='Players:', value=':small_blue_diamond: UNOBot\n', inline=False)
                                else:
                                    message.add_field(name='Players:', value='None', inline=False)
                            else:
                                p = ""
                                for key in games[str(ctx.guild.id)]['players']:
                                    p += (':small_blue_diamond: ' + client.get_user(int(key)).name + '\n')
                                if bot:
                                    p += ':small_blue_diamond: UNOBot\n'

                                message.add_field(name='Players:', value=p, inline=False)

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
                                message = interaction.message
                                guild = interaction.guild
                                user = interaction.user

                                message_dict = message.embeds[0].to_dict()

                                if str(user.id) not in games[str(guild.id)]['players']:

                                    for g in client.guilds:
                                        user_options[str(user.id)].pop(str(g.id), None)

                                    games[str(guild.id)]['players'][str(user.id)] = user_options[
                                        str(user.id)]
                                    games[str(guild.id)]['players'][str(user.id)]['cards'] = []

                                    if len(games[str(guild.id)]['players'].keys()) > 0:
                                        for field in message_dict['fields']:
                                            if field['name'] == 'Players:':
                                                if bot:
                                                    value = ':small_blue_diamond: UNOBot\n'
                                                else:
                                                    value = ''

                                                for key in games[str(guild.id)]['players']:
                                                    value += (':small_blue_diamond: ' + guild.get_member(
                                                        int(key)).name + '\n')

                                                field['value'] = value

                                                break

                                    await interaction.message.edit(embed=discord.Embed.from_dict(message_dict))

                                else:

                                    if str(guild.id) in games and 'current' not in games[str(guild.id)]:
                                        message_dict = message.embeds[0].to_dict()

                                        del games[str(guild.id)]['players'][str(user.id)]

                                        if len(games[str(guild.id)]['players'].keys()) >= 0:
                                            for field in message_dict['fields']:
                                                if field['name'] == 'Players:':
                                                    if len(games[str(guild.id)]['players'].keys()) == 0:
                                                        field['value'] = 'None'
                                                    else:
                                                        value = ''
                                                        for key in games[str(guild.id)]['players']:
                                                            value += (':small_blue_diamond: ' + guild.get_member(
                                                                int(key)).name + '\n')

                                                        field['value'] = value

                                                    break

                                        await message.edit(embed=discord.Embed.from_dict(message_dict))
                            join.callback = join_callback

                            start = Button(label='Start now!', style=discord.ButtonStyle.blurple, emoji='▶️')
                            async def start_callback(interaction):
                                await interaction.response.defer()

                                if interaction.user == interaction.guild.owner or str(interaction.user) == str(
                                        interaction.guild.get_member(games[str(interaction.guild.id)]['creator'])):
                                    n = len(games[str(interaction.guild.id)]['players'].keys())
                                    if bot:
                                        n += 1

                                    if n > 1:
                                        await interaction.message.edit(view=None)

                                        message_dict = interaction.message.embeds[0].to_dict()

                                        games[str(interaction.guild.id)]['seconds'] = -2
                                        games[str(interaction.guild.id)]['creator'] = interaction.user.id

                                        message_dict['title'] = 'A game of UNO has started!'
                                        message_dict[
                                            'description'] = ':white_check_mark: A game of UNO has started. Go to your UNO channel titled with your username.'

                                        try:
                                            await interaction.message.edit(embed=discord.Embed.from_dict(message_dict), view=None)

                                            await game_setup(await client.get_context(interaction.message),
                                                             games[str(interaction.guild.id)], bot)
                                        except discord.errors.NotFound:
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
                                    elif str(interaction.user) == interaction.message.embeds[0].to_dict()['fields'][2]['value']:
                                        message_dict['description'] = ':x: The game creator cancelled the game.'

                                    await interaction.message.edit(embed=discord.Embed.from_dict(message_dict))

                                    try:
                                        del games[str(interaction.guild.id)]
                                    except ValueError:
                                        pass

                                    print('[' + datetime.now().strftime(
                                        '%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game is cancelled in ' + str(interaction.guild) + '.')
                            cancel.callback = cancel_callback

                            view = View()
                            view.add_item(join)
                            view.add_item(start)
                            view.add_item(cancel)

                            response = await ctx.respond(embed=message, view=view)
                            e = await response.original_message()
                            eid = e.id

                            while True:
                                if str(ctx.guild.id) not in games or games[str(ctx.guild.id)]['seconds'] == -2:
                                    break

                                if games[str(ctx.guild.id)]['seconds'] == -1:
                                    del games[str(ctx.guild.id)]

                                    break

                                games[str(ctx.guild.id)]['seconds'] -= 10
                                m = (await ctx.fetch_message(eid)).embeds[0]

                                if games[str(ctx.guild.id)]['seconds'] == 0:
                                    await e.edit(view=None)

                                    n = len(games[str(ctx.guild.id)]['players'].keys())
                                    if bot:
                                        n += 1
                                    if n > 1:
                                        message_dict = m.to_dict()
                                        message_dict['title'] = 'A game of UNO has started!'
                                        message_dict[
                                            'description'] = ':white_check_mark: A game of UNO has started. Go to your UNO channel titled with your username.'

                                        await e.edit(embed=discord.Embed.from_dict(message_dict))

                                        await game_setup(ctx, games[str(ctx.guild.id)], bot)

                                    else:
                                        message_dict = m.to_dict()
                                        message_dict['title'] = 'A game of UNO failed to start!'
                                        message_dict[
                                            'description'] = ':x: Not enough players! At least 2 players are needed (Bots do not count).'

                                        del games[str(ctx.guild.id)]

                                        await e.edit(embed=discord.Embed.from_dict(message_dict), view=None)

                                        print('[' + datetime.now().strftime(
                                            '%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game failed to start in ' + str(
                                            ctx.guild) + '.')

                                    break

                                message_dict = m.to_dict()
                                message_dict['description'] = 'Less than ' + str(
                                    games[str(ctx.guild.id)]['seconds']) + ' seconds left!'

                                await e.edit(embed=discord.Embed.from_dict(message_dict))
                                await asyncio.sleep(10)

                        else:
                            if len(games[str(ctx.guild.id)]['players']) > 1:
                                m = discord.Embed(title='A game of UNO has started!',
                                                        description=':white_check_mark: A game of UNO has started. Go to your UNO channel titled with your username.',
                                                        color=discord.Color.red())

                                p = ""
                                for key in games[str(ctx.guild.id)]['players']:
                                    p += (':small_blue_diamond: ' + (client.get_user(int(key))).name + "\n")
                                if bot:
                                    p += ':small_blue_diamond: UNOBot\n'

                                m.add_field(name='Players:', value=p, inline=False)

                                s = ""
                                for setting in games[str(ctx.guild.id)]['settings']:
                                    if setting == 'StartingCards':
                                        if games[str(ctx.guild.id)]['settings']['StartingCards'] != 7:
                                            s += ('• ' + setting + "\n")
                                    elif games[str(ctx.guild.id)]['settings'][setting]:
                                        s += ('• ' + setting + "\n")

                                if s:
                                    m.add_field(name='Game Settings:', value=s, inline=False)
                                else:
                                    m.add_field(name='Game Settings:', value='None', inline=False)

                                m.add_field(name='Game Creator:', value=str(ctx.author), inline=False)

                                await ctx.respond(embed=m)

                                await game_setup(ctx, games[str(ctx.guild.id)], bot)

                            else:
                                message = discord.Embed(title='A game of UNO failed to start!',
                                                        description=':x: Not enough players! At least 2 players are needed (Bots do not count).',
                                                        color=discord.Color.red())

                                if not games[str(ctx.guild.id)]['players']:
                                    message.add_field(name='Players:', value='None', inline=False)
                                else:
                                    p = ""
                                    for key in games[str(ctx.guild.id)]['players']:
                                        p += (str(await client.fetch_user(int(key))) + "\n")
                                    if bot:
                                        p += ':small_blue_diamond: UNOBot\n'

                                    message.add_field(name='Players:', value=p, inline=False)

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

                                await ctx.respond(embed=message)

                                del games[str(ctx.guild.id)]

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
            await ctx.respond(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
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
                        await game_shutdown(games[str(ctx.guild.id)], None, ctx.guild)

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
                if ctx.channel.category.name == 'UNO-GAME':
                    if str(ctx.guild.id) in games and str(ctx.author.id) in games[str(ctx.guild.id)]:
                        n = None
                        p = list(games[str(ctx.guild.id)]['players'].keys())

                        temp = iter(p)
                        for key in temp:
                            if key == str(ctx.author.id):
                                n = ctx.guild.get_member(int(next(temp, next(iter(p)))))
                                break

                        del games[str(ctx.guild.id)][str(ctx.author.id)]

                        if len(games[str(ctx.guild.id)]) - 6 >= 2:
                            await ctx.channel.delete()

                            await asyncio.gather(*[asyncio.create_task(x.send(
                                discord.Embed(description=':warning: **' + ctx.author.name + '** left.'))) for x
                                in ctx.message.category.text_channels])

                            if ctx.author.id == games[str(ctx.guild.id)]['player']:
                                await display_cards(n)

                        else:
                            await asyncio.gather(*[asyncio.create_task(x.send(
                                embed=discord.Embed(
                                    description=':x: Since not enough players are left, ending game...',
                                    color=discord.Color.red()))) for x in ctx.channel.category.text_channels])

                            ending.append(str(ctx.guild.id))
                            await game_shutdown(games[str(ctx.guild.id)], None, ctx.guild)

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
                    n = None
                    p = list(games[str(ctx.guild.id)]['players'].keys())

                    temp = iter(p)
                    for key in temp:
                        if key == str(player.id):
                            n = ctx.guild.get_member(int(next(temp, next(iter(p)))))
                            break

                    del games[str(ctx.guild.id)]['players'][str(player.id)]

                    if len(games[str(ctx.guild.id)]['players']) >= 2:
                        if player.id != client.user.id:
                            await discord.utils.get(ctx.guild.text_channels,
                                                    name=sub(r'[^\w -]', '',
                                                             player.name.lower().replace(' ',
                                                                                         '-')) + '-uno-channel').delete()

                            await asyncio.gather(*[asyncio.create_task(x.send(
                                discord.Embed(description=':warning: **' + player.name + '** was kicked.'))) for x in
                                ctx.guild.text_channels if x.category.name == 'UNO-GAME'])

                        else:
                            await asyncio.gather(*[asyncio.create_task(x.send(
                                discord.Embed(description=':warning: **UNOBot** was kicked.'))) for x in
                                ctx.guild.text_channels if x.category.name == 'UNO-GAME'])

                        if player.id == games[str(ctx.guild.id)]['player']:
                            await display_cards(n)

                    else:
                        for channel in [x for x in ctx.guild.text_channels if x.category.name == 'UNO-GAME']:
                            await channel.send(
                                embed=discord.Embed(description=':x: Since not enough players are left, ending game...',
                                                    color=discord.Color.red()))

                        ending.append(str(ctx.guild.id))

                        await game_shutdown(games[str(ctx.guild.id)], None, ctx.guild)

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
                        description=':thumbsup: You now have the **UNO Spectator** role. You can now spectate any UNO game with the **SpectateGame** setting on.',
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