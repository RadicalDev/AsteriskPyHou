import os
import sqlite3 as sql
from syslog import syslog as log, LOG_INFO


class Sqlite3Database(object):
    def __init__(self, path, session=''):
        self.session = session
        self.path = path
        self.db, self.cur = self.connect(path)

    def disconnect(self, session=''):
        session = self.session if self.session else session
        self.db.close()

    def execute(self, qstr):
        log(LOG_INFO, "database.Sqlite3Database.execute: EXECUTING: {0}".format(qstr))
        return self.cur.execute(qstr)

    def delete(self, table, where):
        qstr = "DELETE FROM {0} WHERE {1}".format(table, where)
        return self.execute(qstr)

    def update_d(self, table, d, where=""):
        set_str = ", ".join(["{0}='{1}'".format(x, y) for x, y in d.iteritems()])
        qstr = "UPDATE {0} SET {1}".format(table, set_str)
        if where: qstr += " WHERE {0}".format(where)
        try:
            self.execute(qstr)
            self.db.commit()
            return self.cur.lastrowid
        except Exception, e:
            log(LOG_INFO, "{0}: database.Sqlite3Database.update_d: Exception occurred when updating {1}: {2}".format(self.session, table, e))

    def update(self, table, key, value, where=""):
        qstr = "UPDATE {0} SET {1}='{2}'".format(table, key, value)
        if where: qstr += " WHERE {0}".format(where)
        try:
            self.execute(qstr)
            self.db.commit()
            return self.cur.lastrowid
        except Exception, e:
            log(LOG_INFO, "{0}: database.Sqlite3Database.update: Exception occurred when updating {1}: {2}".format(self.session, table, e))

    def insert(self, table, d):
        keys = ", ".join(d.keys())
        values = ", ".join(["'{0}'".format(x) for x in d.values()])
        qstr = "INSERT INTO {0}({1}) VALUES({2})".format(table, keys, values)
        self.execute(qstr)
        self.db.commit()
        return self.cur.lastrowid

    def dquery(self, table, keys="*", where="", fetchall=False, as_dict=True):
        return self.select(table, keys, where, fetchall, as_dict)

    def select(self, table, keys="*", where="", fetchall = False, as_dict = False):
        if keys == "*":
            keys = ", ".join([x[1] for x in self.execute("PRAGMA table_info({0})".format(table)).fetchall()])
        else:
            keys = ", ".join(keys)
        qstr = "SELECT {0} FROM {1}".format(keys, table)

        if where:
            qstr += " WHERE {0}".format(where)

        try:
            res = self.execute(qstr)
            if not as_dict:
                if fetchall:
                    return res.fetchall()
                return res.fetchone()
            else:
                keys = keys.split(", ")
                if fetchall:
                    d = []
                    for row in res.fetchall():
                        temp = {}
                        if not row:
                            continue
                        t = zip(keys, row)
                        [temp.__setitem__(x, y) for x, y in t]
                        d.append(temp)
                else:
                    d = {}
                    row = res.fetchone()
                    if not row:
                        return {}
                    row = zip(keys, row)
                    [d.__setitem__(x, y) for x, y in row]
                return d

        except Exception, e:
            log(LOG_INFO, "{0}: database.Sqlite3Database.select: Exception occurred when selecting {1} from {2}: {3}".format(self.session, keys, table, e))
        return []

    def connect(self, path):
        if not os.path.exists(path):
            log(LOG_INFO, "{0}: database.Sqlite3Database.connect: {1} doesn't exist. Creating it".format(self.session, path))
            db = sql.connect(path)
            cur = db.cursor()

            create = [
                (
                      "CREATE TABLE users("
                      "rowID INTEGER PRIMARY KEY AUTOINCREMENT, "
                      "username VARCHAR, "
                      "phonenumber VARCHAR UNIQUE, "
                      "winner VARCHAR DEFAULT 'False', "
                      "extension VARCHAR, "
                      "secret VARCHAR"
                      ")"
                ),

                (
                      "CREATE TABLE entry("
                      "rowID INTEGER PRIMARY KEY AUTOINCREMENT, "
                      "game INTEGER, "
                      "phonenumber VARCHAR, "
                      "result VARCHAR, "
                      "UNIQUE(game, phonenumber) ON CONFLICT ABORT"
                      ")"
                )
            ]

            try:
                for stmt in create:
                    log(LOG_INFO, "{0}: database.Sqlite3Database: Executing statement: {1}".format(self.session, stmt))
                    cur.execute(stmt)
                db.commit()
            except Exception, e:
                log(LOG_INFO, "{0}: database.Sqlite3Database: Failed to create tables: {1}".format(self.session, e))
        else:
            db = sql.connect(path)
            cur = db.cursor()
        return db, cur

