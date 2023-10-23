import os

from deta import Deta
from dotenv import load_dotenv

#load environment variables
load_dotenv(".env")

DETA_KEY = os.getenv("DETA_KEY")

#initialize with a project key
deta = Deta(DETA_KEY)

#create/connect database
db = deta.Base("db_mba")


def insert_mba_history(antecedents, consequents, support, confidence, lift):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"support": support, "antecedents": antecedents, "consequents": consequents, "confidence": confidence, "lift": lift})


def fetch_all_history():
    """Returns a dict of all history"""
    res = db.fetch()
    return res.items


def get_history(key):
    """If not found, the function will return None"""
    return db.get(key)

def delete_history(key):
    return db.delete(key)