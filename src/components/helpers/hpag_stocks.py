import discord
from discord.ext import commands

from datetime import datetime
from pytz import timezone


async def open(ctx: commands.Context, firebase_db):
  open_pos = ""

  for key, value in firebase_db.list_stocks(ctx.message.author.id):
    stock_entries = firebase_db.list_entries(key, ctx.message.author.id)

    if len(stock_entries) > 0:
      for i in reversed(stock_entries):
        entry = i[1]

        if entry["type"] == "BTO" or entry["type"] == "PSTC":
          avg, count = firebase_db.avg(key, ctx.message.author.id)
          partials = firebase_db.count_partial(key, ctx.message.author.id)
          pstring = "".join("${} USD; ".format(i) for i in partials)
          open_pos += "\n{} ..........  ${} USD (over {} entries)".format(key, format(float(avg), ".{}f".format(len(str(avg).split(".")[1]))), count)

          if pstring != "":
            open_pos += " .......... {}".format(pstring)
        break
  
  if open_pos == "":
    await ctx.send("You currently have no open positions at this moment.")  
  else:
    au_name = ctx.guild.get_member(ctx.message.author.id).name
    embed = discord.Embed(title="{}'s Plays".format(au_name), color=discord.Color.blurple())
    embed.add_field(name="Open Positions - (Stock, Average, Partial Exit(s) (if any))", value=open_pos)
    await ctx.send(embed=embed)

async def history(ctx: commands.Context, firebase_db):
  au_name = ctx.guild.get_member(ctx.message.author.id).name
  embed = discord.Embed(title="{}'s History (Past 30 Days)".format(au_name), color=discord.Color.blurple())
  empty_history = True

  for key, value in firebase_db.list_stocks(ctx.message.author.id):
    hist = ""
    stock_entries = firebase_db.list_entries(key, ctx.message.author.id)

    if len(stock_entries) > 0:

      # e will help us in ensuring that we don't consider open 
      # transactions
      e = 1
      prev_type = None
      pstcs = ""

      # Go through all the entries. Only consider the entries
      # if they've been closed and are also within the date range
      for i in reversed(stock_entries):
        entry = i[1]
            
        if entry["type"] == "STC":
          fmt = '%Y-%m-%d'
          cdt = datetime.strptime(datetime.now(timezone("US/Eastern")).strftime(fmt), fmt)
          dt = datetime.strptime(entry["date"].split()[0], fmt)
              
          if (cdt - dt).days <= 30:
            hist += "\n\n{} .......... ${} USD .......... ".format(entry["date"].split()[0], format(float(entry["price"]), ".{}f".format(len(entry["price"].split(".")[1]))))
            e += 1
            continue
        else:
          if e == 1:
            pass
          else:

            # Go through the partial exits/entries
            # It's a given that we'll be going through the PSTCs first,
            # but we don't want to concat the result with the
            # string just yet until we go through the entries first
            money = "${} USD; ".format(format(float(entry["price"]), ".{}f".format(len(entry["price"].split(".")[1]))))

            if entry["type"] == "PSTC":
              pstcs += money
            elif entry["type"] == "BTO":
              if prev_type == "PSTC":
                hist += "{} .......... ".format(pstcs)
                pstcs = ""
              hist += money
            
        prev_type = entry["type"]
          
      if e != 1:
        empty_history = False
        embed.add_field(name="{} - (Closing Date, Closing Price, Entry Price(s), Partial Exit(s) (if any))".format(key), value=hist, inline = False)
        embed.add_field(name='\u200b', value='\u200b')
        
  if not empty_history:
    embed.remove_field(len(embed.fields) - 1)
  await ctx.send(embed=embed)