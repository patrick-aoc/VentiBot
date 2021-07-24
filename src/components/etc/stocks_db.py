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
      exists = False
      added = False

      # for key, value in self.list_stocks():
      #   sid = value["stock_id"]

      #   if sid == stock.upper():
      #     exists = True
      #     break

      if not exists:
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        self._get_stocks_ref().push(
            {
              "stock_id": stock.upper(),
              "price": price,
              "date": datetime.now(timezone("US/Eastern")).strftime(fmt),
              "type": "BTO",
            }
          )
        added = True

      return added
    
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

    def _get_stocks_ref(self):
      return self.fdb.reference("/Stocks")

    def _get_symbols(self):
      r_us = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(os.getenv("FINNHUB_API"))).json()
      r_sz = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=SZ&token={}'.format(os.getenv("FINNHUB_API"))).json()

      us_symbols = [i["symbol"] for i in r_us]
      sz_symbols = [e["symbol"] for e in r_sz]

      return us_symbols + sz_symbols
    # =============================

    
