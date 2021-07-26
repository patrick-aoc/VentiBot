import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
import requests

from datetime import datetime
from pytz import timezone
import os

#r = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token=')

class FirebaseStocksDB():

    def __init__(self, project_id, firebase_url):
      # Use the application default credentials
      cred_obj = firebase_admin.credentials.Certificate(os.getenv("FIREBASE_CRED"))
      firebase_admin.initialize_app(cred_obj, {
          'projectId': project_id,
          'databaseURL': firebase_url
      }, "stocks")
      self.fdb = db
      self.symbol_list = self._get_symbols()
    
    def bto(self, stock, price):
      added = False

      try:
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        self._get_stock_ref(stock.upper()).push(
              {
                "stock_id": stock.upper(),
                "price": price,
                "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                "type": "BTO",
              }
        )
        added = True
      except:
        pass
      return added

    def stc(self, stock, price):
      added = False
      entries = self.list_entries(stock.upper())

      if len(entries) != 0:
        last_entry = list(entries)[-1][1]
        
        if last_entry["type"] != "STC":
          try:
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            self._get_stock_ref(stock.upper()).push(
                  {
                    "stock_id": stock.upper(),
                    "price": price,
                    "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
                    "type": "STC",
                  }
            )
            added = True
          except:
            pass
      return added
    
    def avg(self, stock):
      entries = self.list_entries(stock.upper())
      sm = 0
      count = 0

      if len(entries) != 0:
        for i in reversed(entries):
          entry = i[1]
          if entry["type"] == "BTO":
            sm += float(entry["price"])
            count += 1
            continue
          else:
            break
      
      return (sm / count, count) if count > 0 else (0, 0)


    def remove_bd(self, celebrant):
      exists = False
      removed = True
      node = None

      for key, value in self.list_birthdays():
        cb_id = value["celebrant_id"]

        if cb_id == str(celebrant.id):
          exists = True
          node = key
          break
      
      if exists and node:
        try:
          self._get_bday_ref().child(node).delete()
        except Exception:
          removed = False

      return removed

    def get_symbols(self):
      return self.symbol_list

    def list_stocks(self):
      return (self._get_stocks_ref().get()).items() if self._get_stocks_ref().get() else dict()
    
    def list_entries(self, stock):
      return (self._get_stock_ref(stock).get()).items() if self._get_stock_ref(stock).get() else dict()

    def _get_stocks_ref(self):
      return self.fdb.reference("/Stocks")

    def _get_stock_ref(self, stock):
      return self.fdb.reference("/Stocks/{}".format(stock))

    def _get_symbols(self):
      r_us = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(os.getenv("FINNHUB_API"))).json()
      r_sz = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=SZ&token={}'.format(os.getenv("FINNHUB_API"))).json()

      us_symbols = [i["symbol"] for i in r_us]
      sz_symbols = [e["symbol"] for e in r_sz]

      return us_symbols + sz_symbols
    # =============================

    
