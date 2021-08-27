import asyncio
import discord
import json
import boto3
from os import getenv
from botocore.exceptions import ClientError
from scipy.stats import rankdata
from copy import deepcopy
from discord.ext import commands
from collections import OrderedDict
from PIL import Image
from io import BytesIO
from datetime import datetime
from random import sample, choice
from re import search, sub, I
from discord.ext.commands import UserConverter, RoleConverter, BadArgument


prefix = '/u.'
intents = discord.Intents.default()
intents.members, intents.messages, intents.reactions = True, True, True
client = commands.Bot(command_prefix=prefix, intents=intents)
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
s3_client = boto3.client('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))
s3_resource = boto3.resource('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))


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
                        'Played': 0
                    }
                user_stuff[str(member.id)] = default_user_stuff

        else:
            for member in [x for x in client.get_all_members() if str(x.id) not in user_stuff and x.id != client.user.id and not x.bot]:
                for guild in [x for x in client.guilds if x.get_member(member.id)]:
                    user_stuff[str(member.id)] = {"AllowAlerts": True}
                    user_stuff[str(member.id)][str(guild.id)] = {
                        'Wins': 0,
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

    await client.change_presence(activity=discord.Game(name='UNO | Use /u.help'))


def rank(is_global, leaderboardreq, user=None, guild=None):

    wins = []
    users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

    if not is_global and guild:
        for id in [x for x in list(users.keys()) if guild.get_member(int(x))]:
            wins.append(users[id][str(guild.id)]['Wins'])

    else:
        w = 0
        for id in users:
            for g in [x for x in client.guilds if x.get_member(int(id))]:
                w += users[id][str(g.id)]['Wins']
            wins.append(w)
            w = 0

    leaderboard = len(wins) - rankdata(wins, method='max') + 1
    if not leaderboardreq and user:
        return round(leaderboard[list(users.keys()).index(str(user.id))]), len(leaderboard)
    else:
        return [round(x) for x in leaderboard]


def has_played(user):

    for guild in [x for x in client.guilds if x.get_member(user.id)]:
        if json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))[str(user.id)][str(guild.id)]['Played'] > 0:
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

    await ctx.send(embed=message)


async def game_setup(ctx, d):

    guild = ctx.guild
    player_ids = list(d.keys())

    player_ids.remove('settings')
    player_ids.remove('seconds')

    flip = games[str(guild.id)]['settings']['Flip']

    category = await guild.create_category('UNO-GAME')

    for id in player_ids:
        player = guild.get_member(int(id))
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            player: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await category.create_text_channel(player.name.replace(' ', '-').replace('.', '') + '-UNO-Channel',
                                                     overwrites=overwrites)

        await channel.send(content='**Welcome, ' + player.mention + '! This is your UNO channel!**\n'
                                                                    'Strategize, play your cards, unleash your wrath by drawing the feces out of people, and have fun with the game of UNO right here!\n\n'
                                                                    '• Use `p/play <card_color> <card_value>` to play a card.\n'
                                                                    '• Use `c/card(s)` to see your cards at anytime.\n'
                                                                    '• Use `d/draw` to draw a card.\n'
                                                                    '• Use `s/say <message>` to send a message to all players in their UNO channels.\n'
                                                                    '• Use `a/alert` to alert the player who is playing a card.')

    if d['settings']['SpectateGame']:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.roles, name='UNO Spectator'): discord.PermissionOverwrite(read_messages=True)
        }
        await category.create_text_channel('Spectator-UNO-Channel', overwrites=overwrites)

    order = sample(player_ids, len(player_ids))
    ordered_dict = OrderedDict()
    ordered_dict['settings'], ordered_dict['seconds'] = d['settings'], d['seconds']
    for x in order:
        ordered_dict[x] = d[x]

    games[str(guild.id)] = dict(ordered_dict)
    if games[str(guild.id)]['settings']['Flip']:
        games[str(guild.id)]['cards'] = flip_cards
    else:
        games[str(guild.id)]['cards'] = cards

    for id in player_ids:
        while len(games[str(guild.id)]['cards']) <= games[str(guild.id)]['settings']['StartingCards']:
            if flip:
                games[str(guild.id)]['cards'] += flip_cards
            else:
                games[str(guild.id)]['cards'] += cards

        hand = sample(games[str(guild.id)]['cards'], games[str(guild.id)]['settings']['StartingCards'])
        games[str(guild.id)][id]['cards'] = hand
        games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if card not in hand]

        m = discord.Embed(title='Your cards:', color=discord.Color.red())

        image = Image.new('RGBA', (
            len(games[str(guild.id)][id]['cards']) * (
                round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
            round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                          (255, 0, 0, 0))

        if not flip:
            for i in range(len(games[str(guild.id)][id]['cards'])):
                card = Image.open('images/' + games[str(guild.id)][id]['cards'][i] + '.png')
                refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                       round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))
        else:
            for i in range(len(games[str(guild.id)][id]['cards'])):
                card = Image.open('images/' + games[str(guild.id)][id]['cards'][i][0] + '.png')
                refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                       round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)
                image.paste(refined, (i * refined.size[0], 0))

        with BytesIO() as image_binary:
            image.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='image.png')

        m.set_image(url='attachment://image.png')

        await discord.utils.get(guild.text_channels,
                                name=guild.get_member(int(id)).name.lower().replace(' ', '-').replace('.',
                                                                                                      '') + '-uno-channel').send(
            file=file, embed=m)

    if flip:
        c = choice(
            [card for card in games[str(guild.id)]['cards'] if
             card[0] != 'wild' and card[0] != '+2' and 'flip' not in card[0] and card[1] != 'darkwild' and card[
                 1] != '+color'])
        games[str(guild.id)]['current'] = c
        games[str(guild.id)]['current_opposite'] = c

    else:
        games[str(guild.id)]['current'] = choice(
            [card for card in games[str(guild.id)]['cards'] if card != 'wild' and card != '+4'])

    if games[str(guild.id)]['settings']['Flip']:
        color = search(r'red|blue|green|yellow', games[str(guild.id)]['current'][0]).group(0)
    else:
        color = search(r'red|blue|green|yellow', games[str(guild.id)]['current']).group(0)

    if color == 'red':
        message = discord.Embed(title='Top card:', color=discord.Color.red())
    elif color == 'blue':
        message = discord.Embed(title='Top card:', color=discord.Color.blue())
    elif color == 'green':
        message = discord.Embed(title='Top card:', color=discord.Color.green())
    else:
        message = discord.Embed(title='Top card:', color=discord.Color.from_rgb(255, 255, 0))

    if flip:
        image = Image.open('images/' + games[str(guild.id)]['current'][0] + '.png')
    else:
        image = Image.open('images/' + games[str(guild.id)]['current'] + '.png')
    refined = image.resize((round(image.size[0] / 6.0123456790123456790123456790123),
                            round(image.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)

    for channel in category.text_channels:
        with BytesIO() as image_binary:
            refined.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='topcard.png')

        message.set_image(url='attachment://topcard.png')
        await channel.send(file=file, embed=message)

    games[str(guild.id)]['player'] = int(order[0])
    cplayer = order[0]

    if flip:
        games[str(guild.id)]['dark'] = False

    print(
        '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game has started in ' + str(ctx.guild) + '.')

    if not games[str(guild.id)]['settings']['Flip']:
        if '+2' in games[str(guild.id)]['current']:
            if games[str(guild.id)]['settings']['StackCards'] \
                    and (any('+2' in card for card in games[str(guild.id)][cplayer]['cards'])
                         or any('+4' in card for card in games[str(guild.id)][cplayer]['cards'])):
                stack[str(guild.id)] = 2

                for channel in category.text_channels:
                    await channel.send(embed=discord.Embed(description='**' + guild.get_member(
                        int(cplayer)).name + ' can choose to stack cards or draw 2 cards.**',
                                                           color=discord.Color.red()))

                await display_cards(guild.get_member(int(cplayer)))

            else:
                await draw(guild.get_member(int(cplayer)), 2)
                await display_cards(guild.get_member(int(order[1])))

        else:
            await display_cards(guild.get_member(int(cplayer)))

    else:
        if '+1' in games[str(guild.id)]['current'][0]:
            if games[str(guild.id)]['settings']['StackCards'] and any(
                    '+2' in card for card in games[str(guild.id)][cplayer]['cards']):
                for channel in category.text_channels:
                    await channel.send(embed=discord.Embed(description='**' + guild.get_member(
                        int(cplayer)).name + ' can choose to stack cards or draw 1 card.**', color=discord.Color.red()))

                await display_cards(guild.get_member(int(cplayer)))

            else:
                await draw(guild.get_member(int(cplayer)), 1)
                await display_cards(guild.get_member(int(order[1])))

        else:
            await display_cards(guild.get_member(int(cplayer)))

    try:
        del stack[str(guild.id)]
    except KeyError:
        pass


async def game_shutdown(d, winner: discord.Member = None, guild=None):

    player_ids = list(d.keys())
    player_ids.remove('settings')
    player_ids.remove('seconds')
    try:
        player_ids.remove('cards')
    except ValueError:
        pass
    try:
        player_ids.remove('current')
    except ValueError:
        pass
    try:
        player_ids.remove('current_opposite')
    except ValueError:
        pass
    try:
        player_ids.remove('player')
    except ValueError:
        pass
    try:
        player_ids.remove('creator')
    except ValueError:
        pass
    try:
        player_ids.remove('dark')
    except ValueError:
        pass

    if winner and not guild:
        guild = winner.guild

        users_file = s3_resource.Object('unobot-bucket', 'users.json')
        users = json.loads(users_file.get()['Body'].read().decode('utf-8'))

        users[str(winner.id)][str(guild.id)]['Wins'] += 1
        for i in player_ids:
            users[i][str(guild.id)]['Played'] += 1

        users_file.put(Body=json.dumps(users).encode('utf-8'))

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

    if color:
        draw = []

        current_color = search(r'pink|teal|orange|purple', games[str(guild.id)]['current'][1]).group(0)
        c = choice(games[str(guild.id)]['cards'])

        games[str(guild.id)][str(player.id)]['cards'].append(c)
        games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                         card not in games[str(guild.id)][str(player.id)]['cards']]

        if not games[str(guild.id)]['cards']:
            games[str(guild.id)]['cards'] += cards

        draw.append(c)

        color = search(r'pink|teal|orange|purple', c[1])
        while not color or color.group(0) != current_color:
            c = choice(games[str(guild.id)]['cards'])

            games[str(guild.id)][str(player.id)]['cards'].append(c)
            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                             card not in games[str(guild.id)][str(player.id)]['cards']]

            if not games[str(guild.id)]['cards']:
                games[str(guild.id)]['cards'] += cards

            draw.append(c)

            color = search(r'pink|teal|orange|purple', c[1])

    else:
        if not DUM:
            draw = []

            for i in range(number):
                c = choice(games[str(guild.id)]['cards'])
                games[str(guild.id)][str(player.id)]['cards'].append(c)
                games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                 card not in games[str(guild.id)][str(player.id)]['cards']]

                if not games[str(guild.id)]['cards']:
                    if not games[str(guild.id)]['settings']['Flip']:
                        games[str(guild.id)]['cards'] += cards
                    else:
                        games[str(guild.id)]['cards'] += flip_cards

                draw.append(c)

        else:
            draw = []
            c = choice(games[str(guild.id)]['cards'])

            games[str(guild.id)][str(player.id)]['cards'].append(c)
            games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                             card not in games[str(guild.id)][str(player.id)]['cards']]

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

                    games[str(guild.id)][str(player.id)]['cards'].append(c)
                    games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                     card not in games[str(guild.id)][str(player.id)]['cards']]

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

                        games[str(guild.id)][str(player.id)]['cards'].append(c)
                        games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                         card not in games[str(guild.id)][str(player.id)]['cards']]

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

                        games[str(guild.id)][str(player.id)]['cards'].append(c)
                        games[str(guild.id)]['cards'] = [card for card in games[str(guild.id)]['cards'] if
                                                         card not in games[str(guild.id)][str(player.id)]['cards']]

                        if not games[str(guild.id)]['cards']:
                            games[str(guild.id)]['cards'] += cards

                        draw.append(c)

                        color = search(r'red|blue|green|yellow', c[1]).group(0)
                        value = search(r'\+[42]|wild|skip|reverse|\d', c[1]).group(0)

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

    await discord.utils.get(guild.channels,
                            name=player.name.lower().replace(' ', '-').replace('.', '') + '-uno-channel',
                            type=discord.ChannelType.text).send(file=file, embed=message)

    for channel in [x for x in guild.text_channels if
                    x.category.name == 'UNO-GAME' and x.name != player.name.lower().replace(' ', '-').replace('.',
                                                                                                              '') + '-uno-channel']:
        if len(draw) == 1:
            await channel.send(
                embed=discord.Embed(description='**' + player.name + '** drew a card.',
                                    color=discord.Color.red()))
        else:
            await channel.send(
                embed=discord.Embed(description='**' + player.name + '** drew **' + str(len(draw)) + '** cards.',
                                    color=discord.Color.red()))


