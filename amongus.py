import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
channel = ''
deadMates = []
gameState = False
roundState = False
roomCode = ''
hostName = ''
host = ''

def isCurrentHost(authorName):
    if hostName != authorName:
        return False
    return True

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(f'{bot.user} is currently in:')
    guildList = '\n - '.join([guild.name for guild in bot.guilds])
    print(f'Guilds:\n - {guildList}')

@bot.command()
async def initiate(ctx):
    global host
    if isCurrentHost(ctx.author.name):
        global gameState
        if gameState:
            await ctx.send('Game has already been started. Finish the game using !endGame to restart.')
        else:
            if channel == '':
                await ctx.send('Use !host to identify host before starting a game.')
            else:
                gameState = True
                crewList = '\n - '.join([member.name for member in channel.members])
                await ctx.send(f'Game has been initiated. Here are the current crew members:\n - {crewList}')
    elif hostName != '':
        await ctx.send('Only the host can start the game. Calling ' + host.mention + ' to start the game.')
    else:
        await ctx.send('No host has been set yet. Use !host to host the game.')

@bot.command()
async def crewMembers(ctx):
    if channel == '':
        await ctx.send('Use !host to identify host before checking the Crew Members.')
    else:
        crewList = '\n - '.join([member.name for member in channel.members])
        await ctx.send(f'Crew Members:\n - {crewList}')

@bot.command()
async def host(ctx):
    global channel
    global hostName
    global host
    if gameState:
        await ctx.send('Game has already been initiated. Use !endGame first before passing host.')
    else:
        guild = ctx.guild
        host = ctx.author
        hostName = host.name
        flag = 0
        for channels in guild.voice_channels:
            if host in channels.members:
                channel = channels
                await ctx.send(hostName + ' has hosted a game. Join the voice channel "' + channel.name + '" to join the game.')
                flag = 1
                break
        if not flag:
            await ctx.send(hostName + ' is not on a Voice Channel. Join a voice channel before hosting.')

@bot.command()
async def roundStart(ctx):
    if not gameState:
        await ctx.send('Game has not been started yet. Use !initiate to start game.')
    else:
        global roundState
        if roundState:
            await ctx.send('Round is currently ongoing. Use !discuss to start discussion.')
        else:
            if channel == '':
                await ctx.send('Use !host to identify host before starting a game.')
            else:
                roundState = True
                await ctx.send('Shh! Round has been started. Muting everyone in ' + channel.name)
                for member in channel.members:
                    await member.edit(mute=1)

@bot.command()
async def discuss(ctx):
    global roundState
    if not roundState:
        await ctx.send('Round has not been started yet or discussion is currently ongoing. Use !roundStart to begin next round.')
    else:
        if channel == '':
            await ctx.send('Use !host to identify host before starting a game.')
        else:
            roundState = False
            await ctx.send('Discussion has been initiated. Unmuting surviving crew members.')
            for member in channel.members:
                if member.name not in deadMates:
                    await member.edit(mute=0)

@bot.command()
async def dead(ctx, *users: discord.Member):
    if gameState:
        global deadMates
        await ctx.send('Tagging dead crew mates...')
        for user in users:
            deadMates.append(user.name)
            await user.edit(mute=1)
    else:
        await ctx.send("Game is not even initiated yet. You really want to kill them that badly?")

@bot.command()
async def deadcrew(ctx):
    crewList = '\n - '.join([member for member in deadMates])
    await ctx.send(f'Dead mates: {crewList}')

@bot.command()
async def revoke(ctx, user: discord.Member):
    global deadMates
    if user.name in deadMates:
        await ctx.send('Removing ' + user.name +  "'s dead tag.")
        deadMates.remove(user.name)
        if not roundState:
            await user.edit(mute=0)
    else:
        await ctx.send(user.name + ' is not tagged as a dead crew mate. Use this command to undo dead tags.')

@bot.command()
async def endGame(ctx):
    global roundState
    global gameState
    if not gameState:
        await ctx.send('Game has not been started yet. Use !initiate to start game.')
    else:
        global deadMates
        for member in channel.members:
            await member.edit(mute=0)
        deadMates = []
        gameState = False
        roundState = False
        await ctx.send('Game state has been restarted. Use !initiate to start a new game.')

@bot.command()
async def setCode(ctx, code: str):
    global roomCode
    roomCode = code
    await ctx.send('Room Code has been set to: ' + code)

@bot.command()
async def getCode(ctx):
    if roomCode != '':
        await ctx.send('Room Code is currently set to: ' + roomCode)
    else:
        await ctx.send('There are currently no existing rooms.')

bot.run(TOKEN)
