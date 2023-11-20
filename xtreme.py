import discord
import asyncio
import typing
import random
import time
import datetime
import os
import re
from dotenv import load_dotenv
import cv2
import textwrap
import mysql.connector
#import psycopg2
import math
import numpy as np
import hashslingingslasher as hasher
from urllib.request import Request, urlopen
from urllib.parse import quote
from difflib import get_close_matches
from bs4 import BeautifulSoup as soup
from discord.utils import get
from discord.ext import tasks, commands
from discord.ui import Button, View
from utilities import has_perms, format_to_k, format_from_k, pickflower, scorefp

load_dotenv()

conn = mysql.connector.connect(
    user = 'u79588_E6O83yeRrg',
    password = '+AYyBYT6!Npzz^XnXp5+e4Rm',
    host = '78.108.218.47',
    database = 's79588_xtreme-db',
    autocommit = True)

c = conn.cursor(dictionary=True, buffered=True)
c.execute("SET SESSION wait_timeout=100000")

# c.execute("DROP TABLE rsmoney")
c.execute("""CREATE TABLE if not exists rsmoney (
              id bigint,
              rs3 integer,
              osrs integer,
              rs3total bigint,
              osrstotal bigint,
              rs3week bigint,
              osrsweek bigint,
              clientseed text,
              privacy bit,
              bronze integer,
              iron integer,
              steel integer,
              mithril integer,
              adamant integer,
              rune integer,
              dragon integer,
              noxious integer,
              tickets integer,
              weeklydate text,
              xp integer,
              lastgained integer,
              claimed bit,
              defaultc text,
              rs3profit bigint,
              osrsprofit bigint
              )""")
c.execute("INSERT INTO rsmoney VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", ("546184449373634560",0,0,0,0,0,0,"None",False,0,0,0,0,0,0,0,0,0,"2020-01-01 00:00:00",0,0,False,'07',0,0))

# c.execute("DROP TABLE data")
c.execute("""CREATE TABLE if not exists data (
              seedreset text,
              serverseed text,
              yesterdayseed text,
              nonce integer,
              jackpotroll integer,
              daily integer
              )""")
c.execute("INSERT INTO data VALUES (%s, %s, %s, %s, %s, %s)", (time.strftime("%d"), hasher.create_seed(), "None", 0, 1000, 100))

c.execute("DROP TABLE bj")
c.execute("""CREATE TABLE if not exists bj (
                id bigint,
                deck text,
                botcards text,
                playercards text,
                botscore integer,
                playerscore integer,
                bet integer,
                currency text,
                messageid text,
                channelid text,
                split text
                )""")

# c.execute("DROP TABLE jackpot")
c.execute("""CREATE TABLE if not exists jackpot (
              id bigint,
              bet integer,
              chance float
              )""")

#c.execute("DROP TABLE cash")
c.execute("""CREATE TABLE if not exists cash (
              id text,
              way text,
              code integer,
              currency text,
              amount integer
              )""")

#c.execute("DROP TABLE daily")
c.execute("""CREATE TABLE if not exists daily (
              prize integer,
              people text(1000),
              channelid text
              )""")

# c.execute("DROP TABLE openHosts")
c.execute("""CREATE TABLE if not exists openHosts (
            id bigint,
            streak text
            )""")

#c.execute("DROP TABLE dice")
c.execute("""CREATE TABLE if not exists dice (
            playerid bigint,
            hostid bigint,
            bet integer,
            currency text,
            roll integer,
            first bigint
            )""")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Subscribe to the privileged members intent.
game = discord.Game("My Prefix Is !")
bot = commands.Bot(command_prefix = '!', status=discord.Status.online, activity=game, fetch_offline_members=True, case_insensitive=True, intents=intents)