async def display_cards(player: discord.Member):

    guild = player.guild

    if str(guild.id) not in ending:
        for channel in [x for x in guild.text_channels if x.category.name == 'UNO-GAME']:
            if channel.name == player.name.lower().replace(' ', '-').replace('.', '') + '-uno-channel':
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
                        len(games[str(guild.id)][str(player.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)][str(player.id)]['cards'])):
                        card = Image.open('images/' + games[str(guild.id)][str(player.id)]['cards'][i] + '.png')
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
                        len(games[str(guild.id)][str(player.id)]['cards']) * (
                            round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                        round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                      (255, 0, 0, 0))

                    for i in range(len(games[str(guild.id)][str(player.id)]['cards'])):
                        if not games[str(guild.id)]['dark']:
                            card = Image.open('images/' + games[str(guild.id)][str(player.id)]['cards'][i][0] + '.png')
                        else:
                            card = Image.open('images/' + games[str(guild.id)][str(player.id)]['cards'][i][1] + '.png')

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

                image = Image.new('RGBA', (
                    len(games[str(guild.id)][str(player.id)]['cards']) * (
                        round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                    round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                  (255, 0, 0, 0))

                for i in range(len(games[str(guild.id)][str(player.id)]['cards'])):
                    if games[str(guild.id)]['settings']['Flip']:
                        if not games[str(guild.id)]['dark']:
                            card = Image.open('images/' + games[str(guild.id)][str(player.id)]['cards'][i][1] + '.png')
                        else:
                            card = Image.open('images/' + games[str(guild.id)][str(player.id)]['cards'][i][0] + '.png')
                    else:
                        card = Image.open('images/back.png')

                    refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                           round(card.size[1] / 6.0123456790123456790123456790123)), Image.ANTIALIAS)

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
            p = list(games[str(guild.id)].keys())
            p.remove('settings')
            p.remove('seconds')
            try:
                p.remove('cards')
            except ValueError:
                pass
            try:
                p.remove('current')
            except ValueError:
                pass
            try:
                p.remove('current_opposite')
            except ValueError:
                pass
            try:
                p.remove('player')
            except ValueError:
                pass
            try:
                p.remove('creator')
            except ValueError:
                pass
            try:
                p.remove('dark')
            except ValueError:
                pass

            temp = iter(p)
            for key in temp:
                if key == str(player.id):
                    n = guild.get_member(int(next(temp, next(iter(p)))))
                    break

            message.set_footer(text=n.name + ' is next!')

            await channel.send(files=[thumbnail, file], embed=message)

            games[str(guild.id)]['player'] = player.id

    else:
        ending.remove(str(guild.id))

        return


