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
          if len(args) != 3:
            await ctx.send("Invalid number of arguments specified for 'add'. For more information, please specify 'Venti-san! birthday help'")
          else:
            await self._add_bd(ctx, args[1], args[2])
        elif cmd == "list":
          await self._get_bds(ctx)
        elif cmd == "help":
          await self._help(ctx)
        else:
          await ctx.send("Invalid command '{c}' specified".format(c=cmd))    
    
    async def _help(self, ctx: commands.Context):
        await ctx.send("Not yet implemented")

    async def _add_bd(self, ctx: commands.Context, birthday, celebrant):
      if "/" in birthday or "-" in birthday:
        delim = "/" if "/" in birthday else "-"

        try:

          # Birthdays must be in the format:
          # MM-DD-YYYY or MM/DD/YYYY
          year = int(birthday.split(delim)[2])
          month = int(birthday.split(delim)[0])
          day = int(birthday.split(delim)[1])

          bdate = datetime.datetime(year, month, day).date()
          cb = None

          async for mem in ctx.guild.fetch_members(limit= None):
            uname = str(mem).split("#")[0]
            uid = str(mem).split("#")[1]
            did = mem.id
            
            if (celebrant.split("#")[0] in uname and celebrant.split("#")[1] in uid) or str(did) in celebrant:
              author_id = str(ctx.message.author.id)

              # TODO --> extend it to allow people with a specific role to add birthdays
              if str(os.getenv("DISCORD_MY_ID")) == author_id or did == author_id:
                cb = mem  

                # If an entry for the birthday celebrant already exists, then we skip
                if not self.firebase_db.add_bd(cb, birthday):
                  await ctx.send("An entry for {}'s birthday already exists".format(celebrant))
                  return

                                
                break
              else:
                await ctx.send("You are only allowed to add your own birthday!")
                return

          if not cb:
            await ctx.send("There are no individuals in this server with the username '{}'. Did you make sure to specify the celebrant in the appropriate format? (e.g., Username#9999)'".format(celebrant))
          else:
            await ctx.send("Birthday has been added for {} ... {}".format(celebrant, bdate))
        except Exception as e:
          print(e)
          await ctx.send("Something went wrong with trying to parse your entry. Did you make sure to stick to the appropriate format? (See below)")
          await ctx.send("""```Venti-san! birthday add [date; format --> MM-DD-YYYY or MM/DD/YYYY] [celebrant; format --> DiscordUsername#1234] ```""")
      else:
        msg_1 = "Invalid arguments. Usage:"
        msg_2 = """```Venti-san! birthday add [date; format --> MM-DD-YYYY or MM/DD/YYYY] [celebrant; format --> DiscordUsername#1234] ```"""
        await ctx.send(msg_1)
        await ctx.send(msg_2)

    async def _get_bd(self, ctx: commands.Context, celebrant):
      pass

    async def _get_bds(self, ctx: commands.Context):
        embed = (discord.Embed(title='Birthdays',
                               color=discord.Color.blurple()))
        birthdays = ""

        for key, value in self.firebase_db.list_birthdays():
            birthdays += "{} ... {} \n".format(value["celebrant_name"], value["birthday"])

        embed.add_field(name="Celebrant ... Birthday", value=birthdays)
        await ctx.send(embed=embed)
    
      