def add_member(userid, rs3, osrs):
    c.execute("INSERT INTO rsmoney VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (userid, rs3, osrs, 0, 0, 0, 0, 'Clientseed', False, 0, 0, 0, 0, 0, 0, 0, 0, 0, "2020-01-01 00:00:00", 0, 0, False, '07', 0, 0))

def getvalue(userid, column, table):
    if isinstance(column, list):
        returned = []
        for i in column:
            returned.append(getvalue(userid, i, table))
        return returned
    else:
        strings = ['clientseed', 'seedreset', 'serverseed', 'yesterdayseed', 'deck', 'botcards', 'playercards', 
                    'currency', 'messageid', 'channelid', 'bets', 'streak', 'weeklydate', 'people', 'defaultc', 'type', 'split']
        booleans = ['privacy', 'claimed']

        if column == '07':
            column = 'osrs'

        c.execute(f"SELECT id FROM rsmoney WHERE id={userid}")
        tester = c.fetchall()
        if not tester:
            print('New Member')
            add_member(int(userid), 0, 0)
            return 0

        c.execute(f"SELECT {column} FROM {table} WHERE id={userid}")
        if column in booleans:
            return bool(int(c.fetchone()[column]))
        elif column in strings:
            return str(c.fetchone()[column])
        else:
            return int(c.fetchone()[column])

def update_money(userid, amount, currency):
    rs3 = getvalue(int(userid), currency, 'rsmoney')
    osrs = getvalue(int(userid), currency, 'rsmoney')

    if currency == '07':
        c.execute('UPDATE rsmoney SET osrs={} WHERE id={}'.format(osrs + amount, userid))
    elif currency == 'rs3':
        c.execute('UPDATE rsmoney SET rs3={} WHERE id={}'.format(rs3 + amount, userid))

def is_enough(amount, currency):
    if currency == 'rs3':
        if amount < 1000:
            words = 'The minimum amount you can bet is **1m** gp RS3.'
            return (False, words)
        else:
            return (True, ' ')

    elif currency == '07':
        if amount < 250:
            words = 'The minimum amount you can bet is **250k** gp 07.'
            return (False, words)
        else:
            return (True, ' ')

def ticketbets(userid, bet, currency):
    if currency == 'rs3':
        totalbet = getvalue(userid, 'rs3total', 'rsmoney')
        c.execute('UPDATE rsmoney SET rs3total={} WHERE id={}'.format(totalbet + bet, userid))
        totalbet = getvalue(userid, 'rs3week', 'rsmoney')
        c.execute('UPDATE rsmoney SET rs3week={} WHERE id={}'.format(totalbet + bet, userid))
    elif currency == '07':
        totalbet = getvalue(userid, 'osrstotal', 'rsmoney')
        c.execute('UPDATE rsmoney SET osrstotal={} WHERE id={}'.format(totalbet + bet, userid))
        totalbet = getvalue(userid, 'osrsweek', 'rsmoney')
        c.execute('UPDATE rsmoney SET osrsweek={} WHERE id={}'.format(totalbet + bet, userid))

def getrandint(userid):
    c.execute('SELECT serverseed FROM data')
    guildseed = str(c.fetchone()['serverseed'])
    c.execute('SELECT nonce FROM data')
    nonce = int(c.fetchone()['nonce'])
    clientseed = getvalue(userid, 'clientseed', 'rsmoney')
    randint = hasher.getrandint(guildseed, clientseed, nonce)
    c.execute('UPDATE data SET nonce={}'.format(int(nonce + 1)))
    return randint, nonce
  
def scorebj(userid, cards, player):
    score, aces, soft = 0, 0, ''
    for i in cards.split('|'):
        if i == '':
            continue
        elif i[0] == 'a':
            aces += 1
        elif (i[0] == 'j') or (i[0] == 'q') or (i[0] == 'k') or (i[0] == 't'):
            score += 10
        else:
            score += int(i[0])
    for i in range(aces):
        if (aces > 1) or (score > 10):
            score += 1
        else:
            score += 11
            soft = 'Soft '
    if player:
        c.execute('UPDATE bj SET playerscore={} WHERE id={}'.format(score, userid))
    elif player == False:
        c.execute('UPDATE bj SET botscore={} WHERE id={}'.format(score, userid))
    return (score, soft)

def printbj(user, stood, description, color):
    def cardsToEmoji(cards, stood, is_bot):
        emojiCards = ''
        size = 0
        if (stood == False) and is_bot:
            size = 1
            emojiCards += str(get(bot.emojis, name='cardback'))
        for i in (cards.split("|"))[size:]:
            for emoji in bot.emojis:
                if emoji.name == i:
                    emojid = emoji.id
                    emojiCards += ("<:"+str(i)+":"+str(emojid)+">")
        return emojiCards

    botcards = getvalue(user.id, 'botcards', 'bj')
    playercards = getvalue(user.id, 'playercards', 'bj')
    split = getvalue(user.id, 'split', 'bj')
    botscore = scorebj(user.id, botcards, False)[0]
    playerscore = scorebj(user.id, playercards, True)
    splitscore = scorebj(user.id, split[1:], 'Split') if split != 'None' else None
    embed = discord.Embed(description=description, color=color)
    
    if split != 'None':
        embed.set_author(name=user.display_name + "'s Blackjack Game - Split", icon_url=user.display_avatar)
    else:
        embed.set_author(name=user.display_name + "'s Blackjack Game", icon_url=user.display_avatar)
    if 'y' in split:
        embed.add_field(name=user.display_name + "'s First Hand - " + playerscore[1] + str(playerscore[0]), value=cardsToEmoji(playercards, stood, False), inline=True)
        embed.add_field(name=user.display_name + "'s Second Hand - " + splitscore[1] + str(splitscore[0]), value=cardsToEmoji(split[1:], stood, False), inline=True)
    elif 'z' in split:
        embed.add_field(name=user.display_name + "'s First Hand - " + splitscore[1] + str(splitscore[0]), value=cardsToEmoji(split[1:], stood, False), inline=True)
        embed.add_field(name=user.display_name + "'s Second Hand - " + playerscore[1] + str(playerscore[0]), value=cardsToEmoji(playercards, stood, False), inline=True)
    else:
        embed.add_field(name=user.display_name + "'s Hand - " + playerscore[1] + str(playerscore[0]), value=cardsToEmoji(playercards, stood, False), inline=True)
    if stood:
        embed.add_field(name="Dealer's Hand - " + str(botscore), value=cardsToEmoji(botcards, stood, True), inline=True)
    else:
        embed.add_field(name="Dealer's Hand - ?", value=cardsToEmoji(botcards, stood, True), inline=True)
    
    return embed

def drawcard(userid, player):
    deck = getvalue(userid, 'deck', 'bj')
    decklist = deck.split('|')

    index = random.randint(0, len(decklist) - 1)
    card = decklist[index]
    del decklist[index]
    deck = '|'.join(decklist)

    if player:
        playercards = getvalue(userid, 'playercards', 'bj')
        c.execute("UPDATE bj SET playercards='{}' WHERE id={}".format((str(playercards) + str(card)) + '|', userid))
    elif player == False:
        botcards = getvalue(userid, 'botcards', 'bj')
        c.execute("UPDATE bj SET botcards='{}' WHERE id={}".format((str(botcards) + str(card)) + '|', userid))
    
    c.execute("UPDATE bj SET deck='{}' WHERE id={}".format(deck, userid))

def bjresult(user, bet, currency, botscore, playerscore, playercards):
    if playerscore > 21:
        embed = printbj(user, True, 'Sorry. You busted and lost.', 16711718)
        win = False
    elif botscore > 21:
        embed = printbj(user, True, ('Dealer Busts. You win **' + format_from_k(bet * 2)) + '**!', 3407616)
        win = True
        update_money(user.id, bet * 2, currency)
    elif (playerscore == 21) and (len(playercards.split('|')) == 3) and (playercards.count('a') == 1) and ((playercards.count('t') == 1) or (playercards.count('j') == 1) or (playercards.count('q') == 1) or (playercards.count('k') == 1)):
        embed = printbj(user, True, ('You got a blackjack! You win **' + format_from_k(bet * 2)) + '**!', 3407616)
        win = True
        update_money(user.id, bet * 2, currency)
    elif botscore == playerscore:
        embed = printbj(user, True, 'Tie! Money Back.', 16776960)
        win = 'tie'
        update_money(user.id, bet, currency)
    elif playerscore > botscore:
        embed = printbj(user, True, ("Your score is higher than the dealer's. You win **" + format_from_k(bet * 2)) + '**!', 3407616)
        win = True
        update_money(user.id, bet * 2, currency)
    elif botscore > playerscore:
        embed = printbj(user, True, "The dealer's score is higher than yours. You lose.", 16711718)
        win = False

    return embed

def openkey(kind):
    if kind == 'bronze':
        ranges = [2, 6, 9, 18, 40, 46, 60, 77, 75, 90, 92, 106, 64, 97, 86, 76, 64, 58, 50, 60, 34, 40, 40, 40, 40, 40, 30, 30, 20, 20, 20, 10, 10]
    elif kind == 'iron':
        ranges = [1, 2, 3, 4, 5, 10, 20, 30, 42, 54, 71, 75, 75, 81, 77, 65, 60, 44, 40, 35, 25, 20, 25]
    elif kind == 'steel':
        ranges = [1, 2, 3, 4, 6, 10, 15, 33, 40, 40, 54, 50, 63, 40, 56, 59, 42, 35, 31, 28, 25]
    elif kind == 'mithril':
        ranges = [2, 3, 5, 15, 18, 22, 29, 30, 40, 40, 44, 52, 70, 80, 90, 70, 60, 65, 50, 47, 40, 35, 25]
    elif kind == 'adamant':
        ranges = [1, 1, 3, 5, 10, 12, 22, 28, 42, 48, 56, 52, 58, 52, 30, 20, 20, 38, 34, 30, 26, 22, 29, 15, 10]
    elif kind == 'rune':
        ranges = [2, 2, 4, 6, 8, 10, 20, 40, 80, 90, 85, 86, 44, 61, 56, 50, 40, 37, 34, 31, 28, 25, 30, 20, 10, 5]
    elif kind == 'dragon':
        ranges = [1, 2, 4, 8, 10, 22, 25, 35, 63, 70, 80, 81, 82, 40, 45, 66, 55, 34, 51, 41, 38, 27, 19, 20, 15, 10]
    elif kind == 'noxious':
        ranges = [1, 1, 2, 4, 6, 8, 10, 30, 62, 40, 69, 65, 71, 54, 61, 94, 59, 75, 60, 20, 25]

    chances = []
    
    for i in ranges:
        chances.append(i / sum(ranges))
    
    return random.choices(population=range(0, len(ranges)), weights=chances, k=1)

def roll_jackpot():
    c.execute('SELECT * FROM jackpot')
    bets = c.fetchall()
    total = sum((x['bet'] for x in bets))
    chances = []
    
    for i in bets:
        chances.append(i['chance'] / 100)
    
    winner = random.choices(population=bets, weights=chances, k=1)[0]
    update_money(winner['id'], total - (total * 0.05), '07')
    c.execute("DROP TABLE jackpot")
    c.execute("""CREATE TABLE jackpot (
                    id bigint,
                    bet integer,
                    chance float
                    )""")
    embed = discord.Embed(description='<@' + str(winner['id']) + '> has won **' + format_from_k(int(total - (total * 0.05))) + '** from the jackpot with a chance of **' + str(winner['chance']) + '%**!', color=5056466)
    embed.set_footer(text="Use '!add (amount)' to start a new jackpot game")
    embed.set_author(name='Jackpot Winner')
    return embed

def print_jackpot(ctx, rollAmount):
    c.execute('SELECT * FROM jackpot')
    bets = c.fetchall()
    total = sum((x['bet'] for x in bets))
    embed = discord.Embed(description='Jackpot Value: **' + format_from_k(total) + '**\n*This jackpot will end once the pot reaches: **' + format_from_k(rollAmount) + '***\n\nUse `!add (amount in 07)` to contribute to the jackpot.', color=5056466)
    
    for i in bets:
        chance = round((i['bet'] / total) * 100, 3)
        c.execute('UPDATE jackpot SET chance={} WHERE id={}'.format(float(chance), i['id']))
        try:
            name = (ctx.guild.get_member(i['id'])).display_name
        except:
            name = 'Deleted User'
        embed.add_field(name=name, value='Bet - *' + format_from_k(i['bet']) + '* | Chance of Winning - *' + str(chance) + '%*', inline=False)
    embed.set_author(name='Jackpot Bets', icon_url=ctx.guild.icon)
    embed.set_footer(text='*You can only bet 07 gold on the Jackpot game')
    return embed, total

def convert_currency(currency):
    if currency == 'osrs':
        return '07'
    else:
        return str(currency).lower()

async def reset_weekly(guild):
    prime = get(guild.roles, name='Prime')
    for member in prime.members:
        rs3 = getvalue(member.id, 'rs3week', 'rsmoney')
        osrs = getvalue(member.id, 'osrsweek', 'rsmoney')
        if (rs3 < 2_500_000 and osrs < 250_000):
            await member.remove_roles(prime)

    c.execute('SELECT id FROM rsmoney WHERE rs3week >= 2500000 OR osrsweek >= 250000')
    ids = c.fetchall()
    if ids:
        for i in ids:
            try:
                member = guild.get_member(i['id'])
                await member.add_roles(prime)
            except:
                None

    c.execute('SELECT id, rs3week, osrsweek FROM rsmoney WHERE rs3week >= 10000000 OR osrsweek >= 10000000')
    stats = c.fetchall()
    if stats:
        for i in stats:
            if i['rs3week'] >= 30_000_000:
                update_money(i['id'], 300_000, 'rs3')
            elif i['rs3week'] >= 20_000_000:
                update_money(i['id'], 200_000, 'rs3')
            elif i['rs3week'] >= 10_000_000:
                update_money(i['id'], 100_000, 'rs3')

            if i['osrsweek'] >= 30_000_000:
                update_money(i['id'], 300_000, '07')
            elif i['osrsweek'] >= 20_000_000:
                update_money(i['id'], 200_000, '07')
            elif i['osrsweek'] >= 10_000_000:
                update_money(i['id'], 100_000, '07')

    c.execute('UPDATE rsmoney SET rs3week = 0')
    c.execute('UPDATE rsmoney SET osrsweek = 0')

###########################################################################################################################################################


@tasks.loop(hours = 1)
async def daily_weekly():
    print('Daily Weekly Called')
    c.execute('SELECT seedreset FROM data')
    lastdate = str(c.fetchone()['seedreset'])
    today = str(time.gmtime()[2])
    if today != lastdate:
        channel = bot.get_channel(876447989214887976)
        c.execute('SELECT serverseed FROM data')
        guildseed = str(c.fetchone()['serverseed'])
        newseed = hasher.create_seed()
        c.execute("UPDATE data SET serverseed='{}'".format(newseed))
        c.execute("UPDATE data SET yesterdayseed='{}'".format(guildseed))
        c.execute('UPDATE data SET seedreset={}'.format(today))
        c.execute('UPDATE data SET nonce=0')
        embed = discord.Embed(color=16724721)
        embed.set_author(name='🌱 Server Seed Updates - Click To Verify Bets', url='https://dicesites.com/primedice/verifier')
        embed.add_field(name="Yesterday's Server Seed Unhashed", value=guildseed, inline=True)
        embed.add_field(name="Yesterday's Server Seed Hashed", value=hasher.hash(guildseed), inline=True)
        embed.add_field(name="Today's Server Seed Hashed", value=hasher.hash(newseed), inline=True)
        await channel.send(embed=embed)
        
        ################################

        if datetime.datetime.today().weekday() == 0:
            await reset_weekly(channel.guild)

        ################################

        c.execute('SELECT * FROM daily')
        daily = c.fetchone()
        channelid = int(daily['channelid'])
        people = str(daily['people'])[:-1]
        amount = format_from_k(int(daily['prize']))
        dailyChannel = bot.get_channel(channelid)
        category = dailyChannel.category
        winner = ''

        if people != '':
            winner = random.choice(people.split('|'))
            words = '<@' + winner + "> has won the previous __daily giveaway__ and gained **" + amount + " 07**!\n\nUse `!daily` to enter today's giveaway! The following people have entered:"
            update_money(int(winner), format_to_k(amount), '07')
        else:
            words = 'Not enough people entered to choose a winner :cry:'
            
        await dailyChannel.delete()
        newChannel = await channel.guild.create_text_channel('Daily Giveaway', category=category)
        await newChannel.set_permissions(channel.guild.default_role, send_messages=False)
        embed = discord.Embed(description=words, color=7354353)
        embed.set_author(name='Giveaway Results', icon_url=str(channel.guild.icon))
        await newChannel.send(embed=embed)
        c.execute("UPDATE daily SET people='{}'".format(''))
        c.execute('UPDATE daily SET channelid={}'.format(str(newChannel.id)))


  
@bot.event
async def on_ready():
    bot_room = bot.get_channel(882466336117260309)
    await bot_room.send('Bot Logged In!')
    print('Bot Logged In!')
    daily_weekly.start()

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(864276642515648513)
    memberRole = get(member.guild.roles, name='OSRS Mobile Secrets Member')
    embed = discord.Embed(description='Welcome to OSRS Mobile Secrets, <@' + str(member.id) + '>! You are member **#' + str(member.guild.member_count) + "**! Use `!claim (RS3 or 07)` for a free 5m RS3 or 1m 07!", color=15925108)
    embed.set_author(name='Welcome Message', icon_url=member.display_avatar)
    await channel.send(embed=embed)
    await member.add_roles(memberRole)

@bot.event
async def on_message(message):
    message.content = message.content.lower()

    if message.author == bot.user:
        return

    if message.content.startswith('!') or message.content.startswith(';') or message.author.bot:
        None
    else:
        lastGained = getvalue(message.author.id, 'lastgained', 'rsmoney')
        xp = getvalue(message.author.id, 'xp', 'rsmoney')
        current = int(datetime.datetime.now().minute)
        if lastGained != current:
            c.execute('UPDATE rsmoney SET xp = {} WHERE id = {}'.format(xp + random.randint(10,25) , message.author.id))
            c.execute('UPDATE rsmoney SET lastgained = {} WHERE id = {}'.format(current, message.author.id))

    if isinstance(message.channel, discord.DMChannel) and message.author.id != 199630284906430465:
        None

    #########################################
    if message.content.startswith('!input'):
        print(message.content)
    #########################################
    # elif message.content == '!log':
    #     if message.author.id == 199630284906430465:
    #         await message.channel.send('Goodbye!')
    #         await bot.logout()
    #########################################
    elif message.content.startswith('$roll'):
        try:
            roll = message.content.split(' ')[1]
            dice = int(roll.split('d')[0])
            kind = int(roll.split('d')[1])
            rolls = []
            for i in range(dice):
                rolls.append(random.randint(1, kind))
            await message.channel.send('🎲 Result: **' + str(sum(rolls)) + '** *(' + ' + '.join(str(i) for i in rolls) + ')*')
        except:
            await message.channel.send('An **error** has occurred. Make sure you use `!roll (NUMBER)d(NUMBER)`.')
    #########################################
    elif message.content == 'hit':
        ctx = await bot.get_context(message)
        await ctx.invoke(bot.get_command('hit'))
    elif message.content == 'stand' or message.content == 'dd':
        ctx = await bot.get_context(message)
        await ctx.invoke(bot.get_command('stand'))
    elif message.content == 'split':
        ctx = await bot.get_context(message)
        await ctx.invoke(bot.get_command('split'))
    ##########################################

    await bot.process_commands(message)


##########################################################################################


@bot.command(aliases = ['colourpicker'])
async def colorpicker(ctx):
    color = ''
    colors = ['A', 'B', 'C', 'D', 'E', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for i in range(6):
        color += random.choice(colors)
    if ctx.message.content.startswith('!colorpicker'):
        await ctx.send('Your random color is https://www.colorhexa.com/' + color)
    elif ctx.message.content.startswith('!colourpicker'):
        await ctx.send('Your random colour is https://www.colorhexa.com/' + color)
#########################################
@bot.command()
async def poll(ctx, *, question: lambda q: q.title()):
    embed = discord.Embed(description='Respond below with 👍 for YES, 👎 for NO, or 🤔 for UNSURE/NEUTRAL', color=16724721)
    embed.set_author(name=question, icon_url=str(ctx.guild.icon))
    embed.set_footer(text='Polled on: ' + str(datetime.datetime.now())[:(-7)])
    sent = await ctx.send(embed=embed)
    await sent.add_reaction('👍')
    await sent.add_reaction('👎')
    await sent.add_reaction('🤔')
#########################################
@bot.command()
async def setseed(ctx, seed: str):
    if ctx.channel.id == 876447964690796564:
        if len(seed) > 20:
            await ctx.send('That client seed is too long. Please try a shorter one. (20 Character Limit)')
        else:
            c.execute("UPDATE rsmoney SET clientseed='{}' WHERE id={}".format(seed, ctx.author.id))
            await ctx.send('Your client seed has been set to "' + seed + '".')
    else:
        await ctx.send('This command can only be used in <#876447964690796564> to prevent spam.')
#########################################








#########################################
@bot.command(aliases = ['w', 'bal', 'balance', '$', 'v', 'value'])
async def wallet(ctx, member: discord.Member = None):
    if (member is None) or ((getvalue(member.id, 'privacy', 'rsmoney') == False) or has_perms(ctx.guild, ctx.author, 'Host')):
        
        if member is None:
            member = ctx.author

        osrs = getvalue(member.id, '07', 'rsmoney')
        rs3 = getvalue(member.id, 'rs3', 'rsmoney')
        tickets = getvalue(member.id, 'tickets', 'rsmoney')

        if (osrs >= 1000000) or (rs3 >= 1000000):
            sidecolor = 2693614
        elif (osrs >= 10000) or (rs3 >= 10000):
            sidecolor = 2490163
        else:
            sidecolor = 12249599

        if ctx.message.content.startswith('!v') or ctx.message.content.startswith('!value'):
            osrs = format_from_k(osrs, round_k = False)
            rs3 = format_from_k(rs3, round_k = False)
        else:
            osrs = format_from_k(osrs)
            rs3 = format_from_k(rs3)

        if rs3 == '0k':
            rs3 = '0 k'
        if osrs == '0k':
            osrs = '0 k'

        embed = discord.Embed(color=sidecolor)
        embed.set_author(name=member.display_name + "'s Wallet", icon_url=member.display_avatar)
        embed.add_field(name='RS3 Balance', value=rs3, inline=True)
        embed.add_field(name='07 Balance', value=osrs, inline=True)
        embed.add_field(name='Tickets', value=str(tickets), inline=True)
        # c.execute('SELECT * FROM jackpot')
        # bets = c.fetchall()
        # total = sum((x[1] for x in bets))
        # embed.set_footer(text=('Checkout our Jackpot game, the current pot is up to ' + format_from_k(total)) + '!')

        if (member == ctx.author) and (getvalue(ctx.author.id, 'privacy', 'rsmoney')):
            sent = await ctx.author.send(embed=embed)
            await ctx.message.add_reaction('👍')
            await asyncio.sleep(2)
        else:
            await ctx.send(embed=embed)

    elif getvalue(member.id, 'privacy', 'rsmoney'):
        await ctx.send('Sorry, that user has wallet privacy mode enabled.')
#########################################
@bot.command()
async def claim(ctx, currency: convert_currency):
    claimed = getvalue(ctx.author.id, 'claimed', 'rsmoney')
    amount = 1000 if currency == '07' else 5000

    if not claimed:
        update_money(ctx.author.id, amount, currency)
        c.execute('UPDATE rsmoney SET claimed={} WHERE id={}'.format(True, ctx.author.id))
        words = 'Your free **' + format_from_k(amount) + ' ' + currency.upper() + '** has been claimed! You can gain an additional 200k 07 / 2m RS3 every time you invite someone to the server.\n\n**Invite Link:** https://discord.gg/8SZ2tkPRbh'
    else:
        words = 'You have already claimed your free 1m 07 / 5m RS3! However, you can gain additional gold every time you invite someone to the server.\n\n**Invite Link:** https://discord.gg/8SZ2tkPRbh'

    embed = discord.Embed(description=words, color=15925108)
    embed.set_author(name='Welcome Money', icon_url=ctx.author.display_avatar)
    await ctx.send(embed=embed)

@claim.error
async def claim_error(ctx, error):
    await ctx.send('An **error** occurred. Make sure you use `!claim (RS3 or 07)`')
#########################################
@bot.command()
async def wipe(ctx, member: discord.Member, currency: convert_currency = None):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        if currency == '07':
            c.execute('UPDATE rsmoney SET osrs={} WHERE id={}'.format(0, member.id))
        elif currency == 'rs3':
            c.execute('UPDATE rsmoney SET rs3={} WHERE id={}'.format(0, member.id))
        
        embed = discord.Embed(description="<@" + str(member.id) + ">'s " + currency.upper() + " currency has been wiped clean. RIP", color=5174318)
        embed.set_author(name='Wallet Wipe', icon_url=member.display_avatar)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Admin Command Only!')

@wipe.error
async def wipe_error(ctx, error):
        await ctx.send('An **error** occurred. Make sure you use `!wipe (@USER) (RS3 or 07)`')
#########################################
@bot.command(name = 'deposit', aliases = ['withdraw'])
async def give_money(ctx, member: discord.Member, amount: format_to_k, currency: convert_currency = None):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        if ctx.message.content.startswith('!deposit'):
            update_money(member.id, amount, currency)
        elif ctx.message.content.startswith('!withdraw'):
            update_money(member.id, amount * -1, currency)
        
        embed = discord.Embed(description='<@' + str(member.id) + ">'s wallet has been updated.", color=5174318)
        embed.set_author(name='Update Request', icon_url=ctx.author.display_avatar)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Admin Command Only!')

@give_money.error
async def give_money_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!deposit/withdraw (@USER) (AMOUNT) (RS3 or 07)`.')
#########################################
@bot.command(aliases = ['commands', 'cmds'])
async def list_commands(ctx):
    if ctx.channel.id != 1043280676071415879:
        (walletcmds, wagercmds, keycmds, gamecmds, misccmds) = ([], [], [], [], [])
        
        f = open('commands.txt')
        section = 0
        for i in f:
            if i[:1] == '-':
                section += 1
                continue

            if section == 0:
                walletcmds.append(i.split('|')[0] + '\n')
            elif section == 1:
                wagercmds.append(i.split('|')[0] + '\n')
            elif section == 2:
                keycmds.append(i.split('|')[0] + '\n')
            elif section == 3:
                gamecmds.append(i.split('|')[0] + '\n')
            else:
                misccmds.append(i.split('|')[0] + '\n')
        
        embed = discord.Embed(description='Use `!info (COMMAND NAME)` for a description of what that command does.\n*Example: !info !wallet*', color=16771099)
        embed.set_author(name='Bot Commands', icon_url=str(ctx.guild.icon))
        embed.add_field(name='Wallet Commands', value=''.join(walletcmds), inline=True)
        embed.add_field(name='Wager Commands', value=''.join(wagercmds), inline=True)
        embed.add_field(name='Key Commands', value=''.join(keycmds), inline=True)
        embed.add_field(name='Game Commands', value=''.join(gamecmds), inline=True)
        embed.add_field(name='Miscellaneous Commands', value=''.join(misccmds), inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Please refrain from using that command in this channel. Check pinned messages for a list of commands.')

@bot.command()
async def info(ctx, command: str):
    f = open('commands.txt')
    for i in f:
        if command in i.strip('\n').split('|')[0]:
            description = ((i.strip('\n').split('|')[2] + '\n\nUsage: `') + i.split('|')[1]) + '`'
            break
    embed = discord.Embed(description='This command ' + str(description), color=16771099)
    embed.set_author(name='Command Explanation', icon_url=str(ctx.guild.icon))
    await ctx.send(embed=embed)

@info.error
async def info_error(ctx, error):
    await ctx.send('That command could not be found, use `!commands` or `!cmds` for a list of commands.')
#########################################
class transfer_view(View):
    def __init__(self, ctx, member, amount, currency):
        super().__init__()
        self.ctx = ctx
        self.member = member
        self.amount = amount
        self.currency = currency

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def button_yes_callback(self, interaction, button):
        if interaction.user.id == self.ctx.author.id:
            taker = getvalue(self.member.id, self.currency, 'rsmoney')
            current = getvalue(self.ctx.author.id, self.currency, 'rsmoney')

            if self.currency == 'rs3':
                c.execute('UPDATE rsmoney SET rs3={} WHERE id={}'.format(current - self.amount, self.ctx.author.id))
                c.execute('UPDATE rsmoney SET rs3={} WHERE id={}'.format(taker + self.amount, self.member.id))
            elif self.currency == '07':
                c.execute('UPDATE rsmoney SET osrs={} WHERE id={}'.format(current - self.amount, self.ctx.author.id))
                c.execute('UPDATE rsmoney SET osrs={} WHERE id={}'.format(taker + self.amount, self.member.id))
            
            embed = discord.Embed(description='<@' + str(self.ctx.author.id) + '> has transfered ' + format_from_k(self.amount) + ' ' + (self.currency).upper() + ' to <@' + str(self.member.id) + ">'s wallet.", color=5174318)
            embed.set_author(name='Transfer Request', icon_url=self.ctx.author.display_avatar)
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def button_no_callback(self, interaction, button):
        if interaction.user.id == self.ctx.author.id:
            self.clear_items()
            embed = discord.Embed(description='Transfer aborted.', color=16718121)
            embed.set_author(name='Transfer Request', icon_url=self.ctx.author.display_avatar)
            await interaction.response.edit_message(embed=embed, view=self)

    async def on_error(self, interaction, error, item):
        await interaction.response.send_message(str(error))

@bot.command(aliases = ['t'])
async def transfer(ctx, member: discord.Member, amount: format_to_k, currency: convert_currency = None):
    if currency == None:
        currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')           
    
    current = getvalue(ctx.author.id, currency, 'rsmoney')
        
    if amount > 1:
        if current >= amount:
            if member == ctx.author:
                await ctx.send("You can't transfer money to yourself 😂")
            else:
                if has_perms(ctx.guild, member, 'Host'):
                    taker = getvalue(member.id, currency, 'rsmoney')

                    if currency == 'rs3':
                        c.execute('UPDATE rsmoney SET rs3={} WHERE id={}'.format(current - amount, ctx.author.id))
                        c.execute('UPDATE rsmoney SET rs3={} WHERE id={}'.format(taker + amount, member.id))
                    elif currency == '07':
                        c.execute('UPDATE rsmoney SET osrs={} WHERE id={}'.format(current - amount, ctx.author.id))
                        c.execute('UPDATE rsmoney SET osrs={} WHERE id={}'.format(taker + amount, member.id))
                    
                    embed = discord.Embed(description='<@' + str(ctx.author.id) + '> has transfered ' + format_from_k(amount) + ' ' + (currency).upper() + ' to <@' + str(member.id) + ">'s wallet.", color=5174318)
                    embed.set_author(name='Transfer Request', icon_url=ctx.author.display_avatar)
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(description=f'Are you sure you want to transfer **{format_from_k(amount)} {currency.upper()}** to <@{str(member.id)}>?', color=5174318)
                    embed.set_author(name = 'Transfer Confirmation', icon_url = ctx.author.display_avatar)
                    await ctx.reply(embed=embed, view=transfer_view(ctx, member, amount, currency))
        else:
            await ctx.send(('<@' + str(ctx.author.id)) + ">, You don't have enough money to transfer that amount!")
    else:
        await ctx.send('You must transfer at least **1k** ' + currency + '.')


@transfer.error
async def transfer_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!transfer (@USER) (AMOUNT) (RS3 or 07)`.')
#########################################
class dicing_view(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.success = False

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def button_yes_callback(self, interaction, button):
        if interaction.user.id == self.ctx.author.id:
            self.success = True
            self.clear_items()
            self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def button_no_callback(self, interaction, button):
        if interaction.user.id == self.ctx.author.id:
            self.clear_items()
            await interaction.response.send_message('Action aborted.', view=self)
            self.stop()

    async def on_error(self, interaction, error, item):
        await interaction.response.send_message(str(error))

@bot.command(name = '50', aliases = ['53', '75', '95'])
async def dicing(ctx, bet, currency: convert_currency = None):
    if ctx.channel.id in [1001547430208221215, 882466336117260309]:
        if bet != 'chuck':
            bet = format_to_k(bet)
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        current = getvalue(ctx.author.id, currency, 'rsmoney')

        if ctx.message.content.startswith('!53'):
            (title, odds, multiplier) = ('53x2', 53, 2)
        elif ctx.message.content.startswith('!50'):
            (title, odds, multiplier) = ('50x1.85', 50, 1.85)
        elif ctx.message.content.startswith('!75'):
            (title, odds, multiplier) = ('75x3', 75, 3)
        elif ctx.message.content.startswith('!95'):
            (title, odds, multiplier) = ('95x7', 95, 7)
            
        if bet == 'chuck':
            view = dicing_view(ctx)
            embed = discord.Embed(description=f'You are about to bet your whole cash stack (**{format_from_k(current)} {currency.upper()}**) on {title}. Are you sure you want to continue?', color=5174318)
            embed.set_author(name = 'Chuck Confirmation', icon_url = ctx.author.display_avatar)
            await ctx.reply(embed=embed, view=view)
            await view.wait()
            if view.success:
                bet = current
            else:
                return

        if is_enough(bet, currency)[0]:
            if current >= bet:
                roll, nonce = getrandint(ctx.author.id)
                
                if roll in range(1, odds):
                    winnings = bet
                    win = False
                    words = 'Rolled **' + str(roll) + '** out of **100**. You lost **' + format_from_k(bet) + '** ' + currency + '.'
                    sidecolor, gains = 16718121, (bet * -1)
                elif roll == odds:
                    winnings = None
                    win = 'tie'
                    words = 'Rolled **' + str(roll) + "** out of **100**. It's a tie! Money back."
                    sidecolor, gains = 16776960, 0
                else:
                    winnings = format_from_k(int(bet * multiplier))
                    win = True
                    words = 'Rolled **' + str(roll) + '** out of **100**. You won **' + str(winnings) + '** ' + currency + '.'
                    sidecolor, gains = 3997475, ((bet * multiplier) - bet)
                
                update_money(ctx.author.id, gains, currency)
                clientseed = getvalue(ctx.author.id, 'clientseed', 'rsmoney')
                embed = discord.Embed(color=sidecolor)
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                embed.add_field(name=title, value=words, inline=True)
                embed.set_footer(text='Nonce: ' + str(nonce) + ' | Client Seed: "' + str(clientseed) + '"')
                await ctx.send(embed=embed)
                ticketbets(ctx.author.id, bet, currency)
            else:
                await ctx.send(('<@' + str(ctx.author.id)) + ">, you don't have that much gold!")
        else:
            await ctx.send(is_enough(bet, currency)[1])
    else:
        await ctx.send('Please go to <#1001547430208221215> to use this command.')

@dicing.error
async def dicing_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!(50, 53, 75, or 95) (BET) (RS3 or 07)`.')
#########################################
@bot.command(aliases = ['weekly', 'thisweek'])
async def wager(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    if ctx.message.content.startswith('!wager'):
        timeframe = 'Total'
        rs3wager = getvalue(member.id, 'rs3total', 'rsmoney')
        osrswager = getvalue(member.id, 'osrstotal', 'rsmoney')
    else:
        timeframe = 'Weekly'
        rs3wager = getvalue(ctx.author.id, 'rs3week', 'rsmoney')
        osrswager = getvalue(ctx.author.id, 'osrsweek', 'rsmoney')

    osrs = format_from_k(osrswager)
    rs3 = format_from_k(rs3wager)
    
    if rs3 == '0k':
        rs3 = '0 k'
    if osrs == '0k':
        osrs = '0 k'

    embed = discord.Embed(color=16766463)
    embed.set_author(name = member.display_name + "'s " + timeframe + " Bets", icon_url = member.display_avatar)
    embed.add_field(name = 'RS3 ' + timeframe + ' Bets', value = rs3, inline=True)
    embed.add_field(name = '07 ' + timeframe + ' Bets', value = osrs, inline=True)
    c.execute('SELECT * FROM jackpot')
    bets = c.fetchall()
    total = sum((x['bet'] for x in bets))
    embed.set_footer(text='Checkout our Jackpot game, the current pot is up to ' + format_from_k(total) + '!')
    await ctx.send(embed=embed)
#########################################
@bot.command(aliases = ['updateweekly'])
async def updatewager(ctx, member: discord.Member, amount: format_to_k, currency: convert_currency = None):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        if ctx.message.content.startswith('!updatewager'):
            timeframe = 'total'
        else:
            timeframe = 'week'

        if currency == '07':
            current = getvalue(member.id, 'osrs' + timeframe, 'rsmoney')
            c.execute("UPDATE rsmoney SET {} = {} WHERE id = {}".format('osrs' + timeframe, current + amount, member.id))
        else:
            current = getvalue(member.id, 'rs3' + timeframe, 'rsmoney')
            c.execute("UPDATE rsmoney SET {} = {} WHERE id = {}".format('rs3' + timeframe, current + amount, member.id))

        embed = discord.Embed(description=f"<@{str(member.id)}>'s wager has been updated.", color=5174318)
        embed.set_author(name = "Wager Update", icon_url = member.display_avatar)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Permissions not met.')

@updatewager.error
async def updatewager_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!updatewager/updateweekly (@USER) (Amount) (RS3 or 07)`.')
#########################################
@bot.command(aliases = ['weeklyreset', 'resetweekly', 'resetthisweek', 'reset_weekly'])
async def weekly_reset(ctx):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        await reset_weekly(ctx.guild)
        embed = discord.Embed(description='All weekly bets have been reset.', color=5174318)
        embed.set_author(name='Weekly Bet Reset', icon_url=ctx.guild.icon)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Admin Command Only!')
#########################################
@bot.command(aliases = ['private', 'priv'])
async def privacy(ctx, toggle: typing.Literal['on', 'off']):
    if toggle == 'on':
        c.execute('UPDATE rsmoney SET privacy=True WHERE id={}'.format(ctx.author.id))
        embed = discord.Embed(description=('<@' + str(ctx.author.id)) + ">'s wallet privacy is now enabled.", color=5174318)
        embed.set_author(name='Privacy Mode', icon_url=str(ctx.author.display_avatar))
        await ctx.send(embed=embed)

    elif toggle == 'off':
        c.execute('UPDATE rsmoney SET privacy=False WHERE id={}'.format(ctx.author.id))
        embed = discord.Embed(description=('<@' + str(ctx.author.id)) + ">'s wallet privacy is now disabled.", color=5174318)
        embed.set_author(name='Privacy Mode', icon_url=str(ctx.author.display_avatar))
        await ctx.send(embed=embed)

@privacy.error
async def privacy_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!privacy (On or Off)`.')
#########################################
@bot.command()
async def default(ctx, currency: convert_currency):
    if currency == '07' or currency == 'rs3':
        c.execute("UPDATE rsmoney SET defaultc='{}' WHERE id={}".format(currency, ctx.author.id))
        embed = discord.Embed(description=('<@' + str(ctx.author.id)) + ">'s default currency is now set to " + currency + '.', color=5174318)
        embed.set_author(name='Default Currency', icon_url=ctx.author.display_avatar)
        await ctx.send(embed=embed)
    else:
        await ctx.send('That is not a valid currency!')
#########################################
@bot.command()
async def bj(ctx, bet: format_to_k, currency: convert_currency = None):
    if ctx.channel.id in [1001547558298067027, 882466336117260309]:
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        deck = 'aC|aS|aH|aD|2C|2S|2H|2D|3C|3S|3H|3D|4C|4S|4H|4D|5C|5S|5H|5D|6C|6S|6H|6D|7C|7S|7H|7D|8C|8S|8H|8D|9C|9S|9H|9D|tC|tS|tH|tD|jC|jS|jH|jD|qC|qS|qH|qD|kC|kS|kH|kD'
        current = getvalue(ctx.author.id, currency, 'rsmoney')
        
        if is_enough(bet, currency)[0]:
            if current >= bet:
                try:
                    c.execute('SELECT playerscore FROM bj WHERE id={}'.format(ctx.author.id))
                    tester = int(c.fetchone()['playerscore'])
                    await ctx.send('You are already in a game of blackjack! Type `!hit` or `!stand` to continue the game!')
                except:
                    update_money(ctx.author.id, bet * -1, currency)
                    ticketbets(ctx.author.id, bet, currency)
                    c.execute('INSERT INTO bj VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (ctx.author.id, deck, '', '', 0, 0, bet, currency, '', str(ctx.channel.id), 'None'))
                    drawcard(ctx.author.id, True)
                    drawcard(ctx.author.id, True)
                    drawcard(ctx.author.id, False)
                    drawcard(ctx.author.id, False)
                    botcards = getvalue(ctx.author.id, 'botcards', 'bj')
                    playercards = getvalue(ctx.author.id, 'playercards', 'bj')
                    scorebj(ctx.author.id, botcards, False)
                    playerscore = scorebj(ctx.author.id, playercards, True)[0]
                    sent = await ctx.send(embed=printbj(ctx.author, False, 'Use `!hit` to draw, `!stand` to pass, `!dd` to double down, or `!split` to split.', 28))
                    c.execute('UPDATE bj SET messageid={} WHERE id={}'.format(str(sent.id), ctx.author.id))
                    
                    if playerscore == 21:
                        await ctx.invoke(bot.get_command('stand'))
            else:
                await ctx.send(('<@' + str(ctx.author.id)) + ">, you don't have that much gold!")
        else:
            await ctx.send(is_enough(bet, currency)[1])
    else:
        await ctx.send('This command can only be used in <#1001547558298067027>.')

@bj.error
async def bj_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!bj (AMOUNT) (RS3 or 07)`.')
#########################################
@bot.command()
async def hit(ctx):
    drawcard(ctx.author.id, True)
    playercards = getvalue(ctx.author.id, 'playercards', 'bj')
    playerscore = scorebj(ctx.author.id, playercards, True)[0]
    botcards = getvalue(ctx.author.id, 'botcards', 'bj')
    botscore = getvalue(ctx.author.id, 'botscore', 'bj')
    messageid = getvalue(ctx.author.id, 'messageid', 'bj')
    currency = getvalue(ctx.author.id, 'currency', 'bj')
    bet = getvalue(ctx.author.id, 'bet', 'bj')
    split = getvalue(ctx.author.id, 'split', 'bj')
    sent = await ctx.fetch_message(messageid)
    
    if playerscore > 21:
        if 'y' in split:
            c.execute("UPDATE bj SET playercards='{}' WHERE id={}".format(split[1:], ctx.author.id))
            c.execute("UPDATE bj SET split='{}' WHERE id={}".format('z' + playercards, ctx.author.id))
            botcards = getvalue(ctx.author.id, 'botcards', 'bj')
            playercards = getvalue(ctx.author.id, 'playercards', 'bj')
            scorebj(ctx.author.id, botcards, False)
            scorebj(ctx.author.id, playercards, True)
            await sent.edit(embed=printbj(ctx.author, False, 'Use `!hit` to draw, `!stand` to pass, or `!dd` to double down.', 28))
        elif split == 'None':
            await sent.edit(embed=printbj(ctx.author, True, 'Sorry. You busted and lost.', 16711718))
            c.execute('DELETE FROM bj WHERE id={}'.format(ctx.author.id))
        else:
            await sent.delete()
            splitscore = scorebj(ctx.author.id, split[1:], 'Split')[0]
            embed1 = bjresult(ctx.author, bet, currency, botscore, splitscore, split[1:])
            embed2 = bjresult(ctx.author, bet, currency, botscore, playerscore, playercards)
            embed1.set_author(name=ctx.author.display_name + "'s Blackjack Hand 1 Result", icon_url=ctx.author.display_avatar)
            embed2.set_author(name=ctx.author.display_name + "'s Blackjack Hand 2 Result", icon_url=ctx.author.display_avatar)
            await ctx.send(embed=embed1)
            await ctx.send(embed=embed2)
            c.execute('DELETE FROM bj WHERE id={}'.format(ctx.author.id))
    elif playerscore == 21:
        await ctx.invoke(bot.get_command('stand'))
    else:
        await sent.edit(embed=printbj(ctx.author, False, 'Use `!hit` to draw, `!stand` to pass, `!dd` to double down, or `!split` to split.', 28))
#########################################
@bot.command(aliases = ['dd'])
async def stand(ctx):
    currency = getvalue(ctx.author.id, 'currency', 'bj')
    playercards = getvalue(ctx.author.id, 'playercards', 'bj')
    playerscore = scorebj(ctx.author.id, playercards, True)[0]
    botcards = getvalue(ctx.author.id, 'botcards', 'bj')
    botscore = scorebj(ctx.author.id, botcards, False)
    messageid = getvalue(ctx.author.id, 'messageid', 'bj')
    current = getvalue(ctx.author.id, currency, 'rsmoney')
    bet = getvalue(ctx.author.id, 'bet', 'bj')
    split = getvalue(ctx.author.id, 'split', 'bj')
    sent = await ctx.fetch_message(messageid)
    enough = True

    if ctx.message.content == '!dd' or ctx.message.content == 'dd':
        if current >= bet:
            update_money(ctx.author.id, bet * -1, currency)
            ticketbets(ctx.author.id, bet, currency)
            bet = bet * 2
            drawcard(ctx.author.id, True)
            playercards = getvalue(ctx.author.id, 'playercards', 'bj')
            playerscore = scorebj(ctx.author.id, playercards, True)[0]
            if playerscore > 21:
                if split == 'None':
                    await sent.edit(embed=printbj(ctx.author, True, 'Sorry. You busted and lost.', 16711718))
                    c.execute('DELETE FROM bj WHERE id={}'.format(ctx.author.id))
                    return
        else:
            enough = False
            await ctx.send("You don't have enough money to double down!")

    if enough:
        if 'y' not in split:
            while (botscore[0] < 17) or ((botscore[0] == 17) and (botscore[1] == 'Soft ') and (botscore[0] <= playerscore)):#(playerscore > botscore[0])
                drawcard(ctx.author.id, False)
                botcards = getvalue(ctx.author.id, 'botcards', 'bj')
                botscore = scorebj(ctx.author.id, botcards, False)

        if 'y' in split:
            c.execute("UPDATE bj SET playercards='{}' WHERE id={}".format(split[1:], ctx.author.id))
            c.execute("UPDATE bj SET split='{}' WHERE id={}".format('z' + playercards, ctx.author.id))
            botcards = getvalue(ctx.author.id, 'botcards', 'bj')
            playercards = getvalue(ctx.author.id, 'playercards', 'bj')
            scorebj(ctx.author.id, botcards, False)
            scorebj(ctx.author.id, playercards, True)
            await sent.edit(embed=printbj(ctx.author, False, 'Use `!hit` to draw, `!stand` to pass, or `!dd` to double down for hand two.', 28))
        elif split == 'None':
            await sent.edit(embed=bjresult(ctx.author, bet, currency, botscore[0], playerscore, playercards))
            c.execute('DELETE FROM bj WHERE id={}'.format(ctx.author.id))
        else:
            await sent.delete()
            splitscore = scorebj(ctx.author.id, split[1:], 'Split')[0]
            embed1 = bjresult(ctx.author, bet, currency, botscore[0], splitscore, split[1:])
            embed2 = bjresult(ctx.author, bet, currency, botscore[0], playerscore, playercards)
            embed1.set_author(name=ctx.author.display_name + "'s Blackjack Hand 1 Result", icon_url=ctx.author.display_avatar)
            embed2.set_author(name=ctx.author.display_name + "'s Blackjack Hand 2 Result", icon_url=ctx.author.display_avatar)
            await ctx.send(embed=embed1)
            await ctx.send(embed=embed2)
            c.execute('DELETE FROM bj WHERE id={}'.format(ctx.author.id))

@stand.error
async def stand_error(ctx, error):
    await ctx.send('An **error** has occured. You may not be in a blackjack game at this time.')
#########################################
@bot.command()
async def split(ctx):
    currency = getvalue(ctx.author.id, 'currency', 'bj')
    bet = getvalue(ctx.author.id, 'bet', 'bj')
    playercards = getvalue(ctx.author.id, 'playercards', 'bj')
    current = getvalue(int(ctx.author.id), currency, 'rsmoney')
    messageid = getvalue(ctx.author.id, 'messageid', 'bj')
    split = getvalue(ctx.author.id, 'split', 'bj')
    
    if split == 'None':
        if (len(playercards.split('|')) == 3) and (playercards.split('|')[0][0] == playercards.split('|')[1][0]):
            if current >= bet:
                update_money(ctx.author.id, bet * -1, currency)
                ticketbets(ctx.author.id, bet, currency)
                c.execute("UPDATE bj SET split='{}' WHERE id={}".format(('y' + playercards.split('|')[1]) + '|', ctx.author.id))
                c.execute("UPDATE bj SET playercards='{}' WHERE id={}".format(playercards.split('|')[0] + '|', ctx.author.id))
                playercards = getvalue(ctx.author.id, 'playercards', 'bj')
                scorebj(ctx.author.id, playercards, True)
                sent = await ctx.fetch_message(messageid)
                await sent.edit(embed=printbj(ctx.author, False, 'Use `!hit` to draw `!stand` to pass, or `!dd` to double down.', 28))
            else:
                await ctx.send("You don't have enough money to split!")
        else:
            await ctx.send('Conditions not met to split. Your hand must consist of a pair of the same card.')
    else:
        await ctx.send('We do not allow respliting, sorry.')

#########################################
@bot.command(aliases = ['k', 'key'])
async def keys(ctx):
    keyNames = ['Bronze', 'Iron', 'Steel', 'Mithril', 'Adamant', 'Rune', 'Dragon', 'Noxious']
    bronze, iron, steel, mithril, adamant, rune, dragon, noxious = getvalue(ctx.author.id, keyNames, 'rsmoney')
    keyValues = [bronze, iron, steel, mithril, adamant, rune, dragon, noxious]

    embed = discord.Embed(color=13226456)
    embed.set_author(name=ctx.author.display_name + "'s Keys", icon_url=ctx.author.display_avatar)

    for counter, i in enumerate(keyValues):
        embed.add_field(name=keyNames[counter], value='**' + str(i) + '**', inline=True)

    c.execute('SELECT * FROM jackpot')
    bets = c.fetchall()
    total = sum((x['bet'] for x in bets))
    embed.set_footer(text='Checkout our Jackpot game, the current pot is up to ' + format_from_k(total) + '!')
    await ctx.send(embed=embed)
#########################################
@bot.command(aliases = ['buykeys', 'buy'])
async def buykey(ctx, keyKind: str, amount: int):
    if ctx.channel.id in [1001549003860742234]:

        if keyKind in ['bronze', 'steel', 'adamant', 'dragon']:
            currency = '07'
        elif keyKind in ['iron', 'mithril', 'rune', 'noxious']:
            currency = 'rs3'

        currentKeys = getvalue(ctx.author.id, keyKind, 'rsmoney')
        buyer = getvalue(ctx.author.id, currency, 'rsmoney')
        keyPrices = {'bronze':1000, 'iron':5000, 'steel':5000, 'mithril':10000, 'adamant':10000, 'rune':50000, 'dragon':20000, 'noxious':100000}
        price = keyPrices[keyKind]

        embed = discord.Embed(description='You successfully purchased **' + str(amount) + '** key(s)!', color=5174318)
        embed.set_author(name='Purchase Complete', icon_url=ctx.author.display_avatar)

        if buyer >= (price * amount):
            c.execute('UPDATE rsmoney SET {} = {} WHERE id = {}'.format(keyKind, currentKeys + amount, ctx.author.id))
            update_money(ctx.author.id, (price * -1 * amount), currency)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Not enough gold. You need **' + format_from_k(price * amount) + ' ' + currency + '** to buy that many ' + keyKind + ' keys.')
    else:
        await ctx.send('This command can only be used in <#1001549003860742234>.')

@buykey.error
async def buykey_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!buykey (KEY TYPE) (AMOUNT)`.')
#########################################
@bot.command(aliases = ['open', 'openkey', 'openkeys'])
async def _open(ctx, keyKind: str, amount: int = 1):
    if ctx.channel.id in [1001549003860742234]:
        keyValue = getvalue(ctx.author.id, keyKind, 'rsmoney')
        keyColors = {'bronze':11880979, 'iron':4209728, 'steel':13226456, 'mithril':9066239, 'adamant':3917613, 'rune':2330341, 'dragon':16718633, 'noxious':13566207}
        if keyKind in ['bronze', 'steel', 'adamant', 'dragon']:
            currency = '07'
        elif keyKind in ['iron', 'mithril', 'rune', 'noxious']:
            currency = 'rs3'

        if keyValue >= amount:
            c.execute('UPDATE rsmoney SET {} = {} WHERE id={}'.format(keyKind, keyValue - amount, ctx.author.id))
            f = open(keyKind + '.txt')

            if amount > 1:
                num_lines = sum(1 for line in f)
                itemcount = [0] * num_lines
                words, url_found, url, total = '', False, '', 0

                for i in range(amount):
                    index = openkey(keyKind)[0]
                    itemcount[index] += 1

                f.seek(0)

                for (counter, x) in enumerate(f):
                    if itemcount[counter] > 0:
                        item = x.strip('\n').split('|')
                        total += (int(item[1]) * itemcount[counter])
                        words += (f'__{str(item[0])}__ *[{format_from_k(int(item[1]))}]* - {itemcount[counter]}\n\n')

                        if not url_found:
                            url = str(item[2])
                            url_found = True

                        update_money(ctx.author.id, (int(item[1]) * itemcount[counter]), currency)

                embed = discord.Embed(description=words, color=keyColors[keyKind])
                embed.set_author(name=keyKind.title() + ' Key Prizes', icon_url=ctx.author.display_avatar)
                embed.add_field(name='Total Value:', value='**' + format_from_k(total) + '**', inline=True)
                embed.set_thumbnail(url=url)
                await ctx.send(embed=embed)
            elif amount == 1:
                index = openkey(keyKind)[0]

                for (counter, x) in enumerate(f):
                    if counter == index:
                        item = x.strip('\n').split('|')

                update_money(ctx.author.id, int(item[1]), currency)
                embed = discord.Embed(description='You received item: **' + str(item[0]) + '**!', color=keyColors[keyKind])
                embed.add_field(name='Price', value='*' + format_from_k(int(item[1])) + '*', inline=True)
                embed.set_author(name=keyKind.title() + ' Key Prize', icon_url=ctx.author.display_avatar)
                embed.set_thumbnail(url=str(item[2]))
                await ctx.send(embed=embed)
            else:
                await ctx.send("You can't open less than one key!")

            f.close()
        else:
            await ctx.send("You don't have that many *" + keyKind + '* keys to open!')
    else:
        await ctx.send('This command can only be used in <#1001549003860742234>.')

@_open.error
async def _open_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!open (KEY TYPE)`.')
#########################################
@bot.command(aliases = ['updatekey', 'updatekeys'])
async def _updatekey(ctx, member: discord.Member, keyKind: str, amount: int):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        currentKeys = getvalue(member.id, keyKind, 'rsmoney')
        c.execute('UPDATE rsmoney SET {} = {} WHERE id = {}'.format(keyKind, currentKeys + amount, member.id))
        
        embed = discord.Embed(description='<@' + str(ctx.author.id) + '> has transfered ' + str(amount) + ' ' + keyKind + ' key(s) to <@' + str(member.id) + '>.', color=5174318)
        embed.set_author(name='Key Transfer', icon_url=ctx.author.display_avatar)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Admin Command Only!')
        
@_updatekey.error
async def _updatekey_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!updatekey (@USER) (KEY TYPE) (AMOUNT)`.')
#########################################
@bot.command()
async def fp(ctx, bet: format_to_k, currency: convert_currency = None):
    if ctx.channel.id in [1001548096322420766, 882466336117260309]:
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')
    
        current = getvalue(ctx.author.id, currency, 'rsmoney')
        
        if is_enough(bet, currency)[0]:
            if current >= bet:

                botflowers, playerflowers = [], []
                pprint, bprint = '', ''
                #flowers=['Red', 'Blue', 'Yellow', 'Purple', 'Orange', 'Assorted', 'Mixed', 'Black', 'White']
                emojis = ['rf', 'bf', 'yf', 'pf', 'of', 'af', 'mf', 'blaf', 'wf']

                for i in range(5):
                    botflowers.append(pickflower())
                    playerflowers.append(pickflower())

                for i in playerflowers:
                    pprint += str(get(bot.emojis, name=emojis[i]))
                for i in botflowers:
                    bprint += str(get(bot.emojis, name=emojis[i]))

                if scorefp(playerflowers)[0] == scorefp(botflowers)[0]:
                    embed = discord.Embed(description='Tie! Money back.', color=16776960)
                    win = 'tie'
                elif scorefp(playerflowers)[0] > scorefp(botflowers)[0]:
                    embed = discord.Embed(description='Congratulations! You won **' + format_from_k(int(bet * 1.9)) + '**!', color=3997475)
                    win = True
                    update_money(ctx.author.id, bet * 0.9, currency)
                elif scorefp(playerflowers)[0] < scorefp(botflowers)[0]:
                    embed = discord.Embed(description=('House wins. You lost ' + format_from_k(bet)) + '.', color=16718121)
                    win = False
                    update_money(ctx.author.id, bet * -1, currency)
                
                ticketbets(ctx.author.id, bet, currency)

                embed.add_field(name='Player Hand', value=(pprint + '\nResult: ') + scorefp(playerflowers)[1], inline=True)
                embed.add_field(name='House Hand', value=(bprint + '\nResult: ') + scorefp(botflowers)[1], inline=True)
                embed.set_author(name='Flower Poker - ' + ctx.author.display_name, icon_url=ctx.author.display_avatar)
                await ctx.send(embed=embed)
            else:
                await ctx.send(('<@' + str(ctx.author.id)) + ">, you don't have that much gold!")
        else:
            await ctx.send(is_enough(bet, currency)[1])
    else:
        await ctx.send('This command can only be used in <#1001548096322420766>.')

@fp.error
async def fp_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!fp (AMOUNT) (RS3 or 07)`.')
#########################################
@bot.command(aliases = ['lb'])
async def leaderboard(ctx, game: convert_currency, period: typing.Literal['weekly', 'total'] = 'weekly'):
    owner = get(ctx.guild.roles, name='Admin')
    host = get(ctx.guild.roles, name='Host')
    outcasts = ()
    for member in owner.members + host.members:
        outcasts += (member.id,)

    if game == 'rs3':
        if period == 'weekly':
            c.execute('SELECT * From rsmoney WHERE id NOT IN {} ORDER BY rs3week DESC LIMIT 8'.format(outcasts))
            text = 'rs3week'
        else:
            c.execute('SELECT * From rsmoney WHERE id NOT IN {} ORDER BY rs3total DESC LIMIT 8'.format(outcasts))
            text = 'rs3total'
    elif game == '07':
        if period == 'weekly':
            c.execute('SELECT * From rsmoney WHERE id NOT IN {} ORDER BY osrsweek DESC LIMIT 8'.format(outcasts))
            text = 'osrsweek'
        else:
            c.execute('SELECT * From rsmoney WHERE id NOT IN {} ORDER BY osrstotal DESC LIMIT 8'.format(outcasts))
            text = 'osrstotal'
    else:
        await ctx.send('That is not a valid currency!')
        return

    top = c.fetchall()
    words = ''
    for (counter, i) in enumerate(top):
        userid = i['id']
        total = i[text]
        bonus = ''

        if period == 'weekly':
            if total >= 30_000_000:
                bonus = '*> Eligible for **300m ' + game.upper() + '** bonus!*'
            elif total >= 20_000_000:
                bonus = '*> Eligible for **200m ' + game.upper() + '** bonus!*'
            elif total >= 10_000_000:
                bonus = '*> Eligible for **100m ' + game.upper() + '** bonus!*'

        total = format_from_k(int(total))
        words += str(counter + 1) + ' | <@' + str(userid) + '> - **' + total + '**\n' + bonus + '\n'
    
    embed = discord.Embed(color=557823, description=words)
    embed.set_author(name=('Top ' + game.upper()) + ' Wagers', icon_url=ctx.guild.icon)
    await ctx.send(embed=embed)

@leaderboard.error
async def leaderboard_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!leaderboard (RS3 or 07) (Weekly or Total)`.')
#########################################
@bot.command()
async def drawraffle(ctx):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        c.execute('SELECT id, tickets FROM rsmoney')
        tickets = c.fetchall()
        entered = []
        for i in tickets:
            for x in range(i['tickets']):
                entered.append(str(i['id']))
        winner = random.choice(entered)

        blacklist = []
        while winner in blacklist:
            winner = random.choice(entered)

        c.execute('UPDATE rsmoney SET tickets=0')
        embed = discord.Embed(description=('<@' + str(winner)) + '> has won the raffle!', color=16729241)
        embed.set_author(name='Raffle Winner', icon_url=ctx.guild.icon)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Admin Command Only!')
#########################################
@bot.command()
async def ticket(ctx, member: discord.Member, amount: int):
    if has_perms(ctx.guild, ctx.author, 'Cashier'):
        tickets = getvalue(member.id, 'tickets', 'rsmoney')
        c.execute('UPDATE rsmoney SET tickets={} WHERE id={}'.format(tickets + amount, member.id))
        await ctx.send('Tickets updated.')
    else:
        await ctx.send('Admin/Cashier Command Only!')
#########################################
@bot.command()
async def editjackpot(ctx, rollAmount: format_to_k):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        c.execute('UPDATE data SET jackpotroll={}'.format(rollAmount))
        await ctx.send('The jackpot will now end once the pot reaches **' + format_from_k(rollAmount) + '**.')
    else:
        await ctx.send('Only admins can change the amount at which a jackpot will end. Please tag one if necessary.')
#########################################
@bot.command()
async def add(ctx, bet: format_to_k):
    if ctx.channel.id == 1001551236346167367:
        current = getvalue(ctx.author.id, '07', 'rsmoney')
        c.execute('SELECT jackpotroll FROM data')
        rollAmount = int(c.fetchone()['jackpotroll'])
        
        if is_enough(bet, '07')[0]:
            if current >= bet:
                update_money(ctx.author.id, bet * -1, '07')
                ticketbets(ctx.author.id, bet, '07')
                c.execute('SELECT * FROM jackpot')
                bets = c.fetchall()
                alreadyIn = False
                
                for y in bets:
                    if ctx.author.id == y['id']:
                        c.execute('UPDATE jackpot SET bet={} WHERE id={}'.format(bet + y['bet'], ctx.author.id))
                        alreadyIn = True
                
                if not alreadyIn:
                    c.execute('INSERT INTO jackpot VALUES (%s, %s, %s)', (ctx.author.id, bet, 0))
                
                await ctx.message.add_reaction('✅')
                info = print_jackpot(ctx, rollAmount)
                await ctx.send(embed=info[0])
                
                if info[1] >= rollAmount:
                    await ctx.send(embed=roll_jackpot())
            else:
                await ctx.send(('<@' + str(ctx.author.id)) + ">, you don't have that much gold!")
        else:
            await ctx.send(is_enough(bet, '07')[1])
    else:
        await ctx.send('This command can only be used in <#1001551236346167367>.')
#########################################
@bot.command()
async def jackpot(ctx):
    if ctx.channel.id == 1001551236346167367:
        c.execute('SELECT jackpotroll FROM data')
        rollAmount = int(c.fetchone()['jackpotroll'])
        await ctx.send(embed=print_jackpot(ctx, rollAmount)[0])
    else:
        await ctx.send('This command can only be used in <#1001551236346167367>.')
########################################        
@bot.command()
async def endjackpot(ctx):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        await ctx.send(embed=roll_jackpot())
    else:
        await ctx.send('Only admins can end a jackpot. Please tag one if necessary.')
#########################################
@bot.command()
async def rank(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    xp = getvalue(member.id, 'xp', 'rsmoney')
    currentLevel = int(math.sqrt(xp/100))
    currentLevelXp = (currentLevel ** 2) * 100
    nextLevel = ((currentLevel + 1) ** 2) * 100
    progress = int(((xp - currentLevelXp) / nextLevel) * 495)
    roles, badge, color = [], 'Noob', (255, 255, 255)
    
    if currentLevel >= 1:
        #roles.append(get(ctx.guild.roles, name='Beginner ( Lvl. 1-10 )'))
        badge, color = 'Beginner', (255, 229, 229)
    if currentLevel >= 10:
        #roles.append(get(ctx.guild.roles, name='Novice ( Lvl. 10-20 )'))
        badge, color = 'Novice', (255, 204, 204)
    if currentLevel >= 20:
        #roles.append(get(ctx.guild.roles, name='Intermediate ( Lvl. 20-30 )'))
        badge, color = 'Pro', (255, 178, 178)
    if currentLevel >= 30:
        #roles.append(get(ctx.guild.roles, name='Pro ( Lvl. 30-40 )'))
        badge, color = 'Expert', (255, 153, 153)
    if currentLevel >= 40:
        #roles.append(get(ctx.guild.roles, name='Expert ( Lvl. 40-50 )'))
        badge, color = 'Master', (255, 127, 127)
    if currentLevel >= 50:
        #roles.append(get(ctx.guild.roles, name='Master ( Lvl. 50-60 )'))
        badge, color = 'Legend', (255, 76, 76)
    if currentLevel >= 60:
        #roles.append(get(ctx.guild.roles, name='Legend ( Lvl. 60-70 )'))
        badge, color = 'God', (255, 50, 50)
    if currentLevel >= 70:
        #roles.append(get(ctx.guild.roles, name='God ( Lvl. 70+ )'))
        badge, color = 'INSANE', (255, 0, 0)
    
    # if roles is not None:
    #     for i in roles:
    #         if i not in member.roles:
    #             await member.add_roles(i)

    template = cv2.imread('rankbar.png', 1)
    cv2.line(template, (50, 160), (550, 160), (136, 128, 122), 15)
    cv2.line(template, (50, 160), (50 + progress, 160), color, 15)
    (width, height) = cv2.getTextSize(member.display_name, 5, 1.3, 2)[0]
    cv2.putText(template, member.display_name, (150, 130), 5, 1.3, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(template, str(member)[-5:], (150 + width, 130), 2, 0.6, (70, 70, 70), 1, cv2.LINE_AA)
    cv2.putText(template, 'Rank', (390, 45), 5, 1.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.line(template, (390, 49), (485, 51), (136, 128, 122), 2)
    cv2.putText(template, badge, (390, 85), 5, 1.5, color, 2, cv2.LINE_AA)
    cv2.putText(template, ((str('{:,}'.format(xp)) + '/') + str('{:,}'.format(nextLevel))) + ' XP', (430, 130), 5, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(template, 'Level: ', (150, 65), 5, 1.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(template, str(currentLevel), (270, 65), 5, 1.5, color, 2, cv2.LINE_AA)
    
    try:
        req = Request(str(member.display_avatar), headers={'User-Agent': 'Mozilla/5.0'})
        arr = np.asarray(bytearray(urlopen(req).read()), dtype=np.uint8)
        avatar = cv2.imdecode(arr, 1)
        resized = cv2.resize(avatar, (100, 100), interpolation=cv2.INTER_AREA)
    except:
        avatar = cv2.imread('defaultavatar.png', 1)
        resized = cv2.resize(avatar, (100, 100), interpolation=cv2.INTER_AREA)
    
    template[30:130, 30:130] = resized
    cv2.rectangle(template, (0, 0), (600, 200), color, 5)
    cv2.imwrite('edited.png', template)
    await ctx.send(file=discord.File('edited.png', filename='edited.png'))
#########################################
@bot.command()
async def levels(ctx):
    c.execute('SELECT id, xp From rsmoney ORDER BY xp DESC LIMIT 10')
    top = c.fetchall()
    words = ''
    
    for (counter, i) in enumerate(top):
        userid = i['id']
        xp = i['xp']
        words += str(counter + 1) + '. <@' + str(userid) + '> - **XP: ' + str(xp) + '**\n\n'
    
    embed = discord.Embed(color=557823, description=words)
    embed.set_author(name='Top Levels and XP', icon_url=ctx.guild.icon)
    await ctx.send(embed=embed)
#########################################
class purge_view(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.success = False

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def button_yes_callback(self, interaction, button):
        if interaction.user.id == self.ctx.author.id:
            self.success = True
            self.clear_items()
            self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def button_no_callback(self, interaction, button):
        if interaction.user.id == self.ctx.author.id:
            self.clear_items()
            await interaction.response.send_message('Action aborted.', view=self)
            self.stop()

    async def on_error(self, interaction, error, item):
        await interaction.response.send_message(str(error))

@bot.command(aliases = ['prune', 'delete'])
async def purge(ctx, amount: lambda a: int(a) + 1):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        if amount >= 100:
            view = purge_view(ctx)
            embed = discord.Embed(description=f'You are about to delete {str(amount)} messages. Are you sure you want to continue?', color=5174318)
            embed.set_author(name = 'Purge Confirmation', icon_url = ctx.author.display_avatar)
            await ctx.reply(embed=embed, view=view)
            await view.wait()
            if view.success:
                None
            else:
                return

        await ctx.channel.purge(limit=amount)
        await asyncio.sleep(1)
        sent = await ctx.send('Successfully deleted **' + str(amount - 1) + '** messages.', delete_after = 3)
    else:
        await ctx.send('Permissions not met.')
#########################################
@bot.command(aliases = ['cashout'])
async def cashin(ctx, amount: format_to_k, currency: convert_currency = None):
    if ctx.channel.id == 876443320098889769:

        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        osrsweekly = getvalue(ctx.author.id, 'osrsweek', 'rsmoney')
        rs3weekly = getvalue(ctx.author.id, 'rs3week', 'rsmoney')
        current = getvalue(ctx.author.id, currency, 'rsmoney')
        way = ctx.message.content.split(' ')[0][1:]
        weekly_met, enough = True, True
        
        if way == 'cashout':        
            if (osrsweekly < 5000) and (rs3weekly < 50000):
                weekly_met = False
            if amount > current:
                enough = False

        if weekly_met:
            if enough:
                c.execute('SELECT code FROM cash')
                (codelist, codes) = (c.fetchall(), [])
                for i in codelist:
                    codes.append(int(i['code']))
                while True:
                    code = random.randint(100, 999)
                    if code in codes:
                        continue
                    else:
                        break
                
                c.execute('INSERT INTO cash VALUES (%s, %s, %s, %s, %s)', (ctx.author.id, way, code, currency, amount))
                await bot.get_channel(876447809765769237).send('<@' + str(ctx.author.id) + '> wants to ' + way + ' **' + format_from_k(amount) + '** ' + currency + '. Use `!accept ' + str(code) + '`.')
                embed = discord.Embed(description='A message has been sent to a cashier. Your request will be processed and you will be messaged soon.', color=5174318)
                embed.set_author(name=way.title(), icon_url=ctx.guild.icon)
                await ctx.send(embed=embed)
            else:
                await ctx.send(('<@' + str(ctx.author.id)) + ">, You don't have that much money to cashout!")
        else:
            await ctx.send('50m RS3 / 5m 07 Weekly Wager is required to cashout.')
    else:
        await ctx.send('This command can only be used in <#876443320098889769>.')

@cashin.error
async def cashin_error(ctx, error):
    await ctx.send(('An **error** has occurred. Make sure you use `!' + way) + ' (AMOUNT) (RS3 or 07)`.')

@bot.command()
async def accept(ctx, code: int):
    if ctx.message.channel.id == 876447809765769237:
        c.execute('SELECT code FROM cash')
        (codelist, codes) = (c.fetchall(), [])
        for i in codelist:
            codes.append(int(i['code']))
        
        if code in codes:
            c.execute('SELECT * FROM cash WHERE code={}'.format(code))
            cash = c.fetchall()[0]
            userid = str(cash['id'])
            way = str(cash['way'])
            currency = str(cash['currency'])
            amount = int(cash['amount'])
            if way == 'cashout':
                update_money(userid, amount * -1, currency)
                update_money(ctx.author.id, amount, currency)
            embed = discord.Embed(description='<@' + userid + '>, <@' + str(ctx.author.id) + '> will perform your ' + way + '.', color=5174318)
            embed.set_author(name=way.title(), icon_url=ctx.guild.icon)
            await bot.get_channel(876443320098889769).send(embed=embed)
            await ctx.send('Accepted. Please DM them now.')
            c.execute('DELETE FROM cash where code={}'.format(code))
        else:
            await ctx.send('There is no cashout/cashin request with that code.')
    else:
        None
############################################
@bot.command()
async def changedaily(ctx, amount: format_to_k):
    if has_perms(ctx.guild, ctx.author, 'Admin'):
        c.execute('UPDATE daily set prize={}'.format(amount))
        await ctx.send('The daily prize amount has been updated to **' + format_from_k(amount) + '**.')
    else:
        await ctx.send('Admin Command Only!')
############################################
@bot.command()
async def daily(ctx):
    if ctx.channel.id in [913778920107700234]:
        osrsweekly = getvalue(ctx.author.id, 'osrsweek', 'rsmoney')
        rs3weekly = getvalue(ctx.author.id, 'rs3week', 'rsmoney')
        c.execute('SELECT people FROM daily')
        people = str(c.fetchone()['people'])
        c.execute('SELECT channelid FROM daily')
        channelid = int(c.fetchone()['channelid'])
        dailyChannel = bot.get_channel(channelid)

        if osrsweekly >= 10000 or rs3weekly >= 100000:
            await ctx.send(':white_check_mark: <@' + str(ctx.author.id) + '> has bet at least **10m 07 / 100m RS3** this week.')
            if str(ctx.author.id) not in people:
                c.execute("UPDATE daily SET people='{}'".format(people + str(ctx.author.id) + '|'))
                await ctx.send(':white_check_mark: <@' + str(ctx.author.id) + '> has entered the daily giveaway!')
                await dailyChannel.send('<@' + str(ctx.author.id) + '>')
            else:
                await ctx.send("You have already entered today's __daily giveaway__!")
        else:
            await ctx.send(':no_entry: <@' + str(ctx.author.id) + '> has not bet at least **10m 07 / 100m RS3** this week. Check weekly wager with `!thisweek`.')
    else:
        await ctx.send('This command can only be used in <#913778920107700234>.')

#####################################
@bot.command(name = 'middle', aliases = ['over', 'under', 'top', 'bottom'])
async def overUnder(ctx, bet: format_to_k, currency: convert_currency = None):
    if ctx.channel.id in [1001550620488126505, 882466336117260309]:
        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        way = ctx.message.content.split(' ')[0][1:]
        current = getvalue(ctx.author.id, currency, 'rsmoney')

        if is_enough(bet, currency)[0]:
            if current >= bet:
                roll, nonce = getrandint(ctx.author.id)
                
                if (roll > 50 and way == 'over') or (roll < 50 and way == 'under'):
                    win, winnings, gains, multiplier = True, int(1.9 * bet), int(0.9 * bet), 1.9
                elif (roll > 50 and way == 'under') or (roll < 50 and way == 'over'):
                    win, winnings, gains, multiplier = False, 0, bet * -1, 1.9
                else:
                    if (roll == 50 and way == 'middle') or (roll == 100 and way == 'top') or (roll == 1 and way == 'bottom'):
                        win, winnings, gains, multiplier = True, bet * 99, bet * 99, 99
                    else:
                        win, winnings, gains, multiplier = False, 0, bet * -1, 0

                if win:
                    words = 'Rolled **' + str(roll) + '** out of **100**. You won **' + format_from_k(winnings) + '** ' + currency + '.'
                    sidecolor = 3997475
                else:
                    words = 'Rolled **' + str(roll) + '** out of **100**. You lost **' + format_from_k(bet) + '** ' + currency + '.'
                    sidecolor = 16718121
    
                update_money(ctx.author.id, gains, currency)
                clientseed = getvalue(ctx.author.id, 'clientseed', 'rsmoney')
                embed = discord.Embed(color=sidecolor)
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                embed.add_field(name='Over/Under', value=words, inline=True)
                embed.set_footer(text='Nonce: ' + str(nonce) + ' | Client Seed: "' + str(clientseed) + '"')
                await ctx.send(embed=embed)
                ticketbets(ctx.author.id, bet, currency)
            else:
                await ctx.send(('<@' + str(ctx.author.id)) + ">, you don't have that much gold!")
        else:
            await ctx.send(is_enough(bet, '07')[1])
    else:
        await ctx.send('This command can only be used in <#1001550620488126505>.')

@overUnder.error
async def overUnder_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!over (AMOUNT) (RS3 or 07)` or `!under (AMOUNT) (RS3 or 07)`.')
####################################
@bot.command()
async def dice(ctx, member: discord.Member, bet: format_to_k, currency: convert_currency = None):
    host = get(ctx.guild.roles, name='Host')
    if host in ctx.author.roles:

        if currency == None:
            currency = getvalue(ctx.author.id, 'defaultc', 'rsmoney')

        current = getvalue(ctx.author.id, currency, 'rsmoney')

        if current >= bet:
            update_money(ctx.author.id, bet * -1, currency)
            ticketbets(member.id, bet, currency)
            c.execute('INSERT INTO dice VALUES (%s, %s, %s, %s, %s, %s)', (member.id, ctx.author.id, bet, currency, 0, 0))
            embed = discord.Embed(description='A dice duel has begun between <@' + str(ctx.author.id) + '> and <@' + str(member.id) + '>!' +
                                                '\n\nUse `!roll` to roll your two six-sided dice!', color=16382207)
            embed.set_author(name='Dice Duel', icon_url=ctx.guild.icon)
            embed.set_image(url='https://cdn.discordapp.com/attachments/616038624143605801/735689548331352114/dicefinal.png')
            await ctx.send(embed=embed)
        else:
            await ctx.send('<@' + str(ctx.author.id) + ">, you don't have that much gold!")
    else:
        await ctx.send('This is a host only game, please tag a host to play!')

@dice.error
async def dice_error(ctx, error):
    await ctx.send('An **error** has occurred. Make sure you use `!dice (@USER) (AMOUNT) (RS3 or 07)`.')
###################################3
@bot.command()
async def roll(ctx):
    c.execute('SELECT * FROM dice')
    diceInfo = c.fetchall()
    duel, game = False, None
    for i in diceInfo:
        if ctx.author.id in [i['playerid'], i['hostid']]:
            duel = True
            game = i

    playerid = game['playerid']
    hostid = game['hostid']
    bet = game['bet']
    currency = game['currency']
    roll = game['roll']
    first = game['first']

    if duel:
        if ctx.author.id != first:
            clientseed = getvalue(ctx.author.id, 'clientseed', 'rsmoney')
            roll1, nonce1 = getrandint(ctx.author.id)
            roll2, nonce2 = getrandint(ctx.author.id)
            roll1, roll2 = [int((i - 1)/16.666) + 1 for i in [roll1, roll2]]
            embed = discord.Embed(description='<@' + str(ctx.author.id) + '> has rolled **' + str(roll1 + roll2) + '** out of 12 (' +
                                                str(roll1) + ' + ' + str(roll2) + ')', color=16382207)
            embed.set_author(name='Dice Duel', icon_url=ctx.guild.icon)
            embed.set_image(url='https://cdn.discordapp.com/attachments/616038624143605801/735689548331352114/dicefinal.png')
            embed.set_footer(text='Nonces: ' + str(nonce1) + ', ' + str(nonce2) + ' | Client Seed: "' + str(clientseed) + '"')
            await ctx.send(embed=embed)
            if roll == 0:
                c.execute('UPDATE dice SET first={} WHERE playerid={}'.format(ctx.author.id, playerid))
                c.execute('UPDATE dice SET roll={} WHERE playerid={}'.format(roll1 + roll2, playerid))
            else:
                if roll == roll1 + roll2:
                    embed = discord.Embed(description='Both players rolled **' + str(roll) + '**, it is a tie! Money back!', color=16776960)
                    win = 'tie'
                    update_money(playerid, bet, currency)
                elif ((roll > roll1 + roll2) and (first == hostid)) or ((roll1 + roll2 > roll) and (first == playerid)):
                    embed = discord.Embed(description='<@' + str(hostid) + '> had the higher roll and has won the duel!', color=3997475)
                    win = False
                else:
                    embed = discord.Embed(description='<@' + str(playerid) + '> had the higher roll and has won **' + format_from_k(int(bet * 1.9)) + ' ' + currency + '**!', color=3997475)
                    win = True
                    update_money(playerid, bet * 1.9, currency)
                    update_money(hostid, bet * 0.05, currency)
                ticketbets(ctx.author.id, bet, currency)
                embed.set_author(name='Dice Duel Results', icon_url=ctx.guild.icon)
                embed.set_image(url='https://cdn.discordapp.com/attachments/616038624143605801/735689548331352114/dicefinal.png')
                await ctx.send(embed=embed)
                c.execute('DELETE FROM dice WHERE playerid={}'.format(playerid))
        else:
            await ctx.send('You have already rolled your dice for this duel!')
    else:
        await ctx.send('You are not currently in a dice duel. Tag an open host to start one.')
####################################
@bot.command()
async def host(ctx, toggle: typing.Literal['open', 'close', 'closed', 'opened']):
    host = get(ctx.guild.roles, name='Host')
    openHost = get(ctx.guild.roles, name='Open Host')

    if host in ctx.author.roles:
        if toggle == 'open' or toggle == 'opened':
            await ctx.author.add_roles(openHost)
            c.execute("INSERT INTO openHosts VALUES (%s, %s)", (ctx.author.id, '<:fresh:748229928561934468>'))
            await ctx.send("https://tenor.com/view/open-gif-8591394")
        else:
            await ctx.author.remove_roles(openHost)
            c.execute('DELETE FROM openHosts WHERE id = {}'.format(ctx.author.id))
            await ctx.send("https://tenor.com/view/close-gif-18800320")
        await ctx.message.add_reaction('👍')
    else:
        await ctx.send('Only hosts can ' + toggle + '!')
####################################
@bot.command(aliases = ['s'])
async def skill(ctx, skill: str, levelRange):
    levelRange = levelRange.split('-')
    levelStart, levelEnd = int(levelRange[0]), int(levelRange[1])
    skills = {
                'attack':[(range(1,71), 20, 'Sand Crabs'), (range(70,100), 15, 'Nightmare Zone (Absorptions)')],
                'strength':[(range(1,71), 20, 'Sand Crabs'), (range(70,100), 15, 'Nightmare Zone (Absorptions)')],
                'defence':[(range(1,71), 20, 'Sand Crabs'), (range(70,100), 15, 'Nightmare Zone (Absorptions)')],
                'range':[(range(1,71), 20, 'Sand Crabs'), (range(70,100), 12, 'MM1 Tunnels')],
                'prayer':[(range(1,100), 10, 'Dragon Bones (Superior bones also available)')],
                'fishing':[(range(1,71), 45, 'Various Methods - Tempoross 450k/Kill'), (range(70,100), 30, 'Various Methods - Tempoross 450k/Kill')],
                'runecrafting':[(range(1,78), 80, 'Lava Rune Method'), (range(77,100), 55, 'Zeah (Blood/Soul rune method also available)')],
                'mining':[(range(1,73), 35, 'Motherlode Mine'), (range(72,100), 23, 'Motherlode Mine (Upper Level)')],
                'hunter':[(range(1,10), 0, 'Varrock Museum (Free if going past level 9)'), (range(9,61), 50, 'Various Methods'), (range(60,100), 25, 'Various Methods')],
                'magic':[(range(1,100), 11, 'Splashing (Cost may vary with rune price)\n(MM1 & MM2 tunnel methods also available)')],
                'farming':[(range(1,100), 10, 'Trees/Tithe Farm')],
                'thieving':[(range(1,66), 50, 'Various Methods'), (range(65,100), 25, 'Various Methods')],
                'woodcutting':[(range(1,36), 60, 'Regular, Oaks, Willows'), (range(35,91), 25, 'Teaks'), (range(90,100), 18, 'Redwoods')],
                'slayer':[(range(1,51), 100, 'Tasks at Highest Level Master'), (range(50,100), 60, 'Tasks at Highest Level Master - Cannon Required Levels 50+')],
                'agility':[(range(1,61), 80, 'Various Courses - Marks of Grace 50k Each or Kept by Worker'), (range(60,91), 50, 'Various Courses - Marks of Grace 50k Each or Kept by Worker'), (range(90,100), 40, 'Various Courses - Marks of Grace 50k Each or Kept by Worker')],
                'cooking':[(range(1,100), 6, 'Wines')],
                'fletching':[(range(1,100), 7, 'Darts')],
                'construction':[(range(1,53), 50, 'Various Methods'), (range(52,100), 11, 'Mahogany Tables')],
                'smithing':[(range(1,61), 40, 'Various Methods'), (range(60,100), 16, 'Blast Furnace')],
                'herblore':[(range(1,73), 25, 'Various Methods'), (range(72,100), 9, 'Various Methods')],
                'crafting':[(range(1,67), 25, 'Various Methods'), (range(66,86), 9, 'Air Battlestaves'), (range(85,100), 7, "Black D'hide Bodies")],
                'firemaking':[(range(1,51), 35, 'Various Logs'), (range(50,99), 10, 'Wintertodt - Crates 150k Each or Kept by Worker')]
                                        }

    def findXP(levelStart, levelEnd):
        def totalXP(level):
            double = total = 0
            for i in range(1, level):
                total += math.floor(i + 300 * pow(2, i / 7.0))

            return math.floor(total / 4)

        return totalXP(levelEnd) - totalXP(levelStart)

    if levelStart < 1 or levelStart > 98:
        await ctx.send('Invalid starting level! Please choose a level between 1 and 98.')
    elif levelEnd < 2 or levelEnd > 99:
        await ctx.send('Invalid ending level! Please choose a level between 2 and 99.')
    elif levelStart > levelEnd:
        await ctx.send('Silly goose! You cannot train a skill backwards!')
    else:
        cost, giveInfo, info, XPtotal = 0, True, '', 0
        for i in skills[skill]:
            if levelStart in i[0] and levelEnd in i[0]:
                methodXP = findXP(levelStart, levelEnd)
            elif levelStart in i[0]:
                methodXP = findXP(levelStart, i[0][-1])
            elif levelEnd in i[0]:
                methodXP = findXP(i[0][0], levelEnd)
            elif any(map(lambda v : v in range(levelStart, levelEnd), i[0])):
                methodXP = findXP(i[0][0], i[0][-1])
            else:
                methodXP = 0
                giveInfo = False
            
            if (i[2] + '\n') not in info and giveInfo:
                info += (i[2] + '\n')

            cost += int(methodXP * i[1] * 0.001)
            XPtotal += methodXP
            giveInfo = True

        embed = discord.Embed(description='**Price:** ' + format_from_k(cost) + '\n\n**Required XP:** {:,}'.format(XPtotal) + ' XP\n\n**Methods/Additional Info:**\n' + info, color=14812678)
        embed.set_author(name=skill.title() + ' Calculator', icon_url=ctx.guild.icon)
        embed.set_footer(text='Tweak Services - React with 🎟️ to create a private ticket room')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/863252433185931285/882462681490141275/OSMS.gif')
        sent = await ctx.send(embed=embed)
        await sent.add_reaction('🎟️')

        def check(reaction, user):
            return user == ctx.author and reaction.message == sent and str(reaction.emoji) == '🎟️'

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            embed.set_footer(text='Tweak Services - Timed out. Use !s again to create a private ticket room')
            await sent.clear_reactions()
            await sent.edit(embed=embed)
        else:
            ticket_log = bot.get_channel(1002275447414993027)
            ticket_category = ticket_log.category

            newChannel = await ctx.channel.guild.create_text_channel(ctx.author.name + "'s Ticket", category=ticket_category)
            await newChannel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)

            embed = discord.Embed(description='<@' + str(ctx.author.id) + '>, this is your private ticket room. You or a staff member can use `!close` when you are done to delete the channel.', color=11854069)
            embed.set_author(name=skill.title() + ' Powerleveling', icon_url=ctx.guild.icon)
            embed.set_footer(text='Channel Opened On: ' + str(datetime.datetime.now())[:-7])
            await newChannel.send(embed=embed)
###########################################
@bot.command(aliases = ['q'])
async def quest(ctx, *, questName: str):
    prices = {"Black Knights' Fortress":1500,
            'Below Ice Mountain':1000,
            "Cook's Assistant":300,
            'The Corsair Curse':1700,
            'Demon Slayer':1000,
            "Doric's Quest":200,
            'Dragon Slayer I':2000,
            'Ernest the Chicken':1000,
            'Goblin Diplomacy':300,
            'Imp Catcher':500,
            "The Knight's Sword":1000,
            'Misthalin Mystery':1000,
            "Pirate's Treasure":1000,
            'Prince Ali Rescue':1000,
            'The Restless Ghost':500,
            'Romeo & Juliet':1000,
            'Rune Mysteries':500,
            'Sheep Shearer':500,
            'Shield of Arrav':1400,
            'Vampyre Slayer':500,
            "Witch's Potion":500,
            'X Marks the Spot':700,
            'Animal Magnetism':2600,
            'Another Slice of H.A.M.':2600,
            'The Ascent of Arceuus':2000,
            'Between a Rock...':3000,
            'Big Chompy Bird Hunting':3800,
            'Biohazard':2000,
            'Bone Voyage':1500,
            'Cabin Fever':1500,
            'Client of Kourend':1000,
            'Clock Tower':1000,
            'Cold War':3500,
            'Contact!':3000,
            'Creature of Fenkenstrain':2000,
            'Darkness of Hallowvale':8000,
            'Death Plateau':1000,
            'Death to the Dorgeshuun':3000,
            'The Depths of Despair':1000,
            'Desert Treasure':9000,
            'Devious Minds':2000,
            'The Dig Site':4000,
            'Dragon Slayer II':30000,
            'Dream Mentor':4500,
            'Druidic Ritual':500,
            'Dwarf Cannon':1500,
            "Eadgar's Ruse":3000,
            "Eagles' Peak":2000,
            'Elemental Workshop I':1000,
            'Elemental Workshop II':2000,
            "Enakhra's Lament":2500,
            'Enlightened Journey':3000,
            'The Eyes of Glouphrie':3000,
            'Fairytale I - Growing Pains':3000,
            'Fairytale II - Cure a Queen':4000,
            'Family Crest':2500,
            'The Feud':4000,
            'Fight Arena':2000,
            'Fishing Contest':1000,
            'Forgettable Tale...':4000,
            'The Forsaken Tower':2000,
            'The Fremennik Exiles':4000,
            'The Fremennik Isles':4000,
            'The Fremennik Trials':5800,
            'Garden of Tranquillity':3700,
            "Gertrude's Cat":500,
            'Getting Ahead':2000,
            'Ghosts Ahoy':3000,
            'The Giant Dwarf':2500,
            'The Golem':2000,
            'The Grand Tree':2500,
            'The Great Brain Robbery':3500,
            'Grim Tales':3000,
            'The Hand in the Sand':3000,
            'Haunted Mine':3000,
            'Hazeel Cult':1500,
            "Heroes' Quest":5000,
            'Holy Grail':2000,
            'Horror from the Deep':2000}

    questName = get_close_matches(questName, prices)[0]
    questUrl = quote(questName)

    url = 'https://oldschool.runescape.wiki/w/'+questUrl+'/Quick_guide'

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}

    req = Request(url, headers=hdr)
    bsclient = urlopen(req)
    page_html = bsclient.read()
    bsclient.close()

    page_soup = soup(page_html, "html.parser")
    quest_details = page_soup.find_all("td", {"class":"questdetails-info"})
    quest_reqSoup = quest_details[4].find_all('li')

    try:
        index = [idx for idx, s in enumerate(quest_reqSoup) if 'Completion of' in str(s)][0]
        quest_reqs = re.findall(r'title="(.*?)"', str(quest_reqSoup[index]).replace('"Quest points"', ''))
    except:
        quest_reqs = []

    skill_reqSoup = quest_details[4].find_all('span')
    skill_names = re.findall(r'data-skill="(.*?)"', str(skill_reqSoup))
    skill_levels = re.findall(r'data-level="(.*?)"', str(skill_reqSoup))
    difficulty = str(quest_details[1])[30:-5]
    length = str(quest_details[3])[30:-5]
    skill_reqs = [i + ' ' + j for i, j in zip(skill_levels, skill_names)]
    skill_reqs = 'None' if skill_reqs == [] else ', '.join(skill_reqs)
    quest_reqs = 'None' if quest_reqs == [] else ', '.join(quest_reqs)

    embed = discord.Embed(description='**Price:** ' + format_from_k(prices[questName]) + '\n\n**Length:** ' + length
                                        + '\n\n**Difficulty:** ' + difficulty + '\n\n**Skill Requirements:** ' + skill_reqs
                                        + '\n\n**Quest Requirements** ' + quest_reqs, color=14812678)
    embed.set_author(name=questName + ' Calculator', icon_url=ctx.guild.icon)
    embed.set_footer(text='Tweak Services - React with 🎟️ to create a private ticket room')
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/863252433185931285/882462681490141275/OSMS.gif')
    sent = await ctx.send(embed=embed)
    await sent.add_reaction('🎟️')

    def check(reaction, user):
        return user == ctx.author and reaction.message == sent and str(reaction.emoji) == '🎟️'

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        embed.set_footer(text='Tweak Services - Timed out. Use !s again to create a private ticket room')
        await sent.clear_reactions()
        await sent.edit(embed=embed)
    else:
        ticket_log = bot.get_channel(1002275447414993027)
        ticket_category = ticket_log.category

        newChannel = await ctx.channel.guild.create_text_channel(ctx.author.name + "'s Ticket", category=ticket_category)
        await newChannel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)

        embed = discord.Embed(description='<@' + str(ctx.author.id) + '>, this is your private ticket room. You or a staff member can use `!close` when you are done to delete the channel.', color=11854069)
        embed.set_author(name=questName + ' Completion', icon_url=ctx.guild.icon)
        embed.set_footer(text='Channel Opened On: ' + str(datetime.datetime.now())[:-7])
        await newChannel.send(embed=embed)
