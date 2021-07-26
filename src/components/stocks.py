import discord
from discord.ext import commands

import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

import os

from datetime import datetime
from pytz import timezone


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
        elif cmd.lower() == "avg":
          if len(args) != 2:
            await ctx.send("Invalid number of arguments specified for 'AVG'. For more information, please specify '++stocks help'")
          else:
            await self._avg(ctx, args[1])
        elif cmd.lower() == "open":
          if len(args) != 1:
            await ctx.send("Invalid number of arguments specified for 'OPEN'. For more information, please specify '++stocks help'")
          else:
            await self._open(ctx)
        elif cmd.lower() == "history":
          if len(args) != 1:
            await ctx.send("Invalid number of arguments specified for 'HISTORY'. For more information, please specify '++stocks help'")
          else:
            await self._history(ctx)
        elif cmd == "help":
          await self._help(ctx)

        else:
          await ctx.send("Invalid command '{c}' specified".format(c=cmd))    
    
    async def _help(self, ctx: commands.Context):
        await ctx.send("Not yet implemented")

    async def _bto(self, ctx: commands.Context, stock, price):
      # Perform a lookup for the stock. If it's valid, add it
      # as an entry. O/w, reject
      if stock.upper() in self.firebase_db.get_symbols():
        try:
          px = round(float(price), 2)
          if px < 0:
            await ctx.send("Price cannot be negative")
          else:
            if self.firebase_db.bto(stock, price):
              await ctx.send("Successfully bought to open (BTO) on the stock {} at the price ${} CAD".format(stock, px))
            else:
              await ctx.send("Failed to register the entry.")
        except ValueError:
          await ctx.send("Invalid price specified")
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))    

    async def _stc(self, ctx: commands.Context, stock, price):
      if stock.upper() in self.firebase_db.get_symbols():
        try:
          px = round(float(price), 2)
          if px < 0:
            await ctx.send("Price cannot be negative")
          else:
            if self.firebase_db.stc(stock, price):
              await ctx.send("Successfully sold to close (STC) on the stock {} at the price ${} CAD".format(stock, px))
            else:
              await ctx.send("Failed to register the entry. Either you have never BTO'd on the stock or your last transaction with the stock was a STC.")
        except ValueError:
          await ctx.send("Invalid price specified")
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))  

    async def _avg(self, ctx: commands.Context, stock):
      if stock.upper() in self.firebase_db.get_symbols():
        avg, count = self.firebase_db.avg(stock)
        await ctx.send("The average for the stock {} is ${} CAD (based on {} entries)".format(stock.upper(), avg, count)) 
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))  

    async def _open(self, ctx: commands.Context):
      open_pos = ""

      for key, value in self.firebase_db.list_stocks():
        stock_entries = self.firebase_db.list_entries(key)

        if len(stock_entries) > 0:
          for i in reversed(stock_entries):
            entry = i[1]

            if entry["type"] == "BTO":
              avg, count = self.firebase_db.avg(key)
              open_pos += "{} ..........  ${} CAD (over {} entries)\n".format(key, avg, count)
            break
  
      if open_pos == "":
        await ctx.send("You have not exited from any positions as of yet")  
      else:
        embed = discord.Embed(title="Jay's Plays", color=discord.Color.blurple())
        embed.add_field(name="Open Positions", value=open_pos)
        await ctx.send(embed=embed)

    async def _history(self, ctx: commands.Context):
      embed = discord.Embed(title="Jay's History", color=discord.Color.blurple())

      for key, value in self.firebase_db.list_stocks():
        hist = ""
        stock_entries = self.firebase_db.list_entries(key)

        if len(stock_entries) > 0:
          pairs = dict()
          e = 1

          # Go through all the entries. Only consider the entries
          # if they've been closed and are also within the date range
          for i in reversed(stock_entries):
            entry = i[1]
            
            if entry["type"] == "STC":
              fmt = '%Y-%m-%d'
              cdt = datetime.strptime(datetime.now(timezone("US/Eastern")).strftime(fmt), fmt)
              dt = datetime.strptime(entry["date"].split()[0], fmt)
              
              if (cdt - dt).days <= 30:
                hist += "\n{} .......... ${} CAD .......... ".format(entry["date"].split()[0], entry["price"])
                # pairs[e - 1] = {"date": entry["date"].split()[0], "entries": [], "closing_price": entry["price"]}
                e += 1
                continue
            else:
              if e == 1:
                pass
              else:
                hist += "${} CAD; ".format(entry["price"])
                # curr_entries = pairs[e - 1]["entries"]
                # curr_entries.append(entry["price"])
                # pairs[e - 1]["entries"] = curr_entries
          
          if e != 1:
            embed.add_field(name="{} - (Closing Date, Closing Price, Entry Price(s))".format(key), value=hist, inline = False)
            
      await ctx.send(embed=embed)
            

        


