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
    
    def get_bday_ref(self):
      return self.fdb.reference("/Birthdays")
