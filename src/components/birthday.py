import discord
from discord.ext import commands

import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

import os


class Birthday(commands.Cog):

    def __init__(self, bot: commands.Bot, firebase_db):
        self.bot = bot
        self.voice_states = {}
        self.firebase_db = firebase_db.get_bday_ref()

    @commands.command(name='birthday', invoke_without_subcommand=True)
    async def _birthday(self, ctx: commands.Context, *args):
        
      if len(args) > 0:
        cmd = args[0]

        if cmd == "add":
          if len(args) != 3:
            await ctx.send("Invalid number of arguments specified for 'add'. For more information, please specify 'Venti-san! birthday ?'")
          else:
            await self._add_bd(ctx, args[1], args[2])
        elif cmd == "list":
          await self._get_bds(ctx)
        elif cmd == "help":
          await self._help(ctx)
        elif cmd == "list":
          await self._get_bds(ctx)
        else:
          await ctx.send("Invalid command '{c}' specified".format(c=cmd))    
    
    async def _help(self, ctx: commands.Context):
        await ctx.send("Not yet implemented")

    async def _add_bd(self, ctx: commands.Context, birthday, celebrant):
      if "/" in birthday or "-" in birthday:
        delim = "/" if "/" in birthday else "-"

        try:

          # Birthdays must be in the format:
          # MM-DD-YYYY or MM/DD/YY
          year = int(birthday.split(delim)[2])
          month = int(birthday.split(delim)[0])
          day = int(birthday.split(delim)[1])

          bdate = datetime.datetime(year, month, day)
          cb = None

          async for mem in ctx.guild.fetch_members(limit= None):
            uname = str(mem).split("#")[0]
            uid = str(mem).split("#")[1]

            if celebrant in uname:
              cb = mem
              break

          self.firebase_db.push(
              {
                "celebrant": str(cb),
                "birthday": birthday
              }
          )
          await ctx.send("Birthday has been added for <@{}> ... {}".format(cb.id, bdate))
        except Exception as e:
          print(e)
      else:
        pass

    async def _get_bd(self, ctx: commands.Context, celebrant):
      pass

    async def _get_bds(self, ctx: commands.Context):
        embed = (discord.Embed(title='Birthdays',
                               color=discord.Color.blurple()))
        birthdays = ""

        for key, value in (self.firebase_db.get()).items():
            birthdays += "{} ... {} \n".format(value["celebrant"], value["birthday"])

        embed.add_field(name="Celebrant ... Birthday", value=birthdays)
        await ctx.send(embed=embed)
    
      