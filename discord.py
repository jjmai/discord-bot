import asyncio
import discord
from discord import guild
from discord.ext import commands
import os
import json
import requests
import random
import webbrowser
import urllib.parse, urllib.request, re

import youtube_dl

#youtube convertor
ydl_opts ={
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'

    }]
}

client = commands.Bot(command_prefix = ".")

list_queue ={}
list_count=0

list_quote = ['Mom, Dad, I Love You. Please Don’t Sell Me To Paris Hilton.',
              'My Name Is Butters. I’m Eight Years Old, I’m Blood Type O, And I’m Bi-Curious.',
              'Hey, Government. It’s Me, Butters.',
              'You Think It’s Because Gay Weiners Are Less Threatening To Women Viewers?',
              'Do You Know What I Am Saying?',
              'Hey, Little Dude, You’ve Got Some Crap Right Here.” “That’s My Face, Sir!',
              'I’m Pretty Sure The Car Is Moving. Looks Like I’m Heading For The Water.',
              'Well, Yeah, I’m Sad, But At The Same Time, I’m Really Happy That Something Can Make Me Feel That Sad.',
              'Oh, Hamburgers!',
              'Lu-Lu-Lu, I’ve Got Some Apples. Lu-Lu-Lu, You’ve Got Some, Too!']

target =""

#receives random quote
def get_quote():
    rando = random.randint(0,9)
    quote = list_quote[rando]

    return quote

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def join(ctx):
    voice = ctx.message.author.voice
    channel = voice.channel
    await channel.connect()

#@client.command()
#async def leave(ctx):
 #   voice_client = ctx.message.guild.voice_client
  #  await voice_client.disconnect()

@client.command()
async def youtube(ctx,*,search):
    query_string = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r'/watch\?v=(.{11})',htm_content.read().decode())
    await ctx.send('http://www.youtube.com/watch?v=' + search_results[0])

#play youtube song
@client.command()
async def play(ctx, url:str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("wait")

    if not ctx.voice_client:
        voice_channel = discord.utils.get(ctx.guild.voice_channels,name ='Losers')
        await voice_channel.connect()
        voice = discord.utils.get(client.voice_clients,guild=ctx.guild)

    if url.startswith("http"):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3") and not (file.startswith("donnie") or file.startswith("lululu")):
                os.rename(file, "song.mp3")
        voice.play(discord.FFmpegPCMAudio("song.mp3"))
    else:
        query_string = urllib.parse.urlencode({
            'search_query': url
        })
        htm_content = urllib.request.urlopen(
            'http://www.youtube.com/results?' + query_string
        )
        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        url = 'http://www.youtube.com/watch?v=' + search_results[0]
        await ctx.send(url)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3") and not (file.startswith("donnie") or file.startswith("lululu")):
                os.rename(file, "song.mp3")
        voice.play(discord.FFmpegPCMAudio("song.mp3"))


#specifically plays looloo
@client.command()
async def looloo(ctx):
    try:
        voice_channel = discord.utils.get(ctx.guild.voice_channels,name ='Losers')
        voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio("lululu.mp3"))
    except PermissionError:
        await ctx.send("Butters is not in a channel yet!")

@client.command()
async def donnie(ctx):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name='Losers')
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio("donnie.mp3"))

@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected:
        await voice.disconnect()
    else:
        await ctx.send("Bot already connected")

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("no audio playing")

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("no audio paused")

@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if ctx.voice_client:
        voice.stop()

@client.command()
async def queue(ctx):
    if ctx.voice_client:
        for i in range(0,list_count):
            print(i,":" , list_queue[i])

@client.command()
async def say(ctx):
    quote = get_quote()
    await ctx.send(quote)

#marks a target
@client.command()
async def mark(ctx,message:str):
    global target
    target = message
    print(target)

#interrupt
@client.event
async def on_voice_state_update(member, prev, cur):
    user = f"{member.name}#{member.discriminator}"

    voice_channel = discord.utils.get(member.guild.voice_channels, name='Losers')
    voice = discord.utils.get(client.voice_clients, guild=member.guild)

    if voice and mark == "":
        await voice.move_to(voice_channel)
        await voice_channel.connect()
    if cur.afk and not prev.afk:
        print(f"{user} went AFK!")
    elif prev.afk and not cur.afk:
        print(f"{user} is no longer AFK!")
    elif cur.self_mute and not prev.self_mute and target == user: # Would work in a push to talk channel
        print(f"{user} stopped talking!")
        voice.pause()
    elif prev.self_mute and not cur.self_mute and target == user: # As would this one
        print(f"{user} started talking!")
        if voice.is_paused():
            voice.resume()
        else:
            voice.play(discord.FFmpegPCMAudio("lululu.mp3"))

@client.event
async def move(ctx,prev,cur):
    if(prev.channel is None and cur.channel is not None):
        author = ctx.message.author
        channel = client.get_channel(398030725720571912)
        await author.move_to(channel)
        print("moved")

#client.run('ODQ1NDQ4MTI1NjgxMzY5MTM4.YKhG7A.kt8D8aoi5IAqTjkHfXI35cqsAbQ')
