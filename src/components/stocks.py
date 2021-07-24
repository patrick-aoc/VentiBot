import discord
from discord.ext import commands

import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

import os


class Stocks(commands.Cog):

    def __init__(self, bot: commands.Bot, firebase_db):
        self.bot = bot
        self.voice_states = {}
        self.firebase_db = firebase_db

    @commands.command(name='stocks', invoke_without_subcommand=True)
    async def _stocks(self, ctx: commands.Context, *args):
      author_id = str(ctx.message.author.id)
      if str(os.getenv("DISCORD_MY_ID")) != author_id and str(os.getenv("DISCORD_JAY_ID")) != author_id:
        await ctx.send("You are not allowed to use the stocks feature")
        return

      if len(args) > 0:
        cmd = args[0]

        if cmd.lower() == "bto":
          if len(args) != 3:
            await ctx.send("Invalid number of arguments specified for 'BTO'. For more information, please specify '++stocks help'")
          else:
            await self._bto(ctx, args[1], args[2])
        elif cmd.lower() == "stc":
          if len(args) != 3:
            await ctx.send("Invalid number of arguments specified for 'STC'. For more information, please specify '++stocks help'")
          else:
            await self._stc(ctx, args[1], args[2])
        elif cmd == "list":
          await self._get_bds(ctx)
        elif cmd == "help":
          await self._help(ctx)

        else:
          await ctx.send("Invalid command '{c}' specified".format(c=cmd))    
    
    async def _help(self, ctx: commands.Context):
        await ctx.send("Not yet implemented")

    async def _bto(self, ctx: commands.Context, stock, price):
      # Perform a lookup for the stock. If it's valid, add it
      # as an entry. O/w, reversed
      if stock.upper() in self.firebase_db.get_symbols():
        #try:
        px = round(float(price), 2)
        if px < 0:
          await ctx.send("Price cannot be negative")
        else:
          
          if self.firebase_db.bto(stock, price):
            await ctx.send("Successfully registered the entry")
          else:
            await ctx.send("Failed to register the entry. It might b")
        #except ValueError:
          #await ctx.send("Invalid price specified")
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))    

    async def _stc(self, ctx: commands.Context, celebrant = None):
      cb = None

      if celebrant:
        async for mem in ctx.guild.fetch_members(limit= None):
          uname = str(mem).split("#")[0]
          uid = str(mem).split("#")[1]
          did = str(mem.id)

          if (celebrant.split("#")[0] in uname and celebrant.split("#")[1] in uid) or str(did) in str(celebrant):
            author_id = str(ctx.message.author.id)
            
            if str(os.getenv("DISCORD_MY_ID")) == author_id or did == author_id:
              cb = mem
              break
            else:
              await ctx.send("You are only allowed to remove your own birthday!")
              return
      else:
        cb = await ctx.guild.fetch_member(ctx.message.author.id)
      
      if not self.firebase_db.remove_bd(cb):
        await ctx.send("Failed to remove the celebrant's birthday. Either they no longer exist in the list or something went wrong with the Firebase database.")
      else:
        await ctx.send("Birthday has been removed for {}".format(cb))

    async def _get_bd(self, ctx: commands.Context, celebrant):
      pass

    async def _get_bds(self, ctx: commands.Context):
        embed = discord.Embed(title='Birthdays', color=discord.Color.blurple())
        birthdays = ""
        for key, value in self.firebase_db.list_birthdays():
          bd = value["birthday"]
          birthdays += "{} .......... {} ({}) \n".format(value["celebrant_name"], bd, self._get_month(int(bd.split("/")[0])) + " " + bd.split("/")[1])

        if birthdays == "":
          await ctx.send("There are no birthdays recorded in the database")
        else:
          embed.add_field(name="Celebrant .......... Birthday", value=birthdays)
          await ctx.send(embed=embed)

    def _is_valid_date(self, month, dte):
      is_valid = True
      
      try:
        m = self._get_month(month)

        if month % 2 == 0:
          if m == "February":
            is_valid = dte >= 1 and dte <= 29
          else:
            is_valid = dte >= 1 and dte <= 30
        else:
          is_valid = dte >= 1 and dte <= 31

      except KeyError:
        is_valid = False
      return is_valid

    def _get_month(self, num):
      months = {
          1: "January",
          2: "February",
          3: "March",
          4: "April",
          5: "May",
          6: "June",
          7: "July",
          8: "August",
          9: "September",
          10: "October",
          11: "November",
          12: "December"
      }
      return months[num]
    
      