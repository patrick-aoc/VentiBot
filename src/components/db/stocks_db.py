import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
import requests

from datetime import datetime
import json
from pytz import timezone
import os

#r = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token=')

class FirebaseStocksDB():

    def __init__(self, project_id, firebase_url):
      # Use the application default credentials
      cred_obj = firebase_admin.credentials.Certificate("./m.json")
      firebase_admin.initialize_app(cred_obj, {
          'projectId': project_id,
          'databaseURL': firebase_url
      }, "stocks")
      self.fdb = db
      self.symbol_list = self._get_symbols()
    
    def bto(self, stock, price, user_id, notes=""):
      added = False
      entries = self.list_entries(stock.upper(), user_id)

      if len(entries) != 0:
        last_entry = list(entries)[-1][1]
        
        # Can't BTO on a stock that has already been partially exited
        # or if one has shorted the stock
        if last_entry["type"] == "PSTC" or last_entry["type"] == "STO":
          return added
        
      try:
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        self._get_stock_ref(stock.upper(), user_id).push(
              {
                "stock_id": stock.upper(),
                "price": price,
                "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                "type": "BTO",
                "notes": notes
              }
        )
        added = True
      except:
        pass
      return added

    def stc(self, stock, price, user_id, notes=""):
      added = False
      entries = self.list_entries(stock.upper(), user_id)

      if len(entries) != 0:
        last_entry = list(entries)[-1][1]
        
        if last_entry["type"] == "BTO" or last_entry["type"] == "PSTC":
          try:
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            self._get_stock_ref(stock.upper(), user_id).push(
                  {
                    "stock_id": stock.upper(),
                    "price": price,
                    "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                    "type": "STC",
                    "notes": notes
                  }
            )
            added = True
          except:
            pass
      return added

    def sto(self, stock, price, user_id, notes=""):
      added = False
      entries = self.list_entries(stock.upper(), user_id)

      if len(entries) != 0:
        last_entry = list(entries)[-1][1]
        
        # Can't short a stock if it's currently long
        if last_entry["type"] == "PSTC" or last_entry["type"] == "BTO":
          return added

      try:
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        self._get_stock_ref(stock.upper(), user_id).push(
              {
                "stock_id": stock.upper(),
                "price": price,
                "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                "type": "STO",
                "notes": notes
              }
        )
        added = True
      except:
        pass
      return added
    
    def btc(self, stock, price, user_id, notes=""):
      added = False
      entries = self.list_entries(stock.upper(), user_id)

      if len(entries) != 0:
        last_entry = list(entries)[-1][1]
        
        if last_entry["type"] == "STO":
          try:
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            self._get_stock_ref(stock.upper(), user_id).push(
                  {
                    "stock_id": stock.upper(),
                    "price": price,
                    "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                    "type": "BTC",
                    "notes": notes
                  }
            )
            added = True
          except:
            pass
      return added

    def avg(self, stock, user_id):
      entries = self.list_entries(stock.upper(), user_id)
      sm = 0
      count = 0
      t = ""

      if len(entries) != 0:
        for i in reversed(entries):
          entry = i[1]
          if entry["type"] == "BTO" or entry["type"] == "STO":
            t = "Long" if entry["type"] == "BTO" else "Short"
            sm += float(entry["price"])
            count += 1
            continue
          else:

            # Partial exits do not mean transactions
            # have been fully closed
            if entry["type"] == "PSTC":
              continue
            else:
              break
      
      return (sm / count, count, t) if count > 0 else (0.00, 0, "")

    def count_partial(self, stock, user_id):
      entries = self.list_entries(stock.upper(), user_id)
      sm = []
      if len(entries) != 0:
        for i in reversed(entries):
          entry = i[1]
          if entry["type"] == "PSTC":
            sm.append(float(entry["price"]))
            continue
          else:
            break

      return sm

    def pstc(self, stock, user_id, price, notes=""):
      added = False
      next_stc = False
      ty = ""
      entries = self.list_entries(stock.upper(), user_id)   
      if len(entries) != 0:
        last_entry = list(entries)[-1][1]

        if last_entry["type"] != "BTC" or last_entry["type"] != "STO":
          # One cannot PSTC if their prev. transaction was an STC
          if last_entry["type"] != "STC":
            second_last_entry = None

            # If one's 2nd last entry was a PSTC, we need to make
            # sure that the individual is aware that a 3rd attempt to
            # PSTC will result in an STC
            try:
              second_last_entry = list(entries)[-2][1]
            except:
              pass

            try:
              fmt = '%Y-%m-%d %H:%M:%S %Z%z'
              t = "PSTC" if last_entry["type"] == "BTO" or second_last_entry["type"] != "PSTC" else "STC"
              self._get_stock_ref(stock.upper(), user_id).push(
                    {
                      "stock_id": stock.upper(),
                      "price": price,
                      "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                      "type": t,
                      "notes": notes
                    }
              )
              added = True
              ty = t
              next_stc = last_entry["type"] == "PSTC" and ty != "STC"
            except:
              pass
      return (added, next_stc, ty)

    def get_symbols(self):
      return self.symbol_list

    def list_stocks(self, user_id):
      return (self._get_stocks_ref(user_id).get()).items() if self._get_stocks_ref(user_id).get() else dict()
    
    def list_entries(self, stock, user_id):
      return (self._get_stock_ref(stock, user_id).get()).items() if self._get_stock_ref(stock, user_id).get() else dict()

    def _get_stocks_ref(self, user_id):
      return self.fdb.reference("/Stocks/{}".format(user_id))

    def _get_stock_ref(self, stock, user_id):
      return self.fdb.reference("/Stocks/{}/{}".format(user_id, stock))

    def _get_symbols(self):
      r_us = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(os.getenv("FINNHUB_API"))).json()
      r_sz = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=SZ&token={}'.format(os.getenv("FINNHUB_API"))).json()

      us_symbols = [i["symbol"] for i in r_us]
      sz_symbols = [e["symbol"] for e in r_sz]

      return us_symbols + sz_symbols