async def play_card(card, player: discord.Member):

    guild = player.guild

    if not games[str(guild.id)]['settings']['Flip']:
        if '+4' in card:
            games[str(guild.id)][str(player.id)]['cards'].remove('+4')
        elif 'wild' in card:
            games[str(guild.id)][str(player.id)]['cards'].remove('wild')
        else:
            games[str(guild.id)][str(player.id)]['cards'].remove(card)

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

        if c:
            games[str(guild.id)][str(player.id)]['cards'].remove(c)
        else:
            games[str(guild.id)][str(player.id)]['cards'].remove(card)

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

    for channel in [x for x in guild.text_channels if x.category.name == 'UNO-GAME']:
        with BytesIO() as image_binary:
            refined.save(image_binary, format='PNG', quality=100)
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='card.png')

        message.set_image(url='attachment://card.png')

        await channel.send(file=file, embed=message)

    if not games[str(guild.id)][str(player.id)]['cards']:
        ending.append(str(guild.id))

        message = discord.Embed(title=player.name + ' Won! 🎉 🥳', color=discord.Color.red())
        message.set_image(url=player.avatar_url)

        for channel in [x for x in guild.text_channels if x.category.name == 'UNO-GAME']:
            await channel.send(embed=message)

        await asyncio.sleep(10)

        await game_shutdown(games[str(guild.id)], player)


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
        "**Thanks for adding UNOBot!** :thumbsup:\n• `/u.` is my prefix.\n• Use `/u.commands` for a list of commands.\n• Use `/u.help` if you need help.\n• Use `/u.guide` for an in-depth guide on me.\n"
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
                'Wins': 0,
                'Played': 0
            }

        else:
            user_stuff[str(member.id)] = {
                "AllowAlerts": True,
                str(member.guild.id): {
                    'Wins': 0,
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
                            'Wins': 0,
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
                p = list(games[str(message.guild.id)].keys())
                p.remove('settings')
                p.remove('seconds')
                try:
                    p.remove('cards')
                except ValueError:
                    return
                try:
                    p.remove('current')
                except ValueError:
                    return
                try:
                    p.remove('current_opposite')
                except ValueError:
                    pass
                try:
                    p.remove('player')
                except ValueError:
                    return
                try:
                    p.remove('creator')
                except ValueError:
                    return
                try:
                    p.remove('dark')
                except ValueError:
                    pass

                n = None
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

                player = None
                if games[str(message.guild.id)]['settings']['7-0'] and value == '7':
                    player = message.content.split()[-1]

                    if not message.guild.get_member_named(player):
                        await message.channel.send(
                            embed=discord.Embed(
                                description='**Player not found! Make sure the EXACT name of the player is entered. (It\'s case-sensitive!)**',
                                color=discord.Color.red()))

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

                    for channel in [x for x in message.channel.category.text_channels if x != message.channel]:
                        await channel.send(
                            embed=discord.Embed(title=message.author.name + ' says:', description=say,
                                                color=discord.Color.red()))

                    await message.add_reaction('\N{THUMBS UP SIGN}')

                    return

                elif color in ('a', 'alert'):
                    if 'alert' not in cooldowns[str(message.guild.id)]:
                        current_player = message.guild.get_member(int(games[str(message.guild.id)]['player']))

                        if current_player != message.author:
                            users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                            if users[str(current_player.id)]['AllowAlerts']:
                                await discord.utils.get(message.channel.category.text_channels,
                                                        name=current_player.name.lower().replace(' ', '-').replace('.',
                                                                                                                   '') + '-uno-channel').send(
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
                            len(games[str(message.guild.id)][str(message.author.id)]['cards']) * (
                                round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                            round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123)),
                                          (255, 0, 0, 0))
                    else:
                        image = Image.new('RGBA', (
                            len(games[str(message.guild.id)][str(message.author.id)]['cards']) * (
                                round(Image.open('images/empty.png').size[0] / 6.0123456790123456790123456790123)),
                            round(Image.open('images/empty.png').size[1] / 6.0123456790123456790123456790123 * 2)),
                                          (255, 0, 0, 0))

                    for i in range(len(games[str(message.guild.id)][str(message.author.id)]['cards'])):
                        if not games[str(message.guild.id)]['settings']['Flip']:
                            card = Image.open(
                                'images/' + games[str(message.guild.id)][str(message.author.id)]['cards'][i] + '.png')
                            refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                                   round(card.size[1] / 6.0123456790123456790123456790123)),
                                                  Image.ANTIALIAS)
                            image.paste(refined, (i * refined.size[0], 0))
                        else:
                            card = Image.open(
                                'images/' + games[str(message.guild.id)][str(message.author.id)]['cards'][i][
                                    0] + '.png')
                            refined = card.resize((round(card.size[0] / 6.0123456790123456790123456790123),
                                                   round(card.size[1] / 6.0123456790123456790123456790123)),
                                                  Image.ANTIALIAS)
                            image.paste(refined, (i * refined.size[0], 0))

                            card = Image.open(
                                'images/' + games[str(message.guild.id)][str(message.author.id)]['cards'][
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
                    await message.channel.set_permissions(message.author, overwrite=overwrite)

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
                                if color + value in games[str(message.guild.id)][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == value) and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        if games[str(message.guild.id)]['settings']['7-0']:
                                            player_ids = list(games[str(message.guild.id)].keys())
                                            player_ids.remove('settings')
                                            player_ids.remove('seconds')
                                            try:
                                                player_ids.remove('cards')
                                            except ValueError:
                                                pass
                                            try:
                                                player_ids.remove('current')
                                            except ValueError:
                                                pass
                                            try:
                                                player_ids.remove('current_opposite')
                                            except ValueError:
                                                pass
                                            try:
                                                player_ids.remove('player')
                                            except ValueError:
                                                pass
                                            try:
                                                player_ids.remove('creator')
                                            except ValueError:
                                                pass
                                            try:
                                                player_ids.remove('dark')
                                            except ValueError:
                                                pass

                                            if player:
                                                if '#' not in player:
                                                    match = [x for x in player_ids if
                                                             message.guild.get_member(int(x)).name == player]
                                                    if len(match) > 1:
                                                        await message.channel.send(
                                                            embed=discord.Embed(
                                                                description=':x: **There are multiple ' + player + '\'s here!**',
                                                                color=discord.Color.red()))

                                                        return

                                                    player = int(match[0])

                                                else:
                                                    player = message.guild.get_member_named(player).id

                                                await play_card(color + value, message.author)

                                                games[str(message.guild.id)][str(player)]['cards'], \
                                                games[str(message.guild.id)][str(message.author.id)]['cards'] = \
                                                    games[str(message.guild.id)][str(message.author.id)]['cards'], \
                                                    games[str(message.guild.id)][str(player)]['cards']

                                                for channel in message.channel.category.text_channels:
                                                    await channel.send(embed=discord.Embed(
                                                        description='**' + message.author.name + '** switched hands with **' + message.guild.get_member(
                                                            player).name + '**.', color=discord.Color.red()))

                                                await display_cards(n)

                                            elif value == '0':
                                                await play_card(color + value, message.author)

                                                d = deepcopy(games[str(message.guild.id)])

                                                for i in range(len(player_ids)):
                                                    games[str(message.guild.id)][player_ids[(i + 1) % len(player_ids)]][
                                                        'cards'] = d[player_ids[i]]['cards']

                                                for channel in message.channel.category.text_channels:
                                                    await channel.send(embed=discord.Embed(
                                                        description='**Everyone switched hands!**',
                                                        color=discord.Color.red()))

                                                await display_cards(n)

                                            elif value == '7':
                                                await message.channel.send(embed=discord.Embed(
                                                    description='**Please choose a player to switch hands with.**',
                                                    color=discord.Color.red()))

                                                overwrite.send_messages = True
                                                await message.channel.set_permissions(message.author,
                                                                                      overwrite=overwrite)

                                            else:
                                                await play_card(color + value, message.author)
                                                await display_cards(n)

                                        else:
                                            await play_card(color + value, message.author)
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
                                                         games[str(message.guild.id)][str(message.author.id)]['cards']]:
                                        if (current_color == color or current_value == value) and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            if games[str(message.guild.id)]['settings']['7-0']:
                                                player_ids = list(games[str(message.guild.id)].keys())
                                                player_ids.remove('settings')
                                                player_ids.remove('seconds')
                                                try:
                                                    player_ids.remove('cards')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('current')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('current_opposite')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('player')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('creator')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('dark')
                                                except ValueError:
                                                    pass

                                                if player:
                                                    if '#' not in player:
                                                        match = [x for x in player_ids if
                                                                 message.guild.get_member(int(x)).name == player]
                                                        if len(match) > 1:
                                                            await message.channel.send(
                                                                embed=discord.Embed(
                                                                    description=':x: **There are multiple ' + player + '\'s here!**',
                                                                    color=discord.Color.red()))

                                                            return

                                                        player = int(match[0])

                                                    else:
                                                        player = message.guild.get_member_named(player).id

                                                    await play_card(choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[0] == color + value]),
                                                                    message.author)

                                                    games[str(message.guild.id)][str(player)]['cards'], \
                                                    games[str(message.guild.id)][str(message.author.id)]['cards'] = \
                                                        games[str(message.guild.id)][str(message.author.id)]['cards'], \
                                                        games[str(message.guild.id)][str(player)]['cards']

                                                    for channel in message.channel.category.text_channels:
                                                        await channel.send(embed=discord.Embed(
                                                            description='**' + message.author.name + '** switched hands with **' + message.guild.get_member(
                                                                player).name + '**.', color=discord.Color.red()))

                                                    await display_cards(n)

                                                elif value == '0':
                                                    await play_card(choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[0] == color + value]),
                                                                    message.author)

                                                    d = deepcopy(games[str(message.guild.id)])

                                                    for i in range(len(player_ids)):
                                                        games[str(message.guild.id)][
                                                            player_ids[(i + 1) % len(player_ids)]][
                                                            'cards'] = d[player_ids[i]]['cards']

                                                    for channel in message.channel.category.text_channels:
                                                        await channel.send(embed=discord.Embed(
                                                            description='**Everyone switched hands!**',
                                                            color=discord.Color.red()))

                                                    await display_cards(n)

                                                elif value == '7':
                                                    await message.channel.send(embed=discord.Embed(
                                                        description='**Please choose a player to switch hands with.**',
                                                        color=discord.Color.red()))

                                                    overwrite.send_messages = True
                                                    await message.channel.set_permissions(message.author,
                                                                                          overwrite=overwrite)

                                                else:
                                                    await play_card(choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[0] == color + value]),
                                                                    message.author)
                                                    await display_cards(n)

                                            else:
                                                await play_card(choice([x for x in games[str(message.guild.id)][
                                                    str(message.author.id)]['cards'] if x[0] == color + value]),
                                                                message.author)
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
                                                         games[str(message.guild.id)][str(message.author.id)]['cards']]:
                                        if (current_color == color or current_value == value) and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            if games[str(message.guild.id)]['settings']['7-0']:
                                                player_ids = list(games[str(message.guild.id)].keys())
                                                player_ids.remove('settings')
                                                player_ids.remove('seconds')
                                                try:
                                                    player_ids.remove('cards')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('current')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('current_opposite')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('player')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('creator')
                                                except ValueError:
                                                    pass
                                                try:
                                                    player_ids.remove('dark')
                                                except ValueError:
                                                    pass

                                                if player:
                                                    if '#' not in player:
                                                        match = [x for x in player_ids if
                                                                 message.guild.get_member(int(x)).name == player]
                                                        if len(match) > 1:
                                                            await message.channel.send(
                                                                embed=discord.Embed(
                                                                    description=':x: **There are multiple ' + player + '\'s here!**',
                                                                    color=discord.Color.red()))

                                                            return

                                                        player = int(match[0])

                                                    else:
                                                        player = message.guild.get_member_named(player).id

                                                    await play_card(choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[1] == color + value]),
                                                                    message.author)

                                                    games[str(message.guild.id)][str(player)]['cards'], \
                                                    games[str(message.guild.id)][str(message.author.id)]['cards'] = \
                                                        games[str(message.guild.id)][str(message.author.id)]['cards'], \
                                                        games[str(message.guild.id)][str(player)]['cards']

                                                    for channel in message.channel.category.text_channels:
                                                        await channel.send(embed=discord.Embed(
                                                            description='**' + message.author.name + '** switched hands with **' + message.guild.get_member(
                                                                player).name + '**.', color=discord.Color.red()))

                                                    await display_cards(n)

                                                elif value == '0':
                                                    await play_card(choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[1] == color + value]),
                                                                    message.author)

                                                    d = deepcopy(games[str(message.guild.id)])

                                                    for i in range(len(player_ids)):
                                                        games[str(message.guild.id)][
                                                            player_ids[(i + 1) % len(player_ids)]][
                                                            'cards'] = d[player_ids[i]]['cards']

                                                    for channel in message.channel.category.text_channels:
                                                        await channel.send(embed=discord.Embed(
                                                            description='**Everyone switched hands!**',
                                                            color=discord.Color.red()))

                                                    await display_cards(n)

                                                elif value == '7':
                                                    await message.channel.send(embed=discord.Embed(
                                                        description='**Please choose a player to switch hands with.**',
                                                        color=discord.Color.red()))

                                                    overwrite.send_messages = True
                                                    await message.channel.set_permissions(message.author,
                                                                                          overwrite=overwrite)

                                                else:
                                                    await play_card(choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[1] == color + value]),
                                                                    message.author)
                                                    await display_cards(n)

                                            else:
                                                await play_card(choice([x for x in games[str(message.guild.id)][
                                                    str(message.author.id)]['cards'] if x[1] == color + value]),
                                                                message.author)
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
                            if '+4' in games[str(message.guild.id)][str(message.author.id)]['cards']:
                                await play_card(color + '+4', message.author)

                                if str(message.guild.id) not in stack:
                                    stack[str(message.guild.id)] = 4
                                else:
                                    stack[str(message.guild.id)] += 4

                                if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                        '+4' in card for card in games[str(message.guild.id)][str(n.id)]['cards']):
                                    for channel in message.channel.category.text_channels:
                                        await channel.send(embed=discord.Embed(
                                            description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                stack[str(message.guild.id)]) + ' cards.**',
                                            color=discord.Color.red()))

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
                                if color + 'reverse' in games[str(message.guild.id)][str(message.author.id)]['cards']:
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
                                        try:
                                            await message.channel.set_permissions(message.author, overwrite=overwrite)
                                        except discord.errors.NotFound:
                                            pass

                                        return

                                else:
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            description=':x: **You don\'t have a ' + color.capitalize() + 'Reverse!**',
                                            color=discord.Color.red()))

                                    overwrite.send_messages = True
                                    try:
                                        await message.channel.set_permissions(message.author, overwrite=overwrite)
                                    except discord.errors.NotFound:
                                        pass

                                    return

                            else:
                                if not games[str(message.guild.id)]['dark']:
                                    if color + 'reverse' in [x[0] for x in
                                                             games[str(message.guild.id)][str(message.author.id)][
                                                                 'cards']]:
                                        if (current_color == color or current_value == 'reverse') and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)][
                                                str(message.author.id)]['cards'] if x[0] == color + 'reverse']),
                                                            message.author)

                                        else:
                                            await message.channel.send(
                                                embed=discord.Embed(
                                                    description=':x: **You can\'t play a ' + color.capitalize() + 'Reverse here!**',
                                                    color=discord.Color.red()))

                                            overwrite.send_messages = True
                                            try:
                                                await message.channel.set_permissions(message.author,
                                                                                      overwrite=overwrite)
                                            except discord.errors.NotFound:
                                                pass

                                            return

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You don\'t have a ' + color.capitalize() + 'Reverse!**',
                                                color=discord.Color.red()))

                                        overwrite.send_messages = True
                                        try:
                                            await message.channel.set_permissions(message.author, overwrite=overwrite)
                                        except discord.errors.NotFound:
                                            pass

                                        return

                                else:
                                    if color + 'reverse' in [x[1] for x in
                                                             games[str(message.guild.id)][str(message.author.id)][
                                                                 'cards']]:
                                        if (current_color == color or current_value == 'reverse') and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)][
                                                str(message.author.id)]['cards'] if x[1] == color + 'reverse']),
                                                            message.author)

                                        else:
                                            await message.channel.send(
                                                embed=discord.Embed(
                                                    description=':x: **You can\'t play a ' + color.capitalize() + 'Reverse here!**',
                                                    color=discord.Color.red()))

                                            overwrite.send_messages = True
                                            try:
                                                await message.channel.set_permissions(message.author,
                                                                                      overwrite=overwrite)
                                            except discord.errors.NotFound:
                                                pass

                                            return

                                    else:
                                        await message.channel.send(
                                            embed=discord.Embed(
                                                description=':x: **You don\'t have a ' + color.capitalize() + 'Reverse!**',
                                                color=discord.Color.red()))

                                        overwrite.send_messages = True
                                        try:
                                            await message.channel.set_permissions(message.author, overwrite=overwrite)
                                        except discord.errors.NotFound:
                                            pass

                                        return

                            d = games[str(message.guild.id)]
                            player_ids = list(d.keys())
                            player_ids.remove('settings')
                            player_ids.remove('seconds')
                            try:
                                player_ids.remove('cards')
                            except ValueError:
                                pass
                            try:
                                player_ids.remove('current')
                            except ValueError:
                                pass
                            try:
                                player_ids.remove('current_opposite')
                            except ValueError:
                                pass
                            try:
                                player_ids.remove('player')
                            except ValueError:
                                pass
                            try:
                                player_ids.remove('creator')
                            except ValueError:
                                pass
                            try:
                                player_ids.remove('dark')
                            except ValueError:
                                pass

                            player_ids.reverse()

                            ordered_dict = OrderedDict()
                            ordered_dict['settings'], ordered_dict['seconds'], ordered_dict['cards'], ordered_dict[
                                'current'], ordered_dict['player'], ordered_dict['creator'] = d['settings'], d[
                                'seconds'], d['cards'], d['current'], d['player'], d['creator']
                            if 'current_opposite' in d:
                                ordered_dict['current_opposite'] = d['current_opposite']
                            if 'dark' in d:
                                ordered_dict['dark'] = d['dark']
                            for x in player_ids:
                                ordered_dict[x] = d[x]

                            games[str(message.guild.id)] = dict(ordered_dict)

                            for channel in message.channel.category.text_channels:
                                await channel.send(
                                    embed=discord.Embed(description='**The player order is reversed.**',
                                                        color=discord.Color.red()))

                            p = list(games[str(message.guild.id)].keys())
                            p.remove('settings')
                            p.remove('seconds')
                            p.remove('cards')
                            p.remove('current')
                            p.remove('player')
                            p.remove('creator')
                            try:
                                p.remove('current_opposite')
                            except ValueError:
                                pass
                            try:
                                p.remove('dark')
                            except ValueError:
                                pass

                            m = None
                            temp = iter(p)
                            for key in temp:
                                if key == str(message.author.id):
                                    m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                    break

                            await display_cards(m)

                        elif value in ('skip', 's'):
                            if not games[str(message.guild.id)]['settings']['Flip']:
                                if color + 'skip' in games[str(message.guild.id)][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == 'skip') and not (
                                            '+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(color + 'skip', message.author)

                                        for channel in message.channel.category.text_channels:
                                            await channel.send(
                                                embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                                    color=discord.Color.red()))

                                        m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                        if m == n:
                                            iterable = iter(p)
                                            next(iterable)
                                            m = message.guild.get_member(int(next(iterable)))

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
                                                          games[str(message.guild.id)][str(message.author.id)][
                                                              'cards']]:
                                        if (current_color == color or current_value == 'skip') and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)][
                                                str(message.author.id)]['cards'] if x[0] == color + 'skip']),
                                                            message.author)

                                            for channel in message.channel.category.text_channels:
                                                await channel.send(
                                                    embed=discord.Embed(description='**' + n.name + ' is skipped.**',
                                                                        color=discord.Color.red()))

                                            m = message.guild.get_member(int(next(temp, next(iter(p)))))
                                            if m == n:
                                                iterable = iter(p)
                                                next(iterable)
                                                m = message.guild.get_member(int(next(iterable)))

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
                                                          games[str(message.guild.id)][str(message.author.id)][
                                                              'cards']]:
                                        if (current_color == color or current_value == 'skip') and not (
                                                '+' in current_value and games[str(message.guild.id)]['settings'][
                                            'StackCards'] and str(message.guild.id) in stack):
                                            await play_card(choice([x for x in games[str(message.guild.id)][
                                                str(message.author.id)]['cards'] if x[1] == color + 'skip']),
                                                            message.author)

                                            for channel in message.channel.category.text_channels:
                                                await channel.send(
                                                    embed=discord.Embed(description='**Everyone is skipped!**',
                                                                        color=discord.Color.red()))

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
                                if 'wild' in games[str(message.guild.id)][str(message.author.id)]['cards']:
                                    if not ('+' in current_value and games[str(message.guild.id)]['settings'][
                                        'StackCards'] and str(message.guild.id) in stack):
                                        await play_card(color + 'wild', message.author)
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
                                           games[str(message.guild.id)][str(message.author.id)]['cards']):
                                        if color in ('red', 'blue', 'green', 'yellow'):
                                            if not ('+' in current_value and games[str(message.guild.id)]['settings'][
                                                'StackCards'] and str(message.guild.id) in stack):
                                                await play_card(
                                                    (color + 'wild', choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[0] == 'wild'])[1]),
                                                    message.author)
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
                                           games[str(message.guild.id)][str(message.author.id)]['cards']):
                                        if color in ('pink', 'teal', 'orange', 'purple'):
                                            if not ('+' in current_value and games[str(message.guild.id)]['settings'][
                                                'StackCards'] and str(message.guild.id) in stack):
                                                await play_card((
                                                    choice([x for x in games[str(message.guild.id)][
                                                        str(message.author.id)]['cards'] if x[1] == 'darkwild'])[
                                                        0], color + 'wild'),
                                                    message.author)
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
                                if color + '+2' in games[str(message.guild.id)][str(message.author.id)]['cards']:
                                    if (current_color == color or current_value == '+2') and not (
                                            current_value == '+4' and str(message.guild.id) in stack):
                                        await play_card(color + '+2', message.author)

                                        if str(message.guild.id) not in stack:
                                            stack[str(message.guild.id)] = 2
                                        else:
                                            stack[str(message.guild.id)] += 2

                                        if games[str(message.guild.id)]['settings']['StackCards'] and (
                                                any('+2' in card for card in
                                                    games[str(message.guild.id)][str(n.id)]['cards']) or any(
                                            '+4' in card for card in games[str(message.guild.id)][str(n.id)]['cards'])):
                                            for channel in message.channel.category.text_channels:
                                                await channel.send(embed=discord.Embed(
                                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                        stack[str(message.guild.id)]) + ' cards.**',
                                                    color=discord.Color.red()))

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
                                           games[str(message.guild.id)][str(message.author.id)]['cards']):
                                        if color in ('red', 'blue', 'green', 'yellow'):
                                            await play_card(
                                                (color + '+2', choice([x for x in games[str(message.guild.id)][
                                                    str(message.author.id)]['cards'] if x[0] == '+2'])[
                                                    1]), message.author)

                                            if str(message.guild.id) not in stack:
                                                stack[str(message.guild.id)] = 2
                                            else:
                                                stack[str(message.guild.id)] += 2

                                            if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                    card[0] == '+2' for card in
                                                    games[str(message.guild.id)][str(n.id)]['cards']):
                                                for channel in message.channel.category.text_channels:
                                                    await channel.send(embed=discord.Embed(
                                                        description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                            stack[str(message.guild.id)]) + ' cards.**',
                                                        color=discord.Color.red()))

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
                                       games[str(message.guild.id)][str(message.author.id)]['cards']):
                                    if (current_color == color or current_value == '+1') and not (
                                            current_value == '+2' and str(message.guild.id) in stack):
                                        await play_card(choice([x for x in games[str(message.guild.id)][
                                            str(message.author.id)]['cards'] if x[0] == color + '+1']), message.author)

                                        if str(message.guild.id) not in stack:
                                            stack[str(message.guild.id)] = 1
                                        else:
                                            stack[str(message.guild.id)] += 1

                                        if games[str(message.guild.id)]['settings']['StackCards'] and (
                                                any('+1' in card[0] for card in
                                                    games[str(message.guild.id)][str(n.id)]['cards']) or any(
                                            card[0] == '+2' for card in
                                            games[str(message.guild.id)][str(n.id)]['cards'])):
                                            for channel in message.channel.category.text_channels:
                                                await channel.send(embed=discord.Embed(
                                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                        stack[str(message.guild.id)]) + ' cards.**',
                                                    color=discord.Color.red()))

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
                                       games[str(message.guild.id)][str(message.author.id)]['cards']):
                                    if current_color == color or current_value == '+5':
                                        await play_card(choice([x for x in games[str(message.guild.id)][
                                            str(message.author.id)]['cards'] if x[1] == color + '+5']), message.author)

                                        if str(message.guild.id) not in stack:
                                            stack[str(message.guild.id)] = 5
                                        else:
                                            stack[str(message.guild.id)] += 5

                                        if games[str(message.guild.id)]['settings']['StackCards'] and any(
                                                '+5' in card[1] for card in
                                                games[str(message.guild.id)][str(n.id)]['cards']):
                                            for channel in message.channel.category.text_channels:
                                                await channel.send(embed=discord.Embed(
                                                    description='**' + n.name + ' can choose to stack cards or draw ' + str(
                                                        stack[str(message.guild.id)]) + ' cards.**',
                                                    color=discord.Color.red()))

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
                                       games[str(message.guild.id)][str(message.author.id)]['cards']):
                                    await play_card((choice([x for x in games[str(message.guild.id)][
                                        str(message.author.id)]['cards'] if x[1] == '+color'])[
                                                         0], color + '+color'), message.author)

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
                                                          games[str(message.guild.id)][str(message.author.id)][
                                                              'cards']]:
                                        if color == current_color or current_value == 'flip':
                                            c = choice([x for x in games[str(message.guild.id)][
                                                str(message.author.id)]['cards'] if x[0] == color + 'flip'])

                                            await play_card(c, message.author)

                                            games[str(message.guild.id)]['dark'] = not games[str(message.guild.id)][
                                                'dark']
                                            games[str(message.guild.id)]['current'] = games[str(message.guild.id)][
                                                'current_opposite']
                                            games[str(message.guild.id)]['current_opposite'] = c

                                            for channel in message.channel.category.text_channels:
                                                await channel.send(embed=discord.Embed(
                                                    description='**Everything is flipped!**',
                                                    color=discord.Color.red()))

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
                                                          games[str(message.guild.id)][str(message.author.id)][
                                                              'cards']]:
                                        if color == current_color or current_value == 'flip':
                                            c = choice([x for x in games[str(message.guild.id)][
                                                str(message.author.id)]['cards'] if x[1] == color + 'flip'])

                                            await play_card(c, message.author)

                                            games[str(message.guild.id)]['dark'] = not games[str(message.guild.id)][
                                                'dark']
                                            games[str(message.guild.id)]['current'] = games[str(message.guild.id)][
                                                'current_opposite']
                                            games[str(message.guild.id)]['current_opposite'] = c

                                            for channel in message.channel.category.text_channels:
                                                await channel.send(embed=discord.Embed(
                                                    description='**Everything is flipped!**',
                                                    color=discord.Color.red()))

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
                    except discord.errors.NotFound:
                        pass

                else:

                    await message.channel.send(
                        embed=discord.Embed(description=':x: **It\'s not your turn yet!**', color=discord.Color.red()))

            except KeyError:
                pass

        else:
            await client.process_commands(message)


