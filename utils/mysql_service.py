# -*- coding: utf-8 -*-
# @Author  : fanzfeng

import pymysql


class MysqlSevice(object):
    def __init__(self, table_name, server_ip="localhost", user="root", passwd="root", db_name="mysql",
                 cols_name=["question", "answer"], col_types=["%s", "%s"]):
        self.ip = server_ip
        self.db = db_name

        self.coll = table_name
        self.cols = cols_name
        self.dtypes = col_types
        assert len(cols_name) == len(self.dtypes)
        self.nlen = len(cols_name)
        self.client = pymysql.connect(host=self.ip, user=user, passwd=passwd, db=self.db, autocommit=True,
                                      use_unicode=True, charset="utf8")
        self.exe = self.client.cursor()
        self.create_table()

    def create_table(self):
        if isinstance(self.scan(0), list):
            pass
        else:
            format_cols = ["{} {}".format(self.cols[j], "int" if self.dtypes[j] == "%d" else "varchar(100)")
                           for j in range(self.nlen)]
            new_sql = "create table {}({})".format(self.coll, ", ".join(format_cols))
            self.exe.execute(new_sql)

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


if __name__ == "__main__":
    mysql = MysqlSevice(table_name="just_test")
