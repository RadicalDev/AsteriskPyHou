import sys
sys.path.append("../lib")

import random

from functions import sms
from database import Sqlite3Database

if __name__ == "__main__":
    number = "8322611494"

    db = Sqlite3Database("../etc/users.db")
    users = db.dquery("users", fetchall=True)

    for user in users:
        code = open("/etc/secret_code", 'r').read().strip()
        msg = "Hurry! Call {0} and enter {1} when prompted".format(number, code)
        print user['phonenumber'], ": ", msg
        sms(user['phonenumber'], msg)