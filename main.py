from datetime import date, datetime

import aiocron
import discord
import os
import youtube_dl

from discord.ext import commands
from src.components.music import Music
from src.components.etc.firebase_db import FirebaseDB
from src.components.birthday import Birthday
from src.components.degen import Degen
from src.utils.keep_alive import keep_alive

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

intents = discord.Intents.default()
intents.members = True

keep_alive()
bot = commands.Bot(command_prefix=['Venti-san! ', '++', 'Venti!'], description='Kaze da!', intents=intents)

firebase_db = FirebaseDB(os.getenv("PROJECT_ID"), os.getenv("FIREBASE_URL"))

bot.add_cog(Music(bot))
bot.add_cog(Degen(bot))
bot.add_cog(Birthday(bot, firebase_db))

@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

@aiocron.crontab('* * * * *')
async def test():
  channel = bot.get_channel(int(os.getenv("DISCORD_BOT_TESTING")))
  print(datetime.now().time())

@aiocron.crontab('0 1 * * 4,7')
async def crystal_chunks_and_parametric():
  channel = bot.get_channel(int(os.getenv("DISCORD_GACHA_GAMES")))
  ping = "<@&{}>".format(os.getenv("DISCORD_CRYSTAL_CHUNKS"))

  if date.today().isoweekday() == 4:
    await channel.send(ping, file=discord.File('./src/res/cc_1.png'))
    await channel.send("<@&{}> Also, don't forget to use the parametric transformer for this week! uwu".format(os.getenv("DISCORD_GENSHIN_COOP")))
  elif date.today().isoweekday() == 7:
    await channel.send(ping, file=discord.File('./src/res/cc_2.png'))

bot.run(os.getenv("TOKEN"))
