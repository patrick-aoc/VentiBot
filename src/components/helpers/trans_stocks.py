import discord
from discord.ext import commands


async def bto(ctx: commands.Context, firebase_db, stock, price, notes=""):
  # Perform a lookup for the stock. If it's valid, add it
  # as an entry. O/w, reject
  if stock.upper() in firebase_db.get_symbols():
    try:
      px = _parse_price(price)
      if float(px) < 0:
        await ctx.send("Price cannot be negative")
      else:
        if firebase_db.bto(stock, px, ctx.message.author.id, notes):
          await ctx.send("Successfully bought to open (BTO) on the stock {} at the price ${} USD".format(stock, format(float(px), ".{}f".format(len(str(px).split(".")[1])))))
        else:
          await ctx.send("Failed to register the entry. It might be that your last transaction on this stock was a partial exit (PSTC) or you have shorted the stock.")
    except ValueError:
      await ctx.send("Invalid price specified")
  else:
    await ctx.send(_dne(stock))  

async def stc(ctx: commands.Context, firebase_db, stock, price, notes=""):
  if stock.upper() in firebase_db.get_symbols():
    try:
      px = _parse_price(price)
      if float(px) < 0:
        await ctx.send("Price cannot be negative")
      else:
        if firebase_db.stc(stock, px, ctx.message.author.id, notes):
          await ctx.send("Successfully sold to close (STC) on the stock {} at the price ${} USD".format(stock, format(float(px), ".{}f".format(len(str(px).split(".")[1])))))
        else:
          await ctx.send("Failed to register the entry. Either you have never BTO'd on the stock, your last transaction with the stock was a STC, or you have shorted the stock.")
    except ValueError:
      await ctx.send("Invalid price specified")
  else:
    await ctx.send(_dne(stock))  

async def pstc(ctx: commands.Context, firebase_db, stock, price, notes=""):
  if stock.upper() in firebase_db.get_symbols():
    px = _parse_price(price)
    if float(px) < 0:
      await ctx.send("Price cannot be negative")
    else:
      success, next_stc, ty = firebase_db.pstc(stock, ctx.message.author.id, px, notes)
      if success:

        if ty == "PSTC":
          msg = "Successfully made a partial exit on the stock {} at the price ${} USD ".format(stock, format(float(px), ".{}f".format(len(str(px).split(".")[1]))))
        else:
          msg = "Successfully sold to close (STC) on the stock {} at the price ${} USD".format(stock, format(float(px), ".{}f".format(len(str(px).split(".")[1]))))

        if next_stc:
          msg += "(NOTE - if you attempt to make a partial exit again, that transaction will be considered a STC instead)"

        await ctx.send(msg)
      else:
          await ctx.send("Failed to make the partial exit. Either you have never BTO'd on the stock, your last transaction with the stock was an STC, or you have shorted the stock.")
  else:
    await ctx.send(_dne(stock))  

async def btc(ctx: commands.Context, firebase_db, stock, price, notes=""):
  if stock.upper() in firebase_db.get_symbols():
    try:
      px = _parse_price(price)
      if float(px) < 0:
        await ctx.send("Price cannot be negative")
      else:
        if firebase_db.btc(stock, px, ctx.message.author.id, notes):
          await ctx.send("Successfully bought to close (BTC) on the stock {} at the price ${} USD".format(stock, format(float(px), ".{}f".format(len(str(px).split(".")[1])))))
        else:
          await ctx.send("Failed to register the entry. Either you have never STO'd on the stock, your last transaction with the stock was a BTC, or you are current long with the stock")
    except ValueError:
      await ctx.send("Invalid price specified")
  else:
    await ctx.send(_dne(stock))  

async def sto(ctx: commands.Context, firebase_db, stock, price, notes=""):
  # Perform a lookup for the stock. If it's valid, add it
  # as an entry. O/w, reject
  if stock.upper() in firebase_db.get_symbols():
    try:
      px = _parse_price(price)
      if float(px) < 0:
        await ctx.send("Price cannot be negative")
      else:
        if firebase_db.sto(stock, px, ctx.message.author.id, notes):
          await ctx.send("Successfully sold to open (STO) on the stock {} at the price ${} USD".format(stock, format(float(px), ".{}f".format(len(str(px).split(".")[1])))))
        else:
          await ctx.send("Failed to register the entry. It might be that you are currently long with the stock.")
    except ValueError:
      await ctx.send("Invalid price specified")
  else:
    await ctx.send(_dne(stock)) 
  
async def avg(ctx: commands.Context, firebase_db, stock):
  if stock.upper() in firebase_db.get_symbols():
    avg, count = firebase_db.avg(stock, ctx.message.author.id)
    await ctx.send("Your average for the stock {} is ${} USD (based on {} entries)".format(stock.upper(), format(float(avg), ".{}f".format(len(str(avg).split(".")[1]))), count)) 
  else:
    await ctx.send(_dne(stock))  

def _parse_price(price):
  rx = price.split(".")
  r = rx[1] if len(rx) == 2 else "{}.00".format(price)
  return str(round(float(price), len(r))) if len(rx) > 1 else r

def _dne(stock):
  return "The stock '{}' does not exist in the index of exchanges I have cached (US/SZ)".format(stock)