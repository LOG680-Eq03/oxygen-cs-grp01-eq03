import logging
import requests
import json
import time
import sys, os
import mariadb
from mariadb import Connection


class DbConnect:
    database = None
    comm: Connection = None
    module: mariadb = mariadb

    def __init__(self, connection):
        self.database = {}
        for vars in connection.split(","):
            vals = vars.split(":")
            self.database[vals[0].strip()] = vals[1].strip()
        self.initDb()

    def openConnection(self):
        self.comm = self.module.connect(
            user=self.database.get("username"),
            password=self.database.get("passwd"),
            host=self.database.get("host"),
            port=int(self.database.get("port")),
            database=self.database.get("database"),
        )

    def closeConnection(self):
        self.comm.close()

    def initDb(self):
        self.openConnection()
        # listOfTables = self.comm.execute( """SELECT name FROM sqlite_master WHERE type='table' AND name='sensors'; """).fetchall()
        # if(len(listOfTables) < 1):
        #         print("creating sensors table...")
        #         self.comm.execute("CREATE TABLE sensors (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, temperature DECIMAL);")
        #         self.comm.commit()
        #         print("table sucessfully created")
        # print(self.module.version)
        self.closeConnection()

    def insertDb(self, *args):
        self.openConnection()
        if len(args) == 2:
            sensor = (args[0], args[1])
            self.comm.execute(
                "INSERT INTO sensors (timestamp, temperature) VALUES (?, ?)", sensor
            )
            self.comm.commit()
        self.closeConnection()

    def __del__(self):
        self.closeConnection()
