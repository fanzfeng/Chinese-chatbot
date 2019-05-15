# -*- coding: utf-8 -*-
"""
Created on Tue May  9 11:48:52 2017

@author: FanZhengfeng

for: all in use
"""
import os
import hashlib
from pyhive import hive
from impala.dbapi import connect
from impala.util import as_pandas
import pandas as pd
import platform

if platform.system() == 'Darwin':
    default_save_path = "/Users/fanzfeng/Documents/za/hive_data/"
elif platform.system() == 'Linux':
    default_save_path = "/data/home/fanzhengfeng/hive_data"
else:
    default_save_path = './data_sql/'

sys_keywords = ["create table", "drop table", "alter table", "insert overwrite table", "set mem_limit"]


def hiveSql(sql, output_df=True, need_print=True, save_file=False):
    if need_print:
        print(sql)
    if save_file:
        md5obj = hashlib.md5()
        md5obj.update(sql.encode())
        sql_hash = md5obj.hexdigest()
        if not os.path.exists(default_save_path):
            os.mkdir(default_save_path)
        file_name = '{}HIVE_{}.xlsx'.format(default_save_path, sql_hash)
        if os.path.exists(file_name):
            print("Your data already exists: ", file_name)
            ad_s = pd.read_excel(file_name)
            return ad_s
        writer = pd.ExcelWriter(file_name)
    conn = hive.Connection(host='10.11.9.90', port=7001, username='root', password='zhenai@mre12435',
                           database='zhenai', auth="CUSTOM")
    cursor = conn.cursor()
    if sum(k in sql.lower() for k in sys_keywords) > 0:
        cursor.execute(sql)
        print("Success {}".format(sql.split()[0:2]))
        return None
    cursor.execute(sql)
    if not output_df:
        rlist = cursor.fetchall()
        if need_print:
            print('Hive return value cnt: ', len(rlist), '   ', rlist)
        return rlist
    else:
        hive_df = as_pandas(cursor)
        ad_s = hive_df.rename(columns={c: c.split('.')[-1] for c in hive_df.columns})
        if save_file:
            ad_s.to_excel(writer, "sheet1", index=False)
            print("Write sqldata: ", file_name)
    cursor.close()
    conn.close()
    if 'ad_s' in locals().keys():
        if need_print:
            print('Data shape:', ad_s.shape[0])
        return ad_s


def impalaSql(sql, output_df=True, mem=None, save_file=False, sep_str=',', sql_method='impala_windows',
              user='datascience', need_print=True):
    if need_print:
        print(sql)
    md5obj = hashlib.md5()
    md5obj.update(sql.encode())
    sql_hash = md5obj.hexdigest()
    if save_file and not os.path.exists(default_save_path):
        os.mkdir(default_save_path)
    file_name = '{}df_{}.csv'.format(default_save_path, sql_hash)
    #print('sql str hash: ', sql_hash, '\n', 'file name: ', file_name, '\n', 'file exit', os.path.exists(file_name))
    if save_file and os.path.exists(file_name):
        ad_s = pd.read_csv(file_name, sep=sep_str, encoding='utf-8')
        if need_print:
            print("Your data already exists: ", file_name)
    else:
        sql_method = 'impala_linux' if 'windows' not in platform.architecture()[1].lower() else 'impala_windows'
        if sql_method == "impala_linux":
            akey = "~/{}.keytab".format(user)
            os.system("kinit -kt {} {}".format(akey, user))
            connection = connect(host='gs-server-1001', port=int(21050), auth_mechanism='GSSAPI', kerberos_service_name='impala')
        else:
            import pyodbc
            connection_string = '''DSN=Sample Cloudera Impala DSN''' if user == 'datascience' else '''DSN=udmp_Sample Cloudera Impala DSN'''
            connection = pyodbc.connect(connection_string, autocommit=True)
        cursor = connection.cursor()
        if sum(k in sql.lower() for k in sys_keywords) > 0:
            cursor.execute(sql)
            print("Success {}".format(sql.split()[0:2]))
            return None
        if mem is not None:
            cursor.execute('''set mem_limit={};'''.format(mem))
        cursor.execute(sql)
        if not output_df:
            rlist = cursor.fetchall()
            if need_print:
                print('Impala return value cnt: ', len(rlist), '   ', rlist)
            return rlist
        else:
            ad_s = as_pandas(cursor)
            if ad_s.shape[0] == 1000000 and need_print:
                print("Warning, your data may be cut obs=1000000!!!")
            if save_file:
                ad_s.to_csv(file_name, index=False, sep=sep_str, encoding='utf-8')
                print("Write sqldata: ", file_name)
        cursor.close()
        connection.close()
    if 'ad_s' in locals().keys():
        if need_print:
            print('Data shape:', ad_s.shape[0])
        return ad_s


if __name__ == "__main__":
    sql = '''
    select type, servicecode, "20181207_20181212" day_stat,
        call_cnt call_cnt1,
        round(call_cnt/all_cnt, 4) connect_rate,
        round(pass_cnt/all_cnt, 4) pass_rate,
        round(A_over/call_cnt, 4) a_kill_rate,
        round(F_sum/call_cnt, 4) goto_f_rate,
        round(F_over/F_sum, 4) f_kill_rate,
        round(A_yes/call_cnt, 4) af_yes_rate,
        round(A_no/call_cnt, 4) af_no_rate,
        round(A_refuse/call_cnt, 4) af_refuse_rate,
        round(A_stay/call_cnt, 4) af_stay_rate,
        round(B_sum/call_cnt, 4) got_b_rate,
        round(B_over/B_sum, 4) b_kill_rate,
        round(B_yes/B_sum, 4) b_yes_rate,
        round(B_no/B_sum, 4) b_no_rate,
        round((B_sum-B_over-B_yes-B_no-B_stay)/B_sum, 4) b_other_rate,
        round(F_yes/call_cnt, 4) goto_j_rate,
        round(F_no/F_yes, 4) j_over_rate,
        round(F_refuse/F_yes, 4) j_yes_rate,
        round(F_stay/F_yes, 4) j_no_rate,
        round(1-(F_no+F_refuse+F_stay)/F_yes, 4) j_other_rate
    from std.f_offline_telephone_saywhat_stat_py
    where call_cnt > 100 and type="out"
    '''
    df = hiveSql(sql)
    print(df)
