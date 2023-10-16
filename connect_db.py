import pandas as pd
import mysql.connector as mc
from sqlalchemy import create_engine


dfcsv = pd.read_parquet("data_clean.parque", columns=None)

username = "root"
password = "123"
database = "db_mba"
host = "localhost"
connection_string = f"mysql+pymysql://{username}:{password}@{host}/{database}"
engine = create_engine(connection_string)

dfcsv.to_sql('datacustomer_parque', engine, if_exists='replace', schema='db_mba')
print("Connected")

def insertUser(username_value, name_value, password_value):
    mysqldb_conn = mc.connect(host="localhost", user="root", password="123", database="db_mba")
    sql = "INSERT INTO users (username, name, password) VALUES (%s, %s, %s)"
    values = (username_value, name_value, password_value)
    cursor = mysqldb_conn.cursor()
    cursor.execute(sql, values)
    mysqldb_conn.commit()
    cursor.close()
    mysqldb_conn.close()
    print(cursor.rowcount, "record inserted.")

# names = ["Angki Teja", "Rudihybst"]
# usernames = ["kitej", "rdhbst"]
# passwords = ["123", "456"]

# hashed_passwords = stauth.Hasher(passwords).generate()

# for(username, name, hashed_password) in zip(usernames, names, hashed_passwords):
#     db.insertUser(username, name, hashed_password)