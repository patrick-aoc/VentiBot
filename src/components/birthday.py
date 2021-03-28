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
        self.firebase_db = firebase_db

    @commands.command(name='birthday', invoke_without_subcommand=True)
    async def _birthday(self, ctx: commands.Context, *args):
        
      if len(args) > 0:
        cmd = args[0]

        if cmd == "add":
          if len(args) < 2 or len(args) > 3:
            await ctx.send("Invalid number of arguments specified for 'add'. For more information, please specify 'Venti-san! birthday help'")
          else:
            if len(args) == 3:
              await self._add_bd(ctx, args[1], args[2])
            else:
              await self._add_bd(ctx, args[1])
        elif cmd == "remove":
          if len(args) > 2:
            await ctx.send("Invalid number of arguments specified for 'remove'. For more information, please specify 'Venti-san! birthday help'")
          else:
            if len(args) == 2:
              await self._remove_bd(ctx, args[1])
            else:
              await self._remove_bd(ctx)
        elif cmd == "list":
          await self._get_bds(ctx)
        elif cmd == "help":
          await self._help(ctx)

        else:
          await ctx.send("Invalid command '{c}' specified".format(c=cmd))    
    
    async def _help(self, ctx: commands.Context):
        await ctx.send("Not yet implemented")

    async def _add_bd(self, ctx: commands.Context, birthday, celebrant = None):
      if "/" in birthday or "-" in birthday:
        delim = "/" if "/" in birthday else "-"

        try:
          
          # Birthdays must be in the format:
          # MM-DD or MM/DD
          month = int(birthday.split(delim)[0])
          dte = int(birthday.split(delim)[1])

          if not self._is_valid_date(month, dte):
            raise Exception

          bdate = "{}/{}".format(month, dte)
          cb = None

          if celebrant:
            async for mem in ctx.guild.fetch_members(limit= None):
              uname = str(mem).split("#")[0]
              uid = str(mem).split("#")[1]
              did = str(mem.id)

              if (celebrant.split("#")[0] in uname and celebrant.split("#")[1] in uid) or str(did) in str(celebrant):
                author_id = str(ctx.message.author.id)

                # TODO --> extend it to allow people with a specific role to add birthdays
                if str(os.getenv("DISCORD_MY_ID")) == author_id or did == author_id:
                  cb = mem 
                  break
                else:
                  await ctx.send("You are only allowed to add your own birthday!")
                  return
          else:
            cb = await ctx.guild.fetch_member(ctx.message.author.id)

          if not cb:
            await ctx.send("There are no individuals in this server with the username '{}'. Did you make sure to specify the celebrant in the appropriate format? (e.g., Username#9999)'".format(celebrant))
          else:

            # If an entry for the birthday celebrant already exists, then we skip
            if not self.firebase_db.add_bd(cb, bdate):
              await ctx.send("An entry for {}'s birthday already exists".format(cb))
              return   
            await ctx.send("Birthday has been added for {} ... {} ({} {})".format(cb, bdate, self._get_month(month), dte))
        except KeyError:
          await ctx.send("Invalid birthday month was specified")
        except Exception as e:
          print(e)
          await ctx.send("Something went wrong with trying to parse your entry. Did you make sure to stick to the appropriate format? (See below)")
          await ctx.send("""```Venti-san! birthday add [date; format --> MM-DD or MM/DD] [celebrant; format --> DiscordUsername#1234] ```""")
      else:
        msg_1 = "Invalid arguments. Usage:"
        msg_2 = """```Venti-san! birthday add [date; format --> MM-DD or MM/DD] [celebrant; format --> DiscordUsername#1234] ```"""
        await ctx.send(msg_1)
        await ctx.send(msg_2)

    async def _remove_bd(self, ctx: commands.Context, celebrant = None):
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
    
      