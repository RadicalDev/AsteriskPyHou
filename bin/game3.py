import sys
sys.path.append("../lib")

from database import Sqlite3Database
from ami import AMI

if __name__ == "__main__":
    main_line = '2818097414'
    db = Sqlite3Database("../etc/users.db")
    users = db.dquery("users", fetchall=True)

    ami = AMI()
    for user in users:
        ami.create_call(user['phonenumber'], main_line,
                        main_line, 'game-three', user['phonenumber'])