@client.event
async def on_raw_reaction_add(payload):

    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = client.get_guild(payload.guild_id)

    if message.author == client.user and not payload.member.bot and (
            str(guild.id) in games and 'current' not in games[str(guild.id)]):
        message_dict = message.embeds[0].to_dict()

        if str(payload.emoji) == '✋':
            user_options = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

            if str(payload.user_id) not in games[str(guild.id)]:
                for g in client.guilds:
                    user_options[str(payload.user_id)].pop(str(g.id), None)

                games[str(guild.id)][str(payload.user_id)] = user_options[str(payload.user_id)]
                games[str(guild.id)][str(payload.user_id)]['cards'] = []

                if len(games[str(guild.id)].keys()) + 1 > 2:
                    for field in message_dict['fields']:
                        if field['name'] == 'Players:':
                            value = ''

                            for key in games[str(guild.id)]:
                                if key in ('settings', 'seconds'):
                                    continue
                                else:
                                    value += (':small_blue_diamond: ' + guild.get_member(int(key)).name + '\n')

                            field['value'] = value

                            break

                await message.edit(embed=discord.Embed.from_dict(message_dict))

        elif str(payload.emoji) == '▶️':
            if payload.member == guild.owner or str(payload.member) == message.embeds[0].to_dict()['fields'][2][
                'value']:
                await message.clear_reaction('✋')
                await message.clear_reaction('▶️')
                await message.clear_reaction('❌')

                games[str(guild.id)]['seconds'] = -2

                if len(games[str(guild.id)].keys()) > 3:
                    players = games[str(guild.id)]

                    await game_setup(await client.get_context(message), players)

                    games[str(guild.id)]['creator'] = payload.member.id

                    message_dict['title'] = 'A game of UNO has started!'
                    message_dict[
                        'description'] = ':white_check_mark: A game of UNO has started. Go to your UNO channel titled with your username.'
                    del message_dict['footer']

                    await message.edit(embed=discord.Embed.from_dict(message_dict))

                else:
                    message_dict['title'] = 'A game of UNO failed to start!'
                    message_dict[
                        'description'] = ':x: Not enough players! At least 2 players are needed (Bots do not count).'
                    del message_dict['footer']

                    await message.edit(embed=discord.Embed.from_dict(message_dict))

                    print('[' + datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game failed to start in ' + str(guild) + '.')

        elif str(payload.emoji) == '❌':
            if payload.member == guild.owner or str(payload.member) == message.embeds[0].to_dict()['fields'][2][
                'value']:
                await message.clear_reaction('✋')
                await message.clear_reaction('▶️')
                await message.clear_reaction('❌')

                games[str(guild.id)]['seconds'] = -1

                message_dict['title'] = 'A game of UNO was cancelled!'

                if payload.member == guild.owner:
                    message_dict['description'] = ':x: The server owner cancelled the game.'
                elif str(payload.member) == message.embeds[0].to_dict()['fields'][2]['value']:
                    message_dict['description'] = ':x: The game creator cancelled the game.'

                del message_dict['footer']

                await message.edit(embed=discord.Embed.from_dict(message_dict))

                try:
                    del games[str(guild.id)]
                except ValueError:
                    pass
                except KeyError:
                    pass

                print('[' + datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S') + ' | UNOBot] A game is cancelled in ' + str(guild) + '.')


@client.event
async def on_raw_reaction_remove(payload):

    timestamp = datetime.now()

    if (timestamp - last_run).total_seconds() < 3:
        await asyncio.sleep(3)

    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = client.get_guild(payload.guild_id)
    user = client.get_user(payload.user_id)

    if str(guild.id) not in games or str(user.id) not in games[str(guild.id)]:
        await asyncio.sleep(1)

    if message.author == client.user and not user.bot and (
            str(guild.id) in games and 'current' not in games[str(guild.id)]):
        message_dict = message.embeds[0].to_dict()

        if str(payload.emoji) == '✋':
            del games[str(guild.id)][str(user.id)]

            if len(games[str(guild.id)].keys()) >= 2:
                for field in message_dict['fields']:
                    if field['name'] == 'Players:':
                        if len(games[str(guild.id)].keys()) == 2:
                            field['value'] = 'None'
                        else:
                            value = ''

                            for key in games[str(guild.id)]:
                                if key in ('settings', 'seconds'):
                                    continue
                                else:
                                    value += (':small_blue_diamond: ' + guild.get_member(int(key)).name + '\n')

                            field['value'] = value

                        break

            await message.edit(embed=discord.Embed.from_dict(message_dict))


@client.command(aliases=[chr(173) + 'help', 'hp', 'h', '?'])
async def help(ctx):

    UNOBotPNG = discord.File('images/UNOBot.png', filename='bot.png')

    message = discord.Embed(title='UNO Bot Help', color=discord.Color.red())
    message.set_thumbnail(url='attachment://bot.png')
    message.add_field(name=':exclamation: Command List', value='`/u.commands`\nGet a list of commands.\n' + chr(173),
                      inline=False)
    message.add_field(name=':closed_book: Guide',
                      value='`/u.guide`\nRead an in-depth guide on using UNO Bot.\n' + chr(173), inline=False)
    message.add_field(name=':scroll: UNO Rules', value='`/u.rules`\nRead the rules of the original UNO.', inline=False)

    await ctx.send(file=UNOBotPNG, embed=message)


@client.command(aliases=[chr(173) + 'commands', 'cmds', 'cmd'])
async def commands(ctx, command=None):

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

        await ctx.send(file=UNOBotPNG, embed=message)

    else:
        if command in ('startgame', 'sg', 'start'):
            message = discord.Embed(title=prefix + 'startgame', color=discord.Color.red())
            message.add_field(name='Description:',
                              value='Start a game of UNO. Play with those mentioned in the message. Players can play their cards in their auto-created UNO channels.',
                              inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'startgame (list of @user-mentions) (game settings)`',
                              inline=False)
            message.add_field(name=chr(173),
                              value='**Note:** You must have at least 2 players to start a game, bots do not count.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Tips:',
                              value='• Use `' + prefix + 'gamesettings list` to get a list of the game settings.\n• You can change the default game settings using `' + prefix + 'settings dgs`.',
                              inline=False)
            message.add_field(name='Examples:',
                              value='• `' + prefix + 'startgame @VTiS @CoffinMan`\n• `' + prefix + 'sg advancedStart`')
            message.add_field(name='Aliases: ', value='start, sg')

            await ctx.send(embed=message)

        elif command in ('endgame', 'eg', 'stop'):
            message = discord.Embed(title=prefix + 'endgame', color=discord.Color.red())
            message.add_field(name='Description:', value='Ends the ongoing UNO game.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'endgame`', inline=False)
            message.add_field(name=chr(173),
                              value='**Note:** Only the game creator, admins, and whitelisted roles from the settings can use this.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Aliases: ', value='eg, stop')

            await ctx.send(embed=message)

        elif command in ('leavegame', 'leave', 'quit', 'lg', 'quitgame'):
            message = discord.Embed(title=prefix + 'leavegame', color=discord.Color.red())
            message.add_field(name='Description:', value='Lets you leave the UNO game.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'leavegame`', inline=False)
            message.add_field(name='Aliases: ', value='leave, quite, lg, quitgame')

            await ctx.send(embed=message)

        elif command in ('kick', 'remove'):
            message = discord.Embed(title=prefix + 'kick', color=discord.Color.red())
            message.add_field(name='Description:', value='Kicks a player from an UNO game.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'kick <@user-mention>`', inline=False)
            message.add_field(name=chr(173),
                              value='**Note:** Only the game creator, admins, and whitelisted roles from the settings can use this.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Examples:', value='`' + prefix + 'kick @CoffinMan`')
            message.add_field(name='Aliases: ', value='remove')

            await ctx.send(embed=message)

        elif command in ('spectate', 'spec'):
            message = discord.Embed(title=prefix + 'spectate', color=discord.Color.red())
            message.add_field(name='Description:', value='Spectate games of UNO.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'spectate (on|off)`', inline=False)
            message.add_field(name='Aliases: ', value='spec')

            await ctx.send(embed=message)

        elif command == 'stats':
            message = discord.Embed(title=prefix + 'stats', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a user\'s stats only from this Discord server.',
                              inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'stats (@user-mention)`', inline=False)
            message.add_field(name=chr(173),
                              value='**Tip:** You can hide your stats with `' + prefix + 'options HideStats on`.\n' + chr(
                                  173), inline=False)
            message.add_field(name='Examples:', value='`' + prefix + 'stats @VTiS`')

            await ctx.send(embed=message)

        elif command in ('globalstats', 'gstats', 'global-stats', 'g-stats', 'global_stats', 'g_stats'):
            message = discord.Embed(title=prefix + 'globalstats', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a user\'s stats from all servers.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'globalstats (@user-mention)`', inline=False)
            message.add_field(name='Tips:', value='• You can just type `' + prefix + 'gstats`.\n'
                                                                                     '• You can hide your global stats with `' + prefix + 'options HideGlobalStats on`.',
                              inline=False)
            message.add_field(name='Examples:', value='• `' + prefix + 'globalstats @VTiS`')
            message.add_field(name='Aliases: ', value='gstats, global-stats, g-stats, global_stats, g_stats')

            await ctx.send(embed=message)

        elif command in ('leaderboard', 'lb', 'leaderboards'):
            message = discord.Embed(title=prefix + 'leaderboard', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a leaderboard only from this Discord server.',
                              inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'leaderboard`', inline=False)
            message.add_field(name='Aliases: ', value='lb, leaderboards')

            await ctx.send(embed=message)

        elif command in (
                'globalleaderboard', 'glb', 'g-lb', 'g_lb', 'gleaderboard', 'global-leaderboard', 'global_leaderboard'):
            message = discord.Embed(title=prefix + 'globalleaderboard', color=discord.Color.red())
            message.add_field(name='Description:', value='Gives you a eladerboard for all servers.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'globalleaderboard`', inline=False)
            message.add_field(name='Aliases: ',
                              value='glb, g-lb, g_lb, gleaderboard, global-leaderboard, global_leaderboard')

            await ctx.send(embed=message)

        elif command in ('allowalerts', 'alerts', 'alert', 'aa'):
            message = discord.Embed(title=prefix + 'allowalerts', color=discord.Color.red())
            message.add_field(name='Description:', value='Allows alerts just for you.', inline=False)
            message.add_field(name='Usage:', value='`' + prefix + 'allowalerts <on|off|view>`', inline=False)
            message.add_field(name='Examples:', value='• `' + prefix + 'aa on`')
            message.add_field(name='Aliases: ', value='allowalerts, alerts, alert, aa')

            await ctx.send(embed=message)

        elif command in ('settings', 'set', 'sett', 'stngs', 'setting', 'stng'):
            message = discord.Embed(title='UNOBot Settings', color=discord.Color.red(),
                                    description='Adjusts how UNOBot works for the entire server.')
            message.add_field(name=':wrench: Command Customization:', value=prefix + '`settings commands`')
            message.add_field(name=':game_die: Default Game Settings:', value=prefix + '`settings dgs`')
            message.add_field(name=':arrows_counterclockwise: Reset UNOBot:', value=prefix + '`settings reset`',
                              inline=False)
            message.add_field(name='Aliases: ', value='set, sett, stngs, setting, stng')

            await ctx.send(embed=message)


@client.command(aliases=[chr(173) + 'guide', 'g'])
async def guide(ctx, arg=None):

    if not arg:
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

        await ctx.send(file=UNOBotPNG, embed=message)

    else:
        if arg == 'start':
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

            await ctx.send(embed=message)

        elif arg == 'play':
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

            await ctx.send(embed=message)

        elif arg == 'commands':
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

            await ctx.send(embed=message)

        elif arg == 'settings':
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

            await ctx.send(embed=message)

        elif arg == 'options':
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

            await ctx.send(embed=message)


@client.command(aliases=[chr(173) + 'rules', 'r'])
async def rules(ctx):
    await ctx.send("https://github.com/VTiS15/UNOBot#game-rule")


@client.command(aliases=[chr(173) + 'stats'])
async def stats(ctx, user: discord.User = None):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'stats' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['stats']['Enabled']:
            if not user:
                user = ctx.message.author

            if ((not commands[str(ctx.guild.id)]['stats']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['stats']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['stats']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['stats']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['stats']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['stats']['Whitelist']) or ctx.message.author == ctx.guild.owner:

                users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                if users[str(user.id)][str(ctx.guild.id)]['Played'] > 0:
                    message = discord.Embed(title=user.name + '\'s Stats in ' + ctx.guild.name,
                                            color=discord.Color.red())
                    message.set_thumbnail(url=user.avatar_url)
                    ranking = rank(False, False, user, ctx.guild)
                    message.add_field(name='Rank', value='Rank **' + str(ranking[0]) + '** out of ' + str(ranking[1]),
                                      inline=False)
                    dict = users[str(user.id)][str(ctx.guild.id)]
                    message.add_field(name='Win Percentage',
                                      value='Won **' + str(
                                          round(dict['Wins'] / dict['Played'] * 100)) + '%** of games.',
                                      inline=False)
                    message.add_field(name='Total Games', value='**' + str(dict['Played']) + '** games played.',
                                      inline=False)
                    message.add_field(name='Total Wins', value='**' + str(dict['Wins']) + '** games won.', inline=False)
                    message.add_field(name='Total Losses',
                                      value='**' + str(dict['Played'] - dict['Wins']) + '** games lost.')

                    await ctx.send(embed=message)

                else:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(),
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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['stats']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(
    aliases=[chr(173) + 'globalstats', 'gstats', chr(173) + 'global_stats', 'global_stats', 'g-stats', 'g_stats'])
async def globalstats(ctx, user: discord.User = None):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'globalstats' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['globalstats']['Enabled']:
            if not user:
                user = ctx.message.author

            if ((not commands[str(ctx.guild.id)]['globalstats']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['globalstats']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['globalstats']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['globalstats']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['globalstats']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['globalstats'][
                             'Whitelist']) or ctx.message.author == ctx.guild.owner:

                users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                if has_played(user):
                    message = discord.Embed(title=user.name + '\'s Global Stats', color=discord.Color.red())
                    message.set_thumbnail(url=user.avatar_url)
                    ranking = rank(True, False, user)
                    message.add_field(name='Rank', value='Rank **' + str(ranking[0]) + '** out of ' + str(ranking[1]),
                                      inline=False)

                    p = 0
                    for guild in client.guilds:
                        if guild.get_member(user.id):
                            p += users[str(user.id)][str(guild.id)]['Played']

                    w = 0
                    for guild in [x for x in client.guilds if x.get_member(user.id)]:
                        w += users[str(user.id)][str(guild.id)]['Wins']

                    message.add_field(name='Win Percentage', value='Won **' + str(round(w / p * 100)) + '%** of games.',
                                      inline=False)
                    message.add_field(name='Total Games', value='**' + str(p) + '** games played.', inline=False)
                    message.add_field(name='Total Wins', value='**' + str(w) + '** games won.', inline=False)
                    message.add_field(name='Total Losses', value='**' + str(p - w) + '** games lost.')

                    await ctx.send(embed=message)

                else:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(),
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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['globalstats']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'leaderboard', 'lb'])
async def leaderboard(ctx):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'leaderboard' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['leaderboard']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['leaderboard']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['leaderboard']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['leaderboard']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['leaderboard']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['leaderboard']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['leaderboard'][
                             'Whitelist']) or ctx.message.author == ctx.guild.owner:
                message = discord.Embed(title=ctx.guild.name + '\'s Leaderboard', color=discord.Color.red(),
                                        description='The top UNO players in your Discord server.')

                users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                leaderboard = rank(False, True, None, ctx.guild)
                count = 0

                for i in range(1, len(leaderboard) + 1):
                    for index in list_duplicates_of(leaderboard, i):
                        user = client.get_user(
                            int([x for x in list(users.keys()) if ctx.guild.get_member(int(x))][index]))

                        if users[str(user.id)][str(ctx.guild.id)]['Played'] > 0:
                            message.add_field(name='Rank ' + str(i), value='**' + str(user) + '**\n' + str(
                                users[str(user.id)][str(ctx.guild.id)]['Wins']) + ' total wins.', inline=False)

                            count += 1

                        if count >= 5:
                            break

                    if count >= 5:
                        break

                message.set_thumbnail(url=ctx.guild.icon_url)

                if count > 0:
                    await ctx.send(embed=message)
                else:
                    message = discord.Embed(color=discord.Color.red(),
                                            description=':x: **No one has played UNO in this server yet!**')
                    await ctx.send(embed=message)

                if commands[str(ctx.guild.id)]['leaderboard']['Cooldown'] > 0:
                    cooldowns[str(ctx.guild.id)].append('leaderboard')

                    def check(message):
                        return len(message.content.split()) == 6 \
                               and message.content.split()[0] in (
                                   prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                   prefix + 'setting',
                                   prefix + 'stng') \
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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['leaderboard']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'globalleaderboard', 'glb', 'g-lb', 'g_lb', 'gleaderboard', 'global-leaderboard',
                         'global_leaderboard'])
async def globalleaderboard(ctx):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'globalleaderboard' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['globalleaderboard']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['globalleaderboard']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['globalleaderboard']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['globalleaderboard']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['globalleaderboard']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['globalleaderboard']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['globalleaderboard'][
                             'Whitelist']) or ctx.message.author == ctx.guild.owner:
                users = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                message = discord.Embed(title='Global Leaderboard', color=discord.Color.red(),
                                        description='The top UNO players from all Discord servers.')

                leaderboard = rank(True, True)
                count = 0

                for i in range(1, len(leaderboard) + 1):
                    for index in list_duplicates_of(leaderboard, i):
                        user = client.get_user(int(list(users.keys())[index]))
                        p = 0

                        for guild in client.guilds:
                            if guild.get_member(user.id):
                                p += users[str(user.id)][str(guild.id)]['Played']

                        if p > 0:
                            w = 0
                            for g in client.guilds:
                                if g.get_member(user.id):
                                    w += users[str(user.id)][str(g.id)]['Wins']

                            message.add_field(name='Rank ' + str(i),
                                              value='**' + str(user) + '**\n' + str(w) + ' total wins.', inline=False)

                            count += 1

                        if count >= 5:
                            break

                    if count >= 5:
                        break

                if count > 0:
                    message.set_footer(text='Use "' + prefix + 'globalstats" to check your rank.')
                    await ctx.send(embed=message)
                else:
                    message = discord.Embed(color=discord.Color.red(), description=':x: **No one has played UNO yet!**')
                    await ctx.send(embed=message)

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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**',
                                    color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['globalleaderboard']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'allowalerts', 'alerts', 'alert', 'aa'])
async def allowalerts(ctx, option=None):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'allowalerts' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['allowalerts']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['allowalerts']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['allowalerts']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['allowalerts']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['allowalerts']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['allowalerts']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['allowalerts'][
                             'Whitelist']) or ctx.message.author == ctx.guild.owner:
                if not option:
                    message = discord.Embed(title=prefix + 'allowalerts', color=discord.Color.red())
                    message.add_field(name='Description:', value='Allows alerts just for you', inline=False)
                    message.add_field(name='Usage:', value='`' + prefix + 'allowalerts <on|off|view>`', inline=False)
                    message.add_field(name='Example:', value='`' + prefix + 'aa on`', inline=False)
                    message.add_field(name='Aliases:', value='allowalerts, alerts, alert, aa')

                    await ctx.send(embed=message)

                else:
                    users_file = s3_resource.Object('unobot-bucket', 'users.json')
                    users = json.loads(users_file.get()['Body'].read().decode('utf-8'))

                    if option in ('view', 'list'):
                        if users[str(ctx.message.author.id)]['AllowAlerts']:
                            description = 'Enabled :white_check_mark:'
                        else:
                            description = 'Disabled :x:'

                        message = discord.Embed(title=ctx.message.author.name + '\'s alerts', description=description,
                                                color=discord.Color.red())

                        await ctx.send(embed=message)

                    elif option.lower() == 'on':
                        users[str(ctx.message.author.id)]['AllowAlerts'] = True

                        users_file.put(Body=json.dumps(users).encode('utf-8'))

                        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                    elif option.lower() == 'off':
                        users[str(ctx.message.author.id)]['AllowAlerts'] = False

                        users_file.put(Body=json.dumps(users).encode('utf-8'))

                        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**',
                                    color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['options']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'settings', 'set', 'sett', 'stngs', 'setting', 'stng'])
async def settings(ctx, setting=None, *, args=None):

    commands_file = s3_resource.Object('unobot-bucket', 'commands.json')
    commands = json.loads(commands_file.get()['Body'].read().decode('utf-8'))

    if 'settings' not in cooldowns[str(ctx.guild.id)]:
        if ((not commands[str(ctx.guild.id)]['settings']['BlacklistEnabled'] or not
        commands[str(ctx.guild.id)]['settings']['Blacklist'])
            or ctx.message.author.id not in commands[str(ctx.guild.id)]['settings']['Blacklist']) \
                and (not commands[str(ctx.guild.id)]['settings']['WhitelistEnabled'] or
                     commands[str(ctx.guild.id)]['settings']['Whitelist'] and ctx.message.author.id in
                     commands[str(ctx.guild.id)]['settings']['Whitelist']) or ctx.message.author == ctx.guild.owner:
            if not setting:
                message = discord.Embed(title='UNOBot Settings', color=discord.Color.red(),
                                        description='Adjusts how UNOBot works for the entire server.')
                message.add_field(name=':wrench: Command Customization:', value=prefix + '`settings commands`')
                message.add_field(name=':game_die: Default Game Settings:', value=prefix + '`settings dgs`')
                message.add_field(name=':arrows_counterclockwise: Reset UNOBot:', value=prefix + '`settings reset`',
                                  inline=False)
                message.add_field(name='Aliases: ', value='set, sett, stngs, setting, stng')

                await ctx.send(embed=message)

            elif setting == 'commands':
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

                    await ctx.send(embed=message)

                elif len(args.split()) == 1:
                    if args in cmds:
                        await cmd_info(ctx, args)
                    else:
                        await ctx.send(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings help`',
                            color=discord.Color.red()))

                elif len(args.split()) == 2:
                    s = args.split()[0]
                    b = args.split()[1]

                    if s in cmds:
                        if b == 'on':
                            commands[str(ctx.guild.id)][s]['Enabled'] = True
                            commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                        elif b == 'off':
                            commands[str(ctx.guild.id)][s]['Enabled'] = False
                            commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

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

                            await ctx.send(embed=message)

                        else:
                            await ctx.send(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.send(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

                elif len(args.split()) == 3:
                    s = args.split()[0].lower()
                    x = args.split()[1].lower()
                    y = args.split()[2].lower()

                    if s in cmds:
                        if x == 'cooldown':
                            if y == 'view':
                                await ctx.send(
                                    embed=discord.Embed(description='The **' + s + '** command has a cooldown of **'
                                                                    + str(
                                        commands[str(ctx.guild.id)][s]['Cooldown']) + ' seconds**.',
                                                        color=discord.Color.red()))
                            else:
                                await ctx.send(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings help`',
                                    color=discord.Color.red()))

                        elif x == 'whitelist' or x == 'blacklist':
                            if y == 'enable':
                                commands[str(ctx.guild.id)][s][x.capitalize() + 'Enabled'] = True
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                            elif y == 'disable':
                                commands[str(ctx.guild.id)][s][x.capitalize() + 'Enabled'] = False
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

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

                                await ctx.send(embed=message)

                            else:
                                await ctx.send(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                    color=discord.Color.red()))

                        else:
                            await ctx.send(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.send(embed=discord.Embed(
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

                                    await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                                except ValueError:
                                    await ctx.send(embed=discord.Embed(
                                        description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                        color=discord.Color.red()))

                            else:
                                await ctx.send(embed=discord.Embed(
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
                                        await ctx.send(embed=discord.Embed(
                                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                            color=discord.Color.red()))

                                        return

                                if commands[str(ctx.guild.id)][s][x.capitalize()]:
                                    commands[str(ctx.guild.id)][s][x.capitalize()].append(user.id)
                                else:
                                    commands[str(ctx.guild.id)][s][x.capitalize()] = [user.id]
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                            elif y == 'remove':
                                user_converter = UserConverter()
                                role_converter = RoleConverter()

                                try:
                                    user = await user_converter.convert(ctx, z)
                                except BadArgument:
                                    try:
                                        user = await role_converter.convert(ctx, z)
                                    except BadArgument:
                                        await ctx.send(embed=discord.Embed(
                                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                            color=discord.Color.red()))

                                        return

                                if commands[str(ctx.guild.id)][s][x.capitalize()]:
                                    commands[str(ctx.guild.id)][s][x.capitalize()].remove(user.id)

                                    if not commands[str(ctx.guild.id)][s][x.capitalize()]:
                                        commands[str(ctx.guild.id)][s][x.capitalize()] = None
                                commands_file.put(Body=json.dumps(commands).encode('utf-8'))

                                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                            else:
                                await ctx.send(embed=discord.Embed(
                                    description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                    color=discord.Color.red()))

                        else:
                            await ctx.send(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.send(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

                else:
                    await ctx.send(embed=discord.Embed(
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

                    await ctx.send(embed=message)

                elif args == 'view':
                    message = discord.Embed(title='Default Game Settings', color=discord.Color.red())

                    for s in dgs[str(ctx.guild.id)].keys():
                        if type(dgs[str(ctx.guild.id)][s]) == int:
                            message.add_field(name=s, value=str(dgs[str(ctx.guild.id)][s]))
                        elif dgs[str(ctx.guild.id)][s]:
                            message.add_field(name=s, value='Enabled :white_check_mark:')
                        else:
                            message.add_field(name=s, value='Disabled :x:')

                    await ctx.send(embed=message)

                elif len(args.split()) == 2:
                    s = args.split()[0]
                    x = args.split()[1].lower()

                    if s in default_dgs:
                        if x == 'on':
                            dgs[str(ctx.guild.id)][s] = True
                            dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                        elif x == 'off':
                            dgs[str(ctx.guild.id)][s] = False
                            dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

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
                                await ctx.send(
                                    embed=discord.Embed(description=':x: **' + s + '** is not a valid game setting.',
                                                        color=discord.Color.red()))

                                return

                            await ctx.send(embed=message)

                    else:
                        await ctx.send(embed=discord.Embed(
                            description=':x: **' + s + '** is not a game setting. Use `' + prefix + 'settings dgs view` for a list of settings.',
                            color=discord.Color.red()))

                elif len(args.split()) >= 3:
                    s = args.split()[0]
                    x = args.split()[1]
                    y = args.split()[2]

                    if s == 'StartingCards':
                        if x == 'set':
                            try:
                                if 3 < int(y) < 15:
                                    dgs[str(ctx.guild.id)][s] = int(y)
                                    dgs_file.put(Body=json.dumps(dgs).encode('utf-8'))

                                    await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
                                else:

                                    await ctx.send(
                                        embed=discord.Embed(description=':x: **You can only start with 3-15 cards.**',
                                                            color=discord.Color.red()))

                            except ValueError:
                                await ctx.send(embed=discord.Embed(
                                    description=':x: Please enter an integer.',
                                    color=discord.Color.red()))

                        else:
                            await ctx.send(embed=discord.Embed(
                                description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                                color=discord.Color.red()))

                    else:
                        await ctx.send(embed=discord.Embed(
                            description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                            color=discord.Color.red()))

            elif setting == 'reset':
                message = discord.Embed(description=':warning: Are you sure you want to reset UNOBot?'
                                                    ' **Settings including command settings, server stats, and ongoing games will be lost.**\n\n'
                                                    'Respond with **CONFIRM** in 30 seconds to confirm and reset UNOBot.',
                                        color=discord.Color.red())
                resets.append(ctx.guild.id)
                await ctx.send(embed=message)

                def check(m):
                    return m.content == 'CONFIRM' and (
                            not commands[str(ctx.guild.id)]['settings']['WhitelistEnabled'] or (
                            commands[str(ctx.guild.id)]['settings']['Whitelist'] and ctx.message.author.id in
                            commands[str(ctx.guild.id)]['settings'][
                                'Whitelist'] or ctx.message.author == ctx.guild.owner))

                try:
                    await client.wait_for('message', check=check, timeout=30.0)
                except asyncio.TimeoutError:
                    await ctx.send(embed=discord.Embed(description=':ok_hand: **OK, UNOBot will not reset.**',
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
            await ctx.send(
                embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                    color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['settings']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'startgame', 'start', 'sg'])
async def startgame(ctx, *, args=None):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if ctx.channel.category.name != 'UNO-GAME':
        if 'startgame' not in cooldowns[str(ctx.guild.id)] and ctx.channel.category.name != 'UNO-GAME':
            if commands[str(ctx.guild.id)]['startgame']['Enabled']:
                if ((not commands[str(ctx.guild.id)]['startgame']['BlacklistEnabled'] or not
                commands[str(ctx.guild.id)]['startgame']['Blacklist'])
                    or ctx.message.author.id not in commands[str(ctx.guild.id)]['startgame']['Blacklist']) \
                        and (not commands[str(ctx.guild.id)]['startgame']['WhitelistEnabled'] or
                             commands[str(ctx.guild.id)]['startgame']['Whitelist'] and ctx.message.author.id in
                             commands[str(ctx.guild.id)]['startgame'][
                                 'Whitelist']) or ctx.message.author == ctx.guild.owner:
                    if str(ctx.guild.id) not in games:
                        dgs = json.loads(s3_resource.Object('unobot-bucket', 'dgs.json').get()['Body'].read().decode('utf-8'))

                        games[str(ctx.guild.id)] = {'seconds': 40}
                        games[str(ctx.guild.id)]['settings'] = dgs[str(ctx.guild.id)]

                        user_options = json.loads(s3_resource.Object('unobot-bucket', 'users.json').get()['Body'].read().decode('utf-8'))

                        if args:
                            a = args.split()
                            for i in range(len(a)):
                                user_converter = UserConverter()

                                try:
                                    user = await user_converter.convert(ctx, a[i])

                                    for guild in client.guilds:
                                        user_options[str(user.id)].pop(str(guild.id), None)
                                    games[str(ctx.guild.id)][str(user.id)] = user_options[str(user.id)]
                                    games[str(ctx.guild.id)][str(user.id)]['cards'] = []

                                except BadArgument:
                                    if a[i] in (
                                            'DrawUntilMatch', 'DisableJoin', 'QuickStart', 'SpectateGame', 'StackCards',
                                            'Flip', '7-0'):
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
                                                    await ctx.send(
                                                        embed=discord.Embed(
                                                            description=':x: **You can only start with 3-15 cards.**',
                                                            color=discord.Color.red()))

                                                    del games[str(ctx.guild.id)]

                                                    return

                                            except ValueError:
                                                await ctx.send(embed=discord.Embed(
                                                    description=':x: Please enter an integer for the number of starting cards.',
                                                    color=discord.Color.red()))

                                                del games[str(ctx.guild.id)]

                                                return

                                        else:
                                            await ctx.send(embed=discord.Embed(
                                                description=':x: I don\'t understand your command, use `' + prefix + 'commands startgame`',
                                                color=discord.Color.red()))

                                            del games[str(ctx.guild.id)]

                                            return

                                    else:
                                        await ctx.send(embed=discord.Embed(
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
                            message.set_footer(
                                text='React with \'✋\' to join, \'▶️\' to force start, and \'❌\' to cancel the game.')

                            if len(games[str(ctx.guild.id)].keys()) == 2:
                                message.add_field(name='Players:', value='None', inline=False)
                            else:
                                p = ""
                                for key in games[str(ctx.guild.id)]:
                                    if key in ('settings', 'seconds'):
                                        continue
                                    else:
                                        p += (':small_blue_diamond: ' + (client.get_user(int(key))).name + "\n")

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

                            message.add_field(name='Game Creator:', value=str(ctx.message.author), inline=False)

                            e = await ctx.send(embed=message)
                            eid = e.id

                            await e.add_reaction('✋')
                            await e.add_reaction('▶️')
                            await e.add_reaction('❌')

                            while True:
                                if str(ctx.guild.id) not in games or games[str(ctx.guild.id)]['seconds'] == -2:
                                    break

                                if games[str(ctx.guild.id)]['seconds'] == -1:
                                    del games[str(ctx.guild.id)]

                                    break

                                games[str(ctx.guild.id)]['seconds'] -= 10
                                m = (await ctx.fetch_message(eid)).embeds[0]

                                if games[str(ctx.guild.id)]['seconds'] == 0:
                                    await e.clear_reaction('✋')
                                    await e.clear_reaction('▶️')
                                    await e.clear_reaction('❌')

                                    if len(games[str(ctx.guild.id)].keys()) > 3:
                                        players = games[str(ctx.guild.id)]

                                        message_dict = m.to_dict()
                                        message_dict['title'] = 'A game of UNO has started!'
                                        message_dict[
                                            'description'] = ':white_check_mark: A game of UNO has started. Go to your UNO channel titled with your username.'
                                        del message_dict['footer']

                                        await e.edit(embed=discord.Embed.from_dict(message_dict))

                                        await game_setup(ctx, players)

                                        games[str(ctx.guild.id)]['creator'] = ctx.message.author.id

                                    else:
                                        message_dict = m.to_dict()
                                        message_dict['title'] = 'A game of UNO failed to start!'
                                        message_dict[
                                            'description'] = ':x: Not enough players! At least 2 players are needed (Bots do not count).'

                                        del message_dict['footer']
                                        del games[str(ctx.guild.id)]

                                        await e.edit(embed=discord.Embed.from_dict(message_dict))

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
                            if len(games[str(ctx.guild.id)].keys()) > 3:
                                players = games[str(ctx.guild.id)]

                                await game_setup(ctx, players)

                                games[str(ctx.guild.id)]['creator'] = ctx.message.author.id

                                message = discord.Embed(title='A game of UNO has started!',
                                                        description=':white_check_mark: A game of UNO has started. Go to your UNO channel titled with your username.',
                                                        color=discord.Color.red())

                                p = ""
                                for key in games[str(ctx.guild.id)]:
                                    if key in ('settings', 'seconds', 'cards', 'current', 'player', 'creator'):
                                        continue
                                    else:
                                        p += (':small_blue_diamond: ' + (client.get_user(int(key))).name + "\n")

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

                                message.add_field(name='Game Creator:', value=str(ctx.message.author), inline=False)

                                await ctx.send(embed=message)

                            else:
                                message = discord.Embed(title='A game of UNO failed to start!',
                                                        description=':x: Not enough players! At least 2 players are needed (Bots do not count).',
                                                        color=discord.Color.red())

                                if len(games[str(ctx.guild.id)].keys()) == 2:
                                    message.add_field(name='Players:', value='None', inline=False)
                                else:
                                    p = ""
                                    for key in games[str(ctx.guild.id)]:
                                        if key in ('settings', 'seconds'):
                                            continue
                                        else:
                                            p += (str(await client.fetch_user(int(key))) + "\n")

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
                                message.add_field(name='Game Creator:', value=str(ctx.message.author), inline=False)

                                await ctx.send(embed=message)

                                del games[str(ctx.guild.id)]

                        if commands[str(ctx.guild.id)]['startgame']['Cooldown'] > 0:
                            cooldowns[str(ctx.guild.id)].append('startgame')

                            def check(message):
                                return len(message.content.split()) == 6 \
                                       and message.content.split()[0] in (
                                           prefix + 'settings', prefix + 'set', prefix + 'sett', prefix + 'stngs',
                                           prefix + 'setting',
                                           prefix + 'stng') \
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
                        await ctx.send(embed=discord.Embed(description=':x: **A game is already underway!**',
                                                           color=discord.Color.red()))

                else:
                    await ctx.send(
                        embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                            color=discord.Color.red()))

            else:
                await ctx.send(
                    embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

        else:
            await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
                commands[str(ctx.guild.id)]['startgame']['Cooldown']) + ' seconds.**', color=discord.Color.red()))

    else:
        await ctx.send(
            embed=discord.Embed(description=':x: **You can\'t use this command here!**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'endgame', 'eg', 'stop'])
async def endgame(ctx):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'endgame' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['endgame']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['endgame']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['endgame']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['endgame']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['endgame']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['endgame']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['endgame'][
                             'Whitelist']) or ctx.message.author == ctx.guild.owner or ctx.message.author == ctx.guild.get_member(
                games[str(ctx.guild.id)]['creator']):
                if ctx.channel.category.name != 'UNO-GAME':
                    if str(ctx.guild.id) in games and str(ctx.guild.id) not in ending:
                        for channel in [x for x in ctx.guild.text_channels if x.category.name == 'UNO-GAME']:
                            await channel.send(embed=discord.Embed(
                                description=':warning: **' + ctx.message.author.name + ' is ending the game!**',
                                color=discord.Color.red()))

                        ending.append(str(ctx.guild.id))
                        await game_shutdown(games[str(ctx.guild.id)], None, ctx.guild)

                    else:
                        await ctx.send(
                            embed=discord.Embed(description=':x: **The game doesn\'t exist.**',
                                                color=discord.Color.red()))

                else:
                    await ctx.send(
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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['endgame']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'leavegame', 'leave', 'quit', 'lg', 'quitgame'])
async def leavegame(ctx):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'leavegame' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['leavegame']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['leavegame']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['leavegame']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['leavegame']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['leavegame']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['leavegame']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['leavegame'][
                             'Whitelist']) or ctx.message.author == ctx.guild.owner:
                if ctx.channel.category.name == 'UNO-GAME':
                    if str(ctx.guild.id) in games and str(ctx.message.author.id) in games[str(ctx.guild.id)]:
                        n = None
                        p = list(games[str(ctx.guild.id)].keys())
                        p.remove('settings')
                        p.remove('seconds')
                        p.remove('cards')
                        p.remove('current')
                        p.remove('player')
                        p.remove('creator')

                        temp = iter(p)
                        for key in temp:
                            if key == str(ctx.message.author.id):
                                n = ctx.guild.get_member(int(next(temp, next(iter(p)))))
                                break

                        del games[str(ctx.guild.id)][str(ctx.message.author.id)]

                        if len(games[str(ctx.guild.id)]) - 6 >= 2:
                            await ctx.channel.delete()

                            for channel in ctx.message.category.text_channels:
                                await channel.send(
                                    discord.Embed(description=':warning: **' + ctx.message.author.name + '** left.'))

                            if ctx.message.author.id == games[str(ctx.guild.id)]['player']:
                                await display_cards(n)

                        else:
                            for channel in ctx.channel.category.text_channels:
                                await channel.send(
                                    embed=discord.Embed(
                                        description=':x: Since not enough players are left, ending game...',
                                        color=discord.Color.red()))

                            ending.append(str(ctx.guild.id))
                            await game_shutdown(games[str(ctx.guild.id)], None, ctx.guild)

                else:
                    await ctx.send(
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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['leavegame']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'kick', 'remove'])
async def kick(ctx, user):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'kick' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['kick']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['kick']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['kick']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['kick']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['kick']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['kick']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['kick']['Whitelist']) or ctx.message.author == ctx.guild.owner:
                user_converter = UserConverter()

                try:
                    player = await user_converter.convert(ctx, user)
                except BadArgument:
                    await ctx.send(embed=discord.Embed(
                        description=':x: I don\'t understand your command, use `' + prefix + 'settings`',
                        color=discord.Color.red()))

                    return

                if str(ctx.guild.id) in games and str(player.id) in games[str(ctx.guild.id)] and str(
                        ctx.guild.id) not in ending:
                    n = None
                    p = list(games[str(ctx.guild.id)].keys())
                    p.remove('settings')
                    p.remove('seconds')
                    try:
                        p.remove('cards')
                    except ValueError:
                        pass
                    try:
                        p.remove('current')
                    except ValueError:
                        pass
                    try:
                        p.remove('player')
                    except ValueError:
                        pass
                    try:
                        p.remove('creator')
                    except ValueError:
                        pass

                    temp = iter(p)
                    for key in temp:
                        if key == str(player.id):
                            n = ctx.guild.get_member(int(next(temp, next(iter(p)))))
                            break

                    del games[str(ctx.guild.id)][str(player.id)]

                    if len(games[str(ctx.guild.id)]) - 6 >= 2:
                        await discord.utils.get(ctx.guild.text_channels,
                                                name=player.name.lower().replace(' ', '-').replace('.',
                                                                                                   '') + '-uno-channel').delete()

                        for channel in [x for x in ctx.guild.text_channels if x.category.name == 'UNO-GAME']:
                            await channel.send(
                                discord.Embed(description=':warning: **' + player.name + '** was kicked.'))

                        if player.id == games[str(ctx.guild.id)]['player']:
                            await display_cards(n)

                        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                    else:
                        for channel in [x for x in ctx.guild.text_channels if x.category.name == 'UNO-GAME']:
                            await channel.send(
                                embed=discord.Embed(description=':x: Since not enough players are left, ending game...',
                                                    color=discord.Color.red()))

                        ending.append(str(ctx.guild.id))

                        await game_shutdown(games[str(ctx.guild.id)], None, ctx.guild)

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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['kick']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


@client.command(aliases=[chr(173) + 'spectate', 'spec'])
async def spectate(ctx, arg):

    commands = json.loads(s3_resource.Object('unobot-bucket', 'commands.json').get()['Body'].read().decode('utf-8'))

    if 'spectate' not in cooldowns[str(ctx.guild.id)]:
        if commands[str(ctx.guild.id)]['spectate']['Enabled']:
            if ((not commands[str(ctx.guild.id)]['spectate']['BlacklistEnabled'] or not
            commands[str(ctx.guild.id)]['spectate']['Blacklist'])
                or ctx.message.author.id not in commands[str(ctx.guild.id)]['spectate']['Blacklist']) \
                    and (not commands[str(ctx.guild.id)]['spectate']['WhitelistEnabled'] or
                         commands[str(ctx.guild.id)]['spectate']['Whitelist'] and ctx.message.author.id in
                         commands[str(ctx.guild.id)]['spectate']['Whitelist']) or ctx.message.author == ctx.guild.owner:
                role = discord.utils.get(ctx.guild.roles, name='UNO Spectator')

                if arg.lower() == 'on' and role not in ctx.message.author.roles:
                    await ctx.message.author.add_roles(role)

                    await ctx.send(embed=discord.Embed(
                        description=':thumbsup: You now have the **UNO Spectator** role. You can now spectate any UNO game with the **SpectateGame** setting on.',
                        color=discord.Color.red()))

                elif arg.lower() == 'off' and role in ctx.message.author.roles:
                    await ctx.message.author.remove_roles(role)

                    await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

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
                await ctx.send(
                    embed=discord.Embed(description=':lock: **You do not have permission to use this command.**',
                                        color=discord.Color.red()))

        else:
            await ctx.send(
                embed=discord.Embed(description=':x: **The command is disabled.**', color=discord.Color.red()))

    else:
        await ctx.send(embed=discord.Embed(description=':stopwatch: **You can only use this command every ' + str(
            commands[str(ctx.guild.id)]['spectate']['Cooldown']) + ' seconds.**', color=discord.Color.red()))


if __name__ == '__main__':
    main()