###########################################
@bot.command()
async def close(ctx):
    if ctx.channel.category.id == 1001698759429865603:
        await ctx.channel.delete()
    else:
        None
###########################################
@bot.command(aliases = ['autoclickprices', 'autoclick', 'acp'])
async def acPrices(ctx):
    embed = discord.Embed(description='__Firemaker__ - **$3** or **10m**\n\n' +
                                        '__Fly Fisher__ - **$2** or **7m**\n\n' +
                                        '__Fruit Stall Thiever__ - **$1** or **3m**\n\n' +
                                        '__Herblore (Cleaning)__ - **$1** or **3m**\n\n' +
                                        '__Herblore (Unf. Potions)__ - **$1** or **3m**\n\n' +
                                        '__Nightmare Zone__ - **$3** or **10m**\n\n' +
                                        '__Woodcutter (Willows)__ - **$1** or **3m**\n\n' +
                                        '(Requested conigurations may very)', color=14812678)
    embed.set_author(name='Autoclick Config Prices', icon_url=ctx.guild.icon)
    embed.set_footer(text='Tweak Services')
    await ctx.send(embed=embed)
###############################
#Error Handler

@bot.event
async def on_command_error(ctx, err):
    print(err)
    ss = get(bot.guilds, id=860952473061031956)
    report = get(ss.text_channels, id=882466336117260309)
    command = ctx.invoked_with
    embed = discord.Embed(title='An error has occurred', description=f'Error in command {str(command)}: \n `{err}`', timestamp=ctx.message.created_at, color=242424)
    await report.send(embed=embed)




Bot_Token = os.getenv('TOKEN')

async def main():
    await bot.start(str(Bot_Token))

asyncio.run(main())
#https://discordapp.com/oauth2/authorize?client_id=792134008355160065&scope=bot&permissions=8


