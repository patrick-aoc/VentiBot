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

@aiocron.crontab('0 9 * * *')
async def birthday():
    channel = bot.get_channel(os.getenv("DISCORD_BOT_TESTING"))
    await channel.send('Hour Cron Test')

bot.run(os.getenv("TOKEN"))

