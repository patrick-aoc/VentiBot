import re
import requests
from src.components.etc import constants

from discord.ext import commands
from random import randrange

class Degen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))
        
    @commands.command(name='gimme')
    async def _lewd(self, ctx: commands.Context, *, search = 'Venti'):
      lowered = search.lower()

      # Check if user was trying to search for a loli
      if (lowered in constants.genshin_questionable):
        await ctx.send("Traveler-dono...seek help :cry:")
        return
      
      # Check if user tried to do shady stuff
      if (not lowered.isalnum()):
        await ctx.send("Nice try, Traveler-dono :wink: ")
        return

      # Check if user tried to invoke this command in the appropriate channel
      if (ctx.message.channel.name not in constants.allowed_channels):
        await ctx.send("Traveler-dono, baka!! This isn't the right channel for this kind of stuff... :confounded: :point_right: :point_left:")
        return

      # Check if user tried to search for a male
      if (lowered in constants.genshin_males):
        await ctx.send("Traveler-dono... are you perhaps... a homosexual? :face_with_hand_over_mouth:")
        return

      pid = randrange(100)
      query = search
      if (lowered in constants.genshin_females):
        query = lowered + "_(Genshin_Impact)"
        
      url = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=' + query + "+-loli" + '&limit=1&pid=' + str(pid)

      try:
        req = requests.get(url)    
        await ctx.send(req.json()[0]["file_url"])
      except:
        await ctx.send('Gomenasai Traveler-dono, nothing came up for "{}" :cry:'.format(str(search)))

      return
