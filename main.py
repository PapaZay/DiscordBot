import os
import discord
import requests
import json
import random
from replit import db


intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = discord.Client(intents=intent)

sad_words = ["sad", "depressed", "angry", "miserable"]

starter_encouragements = ["Cheer up!", "Looking mad swole dawg"]

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def update_encouragements(encouraging_message):

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if message.content.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  if any(word in msg for word in sad_words):
    await message.channel.send(random.choice(starter_encouragements))

client.run(os.environ['TOKEN'])
