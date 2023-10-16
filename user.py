import mysql.connector
from configparser import ConfigParser
CNX: mysql.connector.connect = None

def login(userName: str, password: str) -> bool:
    args = [userName, password, 0]
    result_args = execute_sql_query("CheckUser", args)
    if (result_args[2] == 1):
        return True
    else:
        return False; 

def execute_sql_query(query, args):
    global CNX
    if (CNX == None):
        config = ConfigParser()
        config. read("config.ini")
        _host = config.get('MySQL', 'host')
        _port = config.get('MySQL', 'port')
        _database = config.get('MySQL', 'database')
        _user = config.get('MySQL', 'user')
        _password = config.get('MySQL', 'password')
        CNX = mysql.connector.connect(host=_host, database=_database,
                                      user=_user, passwd=_password, port=_port)

    with CNX.cursor() as cur:
        return cur.callproc(query, args)



