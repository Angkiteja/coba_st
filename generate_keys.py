import pickle 
from pathlib import Path

import streamlit_authenticator

names = ["Admin 1", "Admin 2"]
usernames = ["admin1", "admin2"]
passwords = ["xxx", "xxx"]


#bycript
hashed_passwords = streamlit_authenticator.Hasher(passwords).generate()

#store password to pickle file
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)