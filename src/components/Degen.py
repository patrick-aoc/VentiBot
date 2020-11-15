import requests

from discord.ext import commands
from random import randrange


class Degen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(name='gimme')
    async def _lewd(self, ctx: commands.Context, *, search = 'Venti'):
      pid = randrange(100)
      url = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=' + search + '&limit=1&pid=' + str(pid)

      try:
        req = requests.get(url)    
        await ctx.send(req.json()[0]["file_url"])
      except:
        await ctx.send('Gomenasai Traveler-dono, nothing came up for "{}" :cry:'.format(str(search)))

      return
