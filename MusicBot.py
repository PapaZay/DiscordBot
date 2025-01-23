import discord
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

current_song_url = None
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
        return info['url']      
    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def play(ctx,url: str):
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel gang...")
        return
    
    channel = ctx.author.voice.channel

    if not ctx.voice_client:
        await channel.connect()

    voice_client = ctx.voice_client

    if not voice_client.is_playing():
        audio_url = get_youtube_url(url)
        global current_song_url
        current_song_url = audio_url
        voice_client.play(discord.FFmpegPCMAudio(audio_url))
        await ctx.send("Now playing:")
        
    else:
        await ctx.send("Already playing audio!")
    
@bot.command()
async def restart(ctx):
    global current_song_url

    if not ctx.voice_client:
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
        await ctx.send("Now playing:")

    
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


"""@bot.event
async def on_message(message):
        # don't respond to ourselves
    if message.author == bot.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')"""



bot.run(discord_token)