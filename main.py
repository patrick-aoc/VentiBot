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
bot = commands.Bot(command_prefix=['Venti-san! ', '++', 'Venti!'], description='Kaze da!', intents=intents, help_command=None)

firebase_db = FirebaseDB(os.getenv("PROJECT_ID"), os.getenv("FIREBASE_URL"))

bot.add_cog(Music(bot))
bot.add_cog(Degen(bot))
bot.add_cog(Birthday(bot, firebase_db))

@bot.event
async def on_ready():
    print(date.today().isoweekday())
    print(datetime.now().time())
    print(datetime.today().strftime('%m/%d'))
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

@bot.event
async def on_message_delete(message):
  chn = bot.get_channel(int(os.getenv("DISCORD_MSG_LOG")))
  embed = discord.Embed(title='DELETED MESSAGE', color=discord.Color.red())
  embed.set_author(name=str(message.author))
  embed.add_field(name="Message", value=message.content)
  embed.set_footer(text="Channel Origin - {}".format(str(message.channel)))
  await chn.send(embed=embed)

@bot.event
async def on_message_edit(message_before, message_after):
  if "https" not in message_before.content:
    chn = bot.get_channel(int(os.getenv("DISCORD_MSG_LOG")))
    embed = discord.Embed(title='EDITED MESSAGE', color=discord.Color.orange())
    embed.set_author(name=str(message_before.author))
    embed.add_field(name="Old Message", value=message_before.content)
    embed.add_field(name="New Message", value=message_after.content)
    embed.set_footer(text="Channel Origin - {}".format(str(message_before.channel)))
    await chn.send(embed=embed)

@aiocron.crontab('0 14 * * *')
async def birthday():
  cd = datetime.today().strftime('%m/%d').split("/")
  month = int(cd[0])
  day = int(cd[1])
  #channel = bot.get_channel(int(os.getenv("DISCORD_BOT_TESTING")))
  channel = bot.get_channel(int(os.getenv("DISCORD_GENERAL")))

  for key, value in firebase_db.list_birthdays():
    bd = value["birthday"].split("/")
    if month == int(bd[0]) and day == int(bd[1]):
      cb = value["celebrant_id"]
      await channel.send("It's <@{}>'s birthday today! Happy birthday desu nyah~ uwu :birthday: :confetti_ball:".format(cb))
      await channel.send(file=discord.File('./src/res/bd.jpg'))

@aiocron.crontab('0 22 * * 3,6')
async def crystal_chunks_and_parametric():
  channel = bot.get_channel(int(os.getenv("DISCORD_GACHA_GAMES")))
  ping = "<@&{}>".format(os.getenv("DISCORD_CRYSTAL_CHUNKS"))
 
  if date.today().isoweekday() == 3:
    await channel.send(ping, file=discord.File('./src/res/cc_1.png'))
    await channel.send("<@&{}> Also, don't forget to use the parametric transformer for this week! uwu".format(os.getenv("DISCORD_GENSHIN_COOP")))
  elif date.today().isoweekday() == 6:
    await channel.send(ping, file=discord.File('./src/res/cc_2.png'))

bot.run(os.getenv("TOKEN"))
