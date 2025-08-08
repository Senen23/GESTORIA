import cx_Oracle
from config import DATABASE_CONFIG

def get_connection():
    dsn = cx_Oracle.makedsn(
        DATABASE_CONFIG['hostname'],
        DATABASE_CONFIG['port'],
        sid=DATABASE_CONFIG['sid']
    )
    return cx_Oracle.connect(
        DATABASE_CONFIG['username'],
        DATABASE_CONFIG['password'],
        dsn
    )