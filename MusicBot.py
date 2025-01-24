import discord
from collections import deque
from dotenv import load_dotenv
import os
from discord.ext import commands
import ffmpeg
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')

queue = deque()
names = deque()
current_song_url = None
current_title = None
def get_youtube_url(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }
    URL = url
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URL, download=False) 

        
        title = info['title']
        return info['url'], title     
    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def play(ctx,url: str):
    global current_song_url
    global current_title
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel gang...")
        return
    
    channel = ctx.author.voice.channel

    if not ctx.voice_client:
        await channel.connect()

        
    voice_client = ctx.voice_client
    audio_url, title = get_youtube_url(url)

    if audio_url:
        queue.append(audio_url)
        names.append(title)

        if not voice_client.is_playing():
            #current_song_url = audio_url
            #current_title = title
            await playing_next(ctx)
        else:
            #queue.append(audio_url)
            #names.append(title)
            await ctx.send(f"{current_title} is playing, {title} added to queue")
    else:
        await ctx.send("Could not find a valid audio source for this video.")

@bot.command()
async def current(ctx):
    global current_title
    await ctx.send(f"{current_title}")
        
@bot.command()
async def skip(ctx):
    global current_title

    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel gang...")
        return
    
    voice_client = ctx.voice_client

    if not voice_client or not voice_client.is_playing():
        await ctx.send("There's nothing to skip bro...")
        return
    
    await ctx.send(f"Skipping {current_title}")
    voice_client.stop()

    if queue:
        await playing_next(ctx)
    else:
        current_title = None
        current_song_url = None
        await ctx.send("No songs in queue brody.")


async def playing_next(ctx):
    global current_title
    global current_song_url
    voice_client = ctx.voice_client
    if not queue:
        current_title = None
        current_song_url = None
        await ctx.send("Queue is empty, add a song gango.")
        return
    
    
    current_song_url = queue.popleft()
    current_title = names.popleft()

    #current_song_url = next_song
    #current_title = names.popleft()

    def after_playing(error):
        if queue:
            #asyncio.run_coroutine_threadsafe(playing_next(ctx), bot.loop)
            bot.loop.create_task(playing_next(ctx))

    voice_client.play(discord.FFmpegPCMAudio(current_song_url), after=after_playing)
    await ctx.send(f"Now Playing: {current_title}")


@bot.command()
async def command(ctx):
    await ctx.send("!play <song_url> - plays the audio associated with the url\n !skip - skips the current song and plays next song in queue.\n !restart - restarts current song\n !stop - stops current song\n !leave - Bot leaves the voice channel")

@bot.command()
async def restart(ctx):
    global current_song_url
    global current_title

    if not ctx.author.voice:
        await ctx.send("You not in a voice channel gang.")
        return 
    
    if not current_song_url:
        await ctx.send("No song to restart!")
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
     
    if current_song_url:
        voice_client = ctx.voice_client
        voice_client.play(discord.FFmpegPCMAudio(current_song_url))
        await ctx.send(f"Now playing: {current_title}")

    
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped playing.")
    else:
        await ctx.send("No audio is playing.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send(f"Disconnected from {ctx.channel.name}")
    else:
        await ctx.send("Not connected to voice channel")

bot.run(discord_token)