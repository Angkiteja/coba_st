import streamlit_authenticator
import connect_db as db

#code buat upload user ke db_mba mysql

usernames = ["admin1", "admin2"]
names = ["Admin 1", "Admin 2"]
passwords = ["admin123", "admin456"]
hashed_passwords = streamlit_authenticator.Hasher(passwords).generate()

for (username, name, hashed_password) in zip(usernames, names, hashed_passwords):
    db.insertUser(username, name, hashed_password)