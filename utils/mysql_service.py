# version='3.5.2'
# -*- coding: utf-8 -*-
# @Author  : fanzfeng

import pymysql


class MysqlSevice:
    def __init__(self, table_name):
        self.ip = "localhost"
        self.db = "za_chatbot"
        self.coll = table_name
        self.cols = ["question", "answer"]
        self.dtypes = ["%s", "%s"]
        self.client = pymysql.connect(host=self.ip, user='root', passwd='root', db=self.db, autocommit=True,
                                      use_unicode=True, charset="utf8")
        self.exe = self.client.cursor()

    # @staticmethod
    def insert(self, data_list):
        try:
            self.exe.executemany("insert into {} ({}) values ({})".format(self.coll, ",".join(self.cols),
                                                                          ",".join(self.dtypes)),
                                 data_list)
            return 'Success'
        except Exception as e:
            return str(e)

    def clear(self):
        try:
            self.exe.execute("truncate table {}".format(self.coll))
            return 'Success'
        except Exception as e:
            return str(e)

    def scan(self, n=5):
        try:
            if n <= 0:
                self.exe.execute("select * from {}".format(self.coll))
            self.exe.execute("select * from {} limit {}".format(self.coll, n))
            res = [r for r in self.exe]
            return res
        except Exception as e:
            return str(e)

    def count(self):
        try:
            self.exe.execute("select count(*) from {}".format(self.coll))
            return [r for r in self.exe][0][0]
        except Exception as e:
            return str(e)

    def sql_cnt(self, sql):
        try:
            self.exe.execute(sql)
            return [r for r in self.exe][0][0]
        except Exception as e:
            return str(e)
