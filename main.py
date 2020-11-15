import os
import youtube_dl

from discord.ext import commands
from src.components.Music import Music
from src.components.Degen import Degen
from src.utils.keep_alive import keep_alive

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

keep_alive()
bot = commands.Bot('Venti-san! ', description='Kaze da!')
bot.add_cog(Music(bot))
bot.add_cog(Degen(bot))

@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

bot.run(os.getenv("TOKEN"))

# &api_key=8d40e97f4851737d5d0e23ae039d57081135713c1f8b18c8e1dca8d8e95177b5&user_id=668191