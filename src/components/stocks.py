import discord
from discord.ext import commands

import datetime
import os
from pytz import timezone

from src.res.help_res import stocks_help


class Stocks(commands.Cog):

    def __init__(self, bot: commands.Bot, firebase_db):
        self.bot = bot
        self.voice_states = {}
        self.firebase_db = firebase_db

    @commands.command(name='BTO', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def bto(self, ctx: commands.Context, *args):
      """
      BTO - Buy to Open

      Make an entry for a stock at a given price for the user that 
      called the command.
      """
      if len(args) != 2:
        await ctx.send("Invalid number of arguments specified for 'BTO'. For more information, please specify '++stocks help'")
      else:
        await self._bto(ctx, args[0], args[1])

    @commands.command(name='STC', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def stc(self, ctx: commands.Context, *args):
      """
      STC - Sell to Close
      
      Close the entries for a stock at a given price for the user
      that called the command.
      """
      if len(args) != 2:
        await ctx.send("Invalid number of arguments specified for 'STC'. For more information, please specify '++stocks help'")
      else:
        await self._stc(ctx, args[0], args[1])

    @commands.command(name='AVG', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def avg(self, ctx: commands.Context, *args):
      """
      Returns the average value for a given stock based on the most recent
      set of (open) purchased entries that have not yet been closed.
      """
      if len(args) != 1:
        await ctx.send("Invalid number of arguments specified for 'AVG'. For more information, please specify '++stocks help'")
      else:
        await self._avg(ctx, args[0])

    @commands.command(name='OPEN', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def open(self, ctx: commands.Context, *args):
      """
      Returns all the open positions (that haven't been closed)
      for the user calling the command.
      """
      await self._open(ctx)
    
    @commands.command(name='HISTORY', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def history(self, ctx: commands.Context, *args):
      """
      Returns a history of every purchase that the user
      calling the command has closed.
      """
      await self._history(ctx)

    @commands.command(name='HELP', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def help(self, ctx: commands.Context):
        user = await ctx.guild.fetch_member(ctx.message.author.id)
        await user.send(stocks_help)
        await ctx.send("Please check your DMs for reference to my comamands pertaining to Stocks")

    async def _bto(self, ctx: commands.Context, stock, price):
      # Perform a lookup for the stock. If it's valid, add it
      # as an entry. O/w, reject
      if stock.upper() in self.firebase_db.get_symbols():
        try:
          px = round(float(price), 2)
          if px < 0:
            await ctx.send("Price cannot be negative")
          else:
            if self.firebase_db.bto(stock, price, ctx.message.author.id):
              await ctx.send("Successfully bought to open (BTO) on the stock {} at the price ${} USD".format(stock, format(float(px), ".2f")))
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
            if self.firebase_db.stc(stock, price, ctx.message.author.id):
              await ctx.send("Successfully sold to close (STC) on the stock {} at the price ${} USD".format(stock, format(float(px), ".2f")))
            else:
              await ctx.send("Failed to register the entry. Either you have never BTO'd on the stock or your last transaction with the stock was a STC.")
        except ValueError:
          await ctx.send("Invalid price specified")
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))  

    async def _avg(self, ctx: commands.Context, stock):
      if stock.upper() in self.firebase_db.get_symbols():
        avg, count = self.firebase_db.avg(stock, ctx.message.author.id)
        await ctx.send("Your average for the stock {} is ${} USD (based on {} entries)".format(stock.upper(), format(float(avg), ".2f"), count)) 
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))  

    async def _open(self, ctx: commands.Context):
      open_pos = ""

      for key, value in self.firebase_db.list_stocks(ctx.message.author.id):
        stock_entries = self.firebase_db.list_entries(key, ctx.message.author.id)

        if len(stock_entries) > 0:
          for i in reversed(stock_entries):
            entry = i[1]

            if entry["type"] == "BTO":
              avg, count = self.firebase_db.avg(key, ctx.message.author.id)
              open_pos += "{} ..........  ${} USD (over {} entries)\n".format(key, format(float(avg), ".2f"), count)
            break
  
      if open_pos == "":
        await ctx.send("You currently have no open positions at this moment.")  
      else:
        au_name = ctx.guild.get_member(ctx.message.author.id).name
        embed = discord.Embed(title="{}'s Plays".format(au_name), color=discord.Color.blurple())
        embed.add_field(name="Open Positions - (Stock, Average)", value=open_pos)
        await ctx.send(embed=embed)

    async def _history(self, ctx: commands.Context):
      au_name = ctx.guild.get_member(ctx.message.author.id).name
      embed = discord.Embed(title="{}'s History (Past 30 Days)".format(au_name), color=discord.Color.blurple())
      empty_history = True

      for key, value in self.firebase_db.list_stocks(ctx.message.author.id):
        hist = ""
        stock_entries = self.firebase_db.list_entries(key, ctx.message.author.id)

        if len(stock_entries) > 0:
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
                hist += "\n\n{} .......... ${} USD .......... ".format(entry["date"].split()[0], format(float(entry["price"]), ".2f"))
                e += 1
                continue
            else:
              if e == 1:
                pass
              else:
                hist += "${} USD; ".format(format(float(entry["price"]), ".2f"))
          
          if e != 1:
            empty_history = False
            embed.add_field(name="{} - (Closing Date, Closing Price, Entry Price(s))".format(key), value=hist, inline = False)
            embed.add_field(name='\u200b', value='\u200b')
        
      if not empty_history:
        embed.remove_field(len(embed.fields) - 1)
      await ctx.send(embed=embed)
