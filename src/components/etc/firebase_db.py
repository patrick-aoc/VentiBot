import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

import os

class FirebaseDB():

    def __init__(self, project_id, firebase_url):
      # Use the application default credentials
      cred_obj = firebase_admin.credentials.Certificate(os.getenv("FIREBASE_CRED"))
      firebase_admin.initialize_app(cred_obj, {
          'projectId': project_id,
          'databaseURL': firebase_url
      })
      self.fdb = db
    
    def add_bd(self, celebrant, birthday):
      exists = False
      added = False

      for key, value in self.list_birthdays():
        cb_id = value["celebrant_id"]

        if cb_id == str(celebrant.id):
          exists = True
          break

      if not exists:
        self._get_bday_ref().push(
            {
              "celebrant_id": str(celebrant.id),
              "celebrant_name": str(celebrant).split("#")[0],
              "birthday": birthday
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

    def list_birthdays(self):
      return (self._get_bday_ref().get()).items() if self._get_bday_ref().get() else dict()

    def _get_bday_ref(self):
      return self.fdb.reference("/Birthdays")
