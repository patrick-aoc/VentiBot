import discord
from discord.ext import commands

from datetime import datetime
import os
from pytz import timezone

import src.components.helpers.trans_stocks as HLP
import src.components.helpers.info_stocks as HLPPag
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
      if "//" not in args:
        if len(args) != 2:
          await ctx.send("Invalid number of arguments specified for 'BTO'. For more information, please specify '++HELP'")
        else:
          await HLP.bto(ctx, self.firebase_db, args[0], args[1])  
      else:
        if args.index("//") == 2 and len(args) > 3:
          notes = "".join("{} ".format(i) for i in args[3:])
          await HLP.bto(ctx, self.firebase_db, args[0], args[1], notes)
        else:
          await ctx.send("Invalid usage of the command 'BTO'. For more information, please specify '++HELP'")

    @commands.command(name='STC', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def stc(self, ctx: commands.Context, *args):
      """
      STC - Sell to Close
      
      Close the entries for a stock at a given price for the user
      that called the command.
      """
      if "//" not in args:
        if len(args) != 2:
          await ctx.send("Invalid number of arguments specified for 'STC'. For more information, please specify '++HELP'")
        else:
          await HLP.stc(ctx, self.firebase_db, args[0], args[1])  
      else:
        if args.index("//") == 2 and len(args) > 3:
          notes = "".join("{} ".format(i) for i in args[3:])
          await HLP.stc(ctx, self.firebase_db, args[0], args[1], notes)
        else:
          await ctx.send("Invalid usage of the command 'STC'. For more information, please specify '++HELP'")
    
    @commands.command(name='PSTC', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def pstc(self, ctx: commands.Context, *args):
      """
      PSTC - Partial Exit

      Perform a partial exit for an open stock at a given price for
      the user that called the command.
      """
      if "//" not in args:
        if len(args) != 2:
          await ctx.send("Invalid number of arguments specified for 'PSTC'. For more information, please specify '++HELP'")
        else:
          await HLP.pstc(ctx, self.firebase_db, args[0], args[1])  
      else:
        if args.index("//") == 2 and len(args) > 3:
          notes = "".join("{} ".format(i) for i in args[3:])
          await HLP.pstc(ctx, self.firebase_db, args[0], args[1], notes)
        else:
          await ctx.send("Invalid usage of the command 'PSTC'. For more information, please specify '++HELP'")

    @commands.command(name='BTC', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def btc(self, ctx: commands.Context, *args):
      """
      BTC - Buy to Close

      Make an entry for a stock at a given price for the user that 
      called the command.
      """
      if "//" not in args:
        if len(args) != 2:
          await ctx.send("Invalid number of arguments specified for 'BTC'. For more information, please specify '++HELP'")
        else:
          await HLP.btc(ctx, self.firebase_db, args[0], args[1])  
      else:
        if args.index("//") == 2 and len(args) > 3:
          notes = "".join("{} ".format(i) for i in args[3:])
          await HLP.btc(ctx, self.firebase_db, args[0], args[1], notes)
        else:
          await ctx.send("Invalid usage of the command 'BTC'. For more information, please specify '++HELP'")

    @commands.command(name='STO', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def sto(self, ctx: commands.Context, *args):
      """
      STO - Sell to Open
      
      Close the entries for a stock at a given price for the user
      that called the command.
      """
      if "//" not in args:
        if len(args) != 2:
          await ctx.send("Invalid number of arguments specified for 'STO'. For more information, please specify '++HELP'")
        else:
          await HLP.sto(ctx, self.firebase_db, args[0], args[1])  
      else:
        if args.index("//") == 2 and len(args) > 3:
          notes = "".join("{} ".format(i) for i in args[3:])
          await HLP.sto(ctx, self.firebase_db, args[0], args[1], notes)
        else:
          await ctx.send("Invalid usage of the command 'STO'. For more information, please specify '++HELP'")

    @commands.command(name='TRANS', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def notes(self, ctx: commands.Context, *args):
      """
      TRANS - Transactions
      """
      if len(args) != 1:
        await ctx.send("Invalid number of arguments specified for 'NOTES'. For more information, please specify '++HELP'")
      else:
        await HLPPag.notes(ctx, self.firebase_db, args[0])

    @commands.command(name='AVG', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def avg(self, ctx: commands.Context, *args):
      """
      Returns the average value for a given stock based on the most recent
      set of (open) purchased entries that have not yet been closed.
      """
      if len(args) != 1:
        await ctx.send("Invalid number of arguments specified for 'AVG'. For more information, please specify '++HELP'")
      else:
        await HLP.avg(ctx, self.firebase_db, args[0])

    @commands.command(name='OPEN', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def open(self, ctx: commands.Context, *args):
      """
      Returns all the open positions (that haven't been closed)
      for the user calling the command.
      """
      async with ctx.typing():
        await HLPPag.open(ctx, self.firebase_db)
  
    @commands.command(name='HISTORY', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def history(self, ctx: commands.Context, *args):
      """
      Returns a history of every purchase that the user
      calling the command has closed.
      """
      async with ctx.typing():
        await HLPPag.history(ctx, self.firebase_db)

    @commands.command(name='HELP', invoke_without_subcommand=True)
    @commands.has_role(os.getenv("DISCORD_STOCK_WATCH"))
    async def help(self, ctx: commands.Context):
      user = await ctx.guild.fetch_member(ctx.message.author.id)
      await user.send(stocks_help)
      await ctx.send("Please check your DMs for reference to my comamands pertaining to Stocks")

    