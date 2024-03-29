import discord
from discord.ext import commands

import DiscordUtils

from datetime import datetime
from pytz import timezone


async def open(ctx: commands.Context, firebase_db):
  open_pos = ""
  pages = []
  for key, value in firebase_db.list_stocks(ctx.message.author.id):
    stock_entries = firebase_db.list_entries(key, ctx.message.author.id)

    if len(stock_entries) > 0:
      for i in reversed(stock_entries):
        entry = i[1]

        if entry["type"] == "BTO" or entry["type"] == "PSTC" or entry["type"] == "STO":
          avg, count, te = firebase_db.avg(key, ctx.message.author.id)
          t = "Long" if entry["type"] == "BTO" or entry["type"] == "PSTC" else "Short"
          partials = firebase_db.count_partial(key, ctx.message.author.id)
          pstring = "".join("${} USD; ".format(i) for i in partials)
          open_pos += "\n{} ..........  ${} USD (over {} entries)".format(key, format(float(avg), ".{}f".format(len(str(avg).split(".")[1]))), t, count)

          if pstring != "":
            open_pos += " .......... {}".format(pstring)
          if len(open_pos) > 500:
            pages.append(open_pos)
            open_pos = ""
        break
  
  if len(pages) == 0 and open_pos == "":
    await ctx.send("You currently have no open positions at this moment.")  
  
  else:
    au_name = ctx.guild.get_member(ctx.message.author.id).name

    if (len(pages) == 0 and open_pos != "") or (len(pages) == 1 and open_pos == ""):
      embed = create_embed("{}'s Plays".format(au_name), "Open Positions - (Stock, Average, Position Type, Partial Exit(s) (if any))", open_pos)
      await ctx.send(embed=embed)
    else:
      embeds = []
      i = 1
      pg_count = len(pages) + 1 if open_pos != "" else len(pages)

      for pg in pages:
        embed = create_embed("{}'s Plays".format(au_name), "Open Positions - (Stock, Average, Partial Exit(s) (if any))", pg, "Page {} of {}".format(i, pg_count))
        embeds.append(embed)
        i += 1
      
      if open_pos != "":
        embed = create_embed("{}'s Plays".format(au_name), "Open Positions - (Stock, Average, Partial Exit(s) (if any))", open_pos, "Page {} of {}".format(pg_count, pg_count))
        embeds.append(embed)

      await create_pagination(ctx, embeds)

async def history(ctx: commands.Context, firebase_db):
  au_name = ctx.guild.get_member(ctx.message.author.id).name
  em_tit = "{}'s History (Past 30 Days)".format(au_name)
  embeds = []
  curr_embed = create_embed(em_tit)
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
        if entry["type"] == "STC" or entry["type"] == "BTC":
          fmt = '%Y-%m-%d'
          cdt = datetime.strptime(datetime.now(timezone("US/Eastern")).strftime(fmt), fmt)
          dt = datetime.strptime(entry["date"].split()[0], fmt)
          if (cdt - dt).days <= 30:
            t = "Long" if entry["type"] == "STC" else "Short"
            hist += "\n\n{} ({}) .......... ${} USD .......... ".format(entry["date"].split()[0], t, format(float(entry["price"]), ".{}f".format(len(entry["price"].split(".")[1]))))
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
            elif entry["type"] == "BTO" or entry["type"] == "STO":
              if prev_type == "PSTC":
                hist += "{} .......... ".format(pstcs)
                pstcs = ""
              hist += money
            
        prev_type = entry["type"]
          
      if e != 1:
        empty_history = False
        create_field(curr_embed, "{} - (Closing Date, Closing Price, Entry Price(s), Partial Exit(s) (if any))".format(key), hist)
        if len(curr_embed.fields) == 8:
          curr_embed.remove_field(7)
          embeds.append(curr_embed)
          curr_embed = create_embed(em_tit)
        
  # Pagination at the footer is dealt with at the end since
  # We don't exactly now how many entries we have as we're
  # iterating through them all
  if not empty_history:
    if len(embeds) == 0 and len(curr_embed.fields) > 0:
      curr_embed.remove_field(len(curr_embed.fields) - 1)
      await ctx.send(embed=curr_embed)
    else:
      if len(embeds) == 1:
        if len(curr_embed.fields) > 0:
          embeds[0].set_footer(text="Page 1 of 2")
          curr_embed.set_footer(text="Page 2 of 2")
          curr_embed.remove_field(len(curr_embed.fields) - 1)
          embeds.append(curr_embed)
          await create_pagination(ctx, embeds)
        else:
          await ctx.send(embed=embeds[0])
      else:
        if len(curr_embed.fields) > 0:
          curr_embed.remove_field(len(curr_embed.fields) - 1)
          embeds.append(curr_embed)
        i = 1
        for e in embeds:
          e.set_footer(text="Page {} of {}".format(i, len(embeds)))
          i += 1
        await create_pagination(ctx, embeds)
  else:
    await ctx.send("You have not closed on any transaction with any stock in the past 30 days")
  
async def notes(ctx: commands.Context, firebase_db, stock):
  notes = ""
  pages = []

  for key, value in firebase_db.list_stocks(ctx.message.author.id):
    if key == stock.upper():
      stock_entries = firebase_db.list_entries(key, ctx.message.author.id)

      if len(stock_entries) > 0:
        for i in stock_entries:
          entry = i[1]

          try:
            nts = "No notes available for this transaction " if entry["notes"] == "" else entry["notes"]
          except KeyError:
            nts = "No notes available for this transaction "

          notes += "\n{} @ ${} USD - {}- {}".format(entry["type"], entry["price"], nts, entry["date"])

          if len(notes) > 500:
            pages.append(notes)
            notes = ""

  if len(pages) == 0 and notes == "":
    await ctx.send("You have not made any transactions with this stock.")  
  
  else:
    au_name = ctx.guild.get_member(ctx.message.author.id).name
    em_tit = "{}'s Transactions for the stock {}".format(au_name, stock)

    if len(pages) == 0 and notes != "":
      embed = create_embed(em_tit, "Transaction - Notes - Date", notes)
      await ctx.send(embed=embed)
    else:
      embeds = []
      i = 1
      pg_count = len(pages) + 1 if notes != "" else len(pages)

      for pg in pages:
        embed = create_embed(em_tit, "Transaction - Notes - Date", pg, "Page {} of {}".format(i, pg_count))
        embeds.append(embed)
        i += 1
      
      if notes != "":
        embed = create_embed(em_tit, "Transaction - Notes - Date", notes, "Page {} of {}".format(pg_count, pg_count))
        embeds.append(embed)

      await create_pagination(ctx, embeds)

def create_embed(title, name="", value="", footer_text=""):
  em = discord.Embed(title=title, color=discord.Color.blurple())

  if name != "" and value != "":
    em.add_field(name=name, value=value)

  if footer_text != "":
    em.set_footer(text=footer_text)
  return em

def create_field(embed, name, value, inline=False):
  embed.add_field(name=name, value=value, inline=inline)
  embed.add_field(name='\u200b', value='\u200b')

async def create_pagination(ctx: commands.Context, embeds):
  paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
  paginator.add_reaction('⏮️', "first")
  paginator.add_reaction('⏪', "back")
  paginator.add_reaction('⏩', "next")
  paginator.add_reaction('⏭️', "last")
  await paginator.run(embeds)