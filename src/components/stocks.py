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
        elif cmd.lower() == "avg":
          if len(args) != 2:
            await ctx.send("Invalid number of arguments specified for 'AVG'. For more information, please specify '++stocks help'")
          else:
            await self.avg(ctx, args[1])

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

    async def avg(self, ctx: commands.Context, stock):
      if stock.upper() in self.firebase_db.get_symbols():
        avg, count = self.firebase_db.avg(stock)
        await ctx.send("The average for the stock {} is ${} CAD (based on {} entries)".format(stock.upper(), avg, count)) 
      else:
        await ctx.send("The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock))  

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
    
      