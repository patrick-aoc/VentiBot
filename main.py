import os
import youtube_dl

from discord.ext import commands
from src.components.Music import Music
from src.components.Degen import Degen
from src.utils.keep_alive import keep_alive

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

keep_alive()
bot = commands.Bot(command_prefix=['Venti-san! ', '++', 'Venti!'], description='Kaze da!')
bot.add_cog(Music(bot))
bot.add_cog(Degen(bot))

@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

bot.run(os.getenv("TOKEN"))
