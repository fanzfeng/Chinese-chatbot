# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging


class MongoSevice(object):
    def __init__(self, server_id="39.108.171.231", my_db="weibo_kol", my_set="kol_find_job", id_col='application_id'):
        self.ip = server_id
        self.client = MongoClient(host=self.ip, port=27017)
        self.set_name = my_set
        self.id_col = id_col
        self.db = self.client[my_db]
        self.coll = self.db[my_set]
        # self.valid_cache_status = ['WAITING_CACHE', 'WAITING', 'SPARK_RUNNING', 'SPARK_FINISH', 'FINISH']
        self.job_status = ['waiting', 'running', 'failed', 'finished']
        # self.finished_cache_statsus = ['FINISH']

    def create_collection(self, set_sort=False, cols_config=["status"]):
        if self.set_name not in self.db.collection_names():
            self.coll.create_index([(self.id_col, pymongo.ASCENDING)], unique=True)
            if set_sort:
                for ce in cols_config:
                    self.coll.create_index([(ce, pymongo.ASCENDING)])
            logging.info('create collection {}'.format(self.set_name))
        else:
            logging.info('collection {} already exists'.format(self.set_name))

    def insert_request(self, doc):
        try:
            # doc.update({'update_time': current_timestamp()})
            self.coll.insert_one(doc)
            return 'Success'
        except DuplicateKeyError as e:
            return 'DuplicateKeyError:' + str(e)
        except Exception as e:
            return str(e)

    def update_request(self, request_id, **args):
        dic = {}
        if 'set' in args:
            dic['$set'] = args['set']
        if 'inc' in args:
            dic['$inc'] = args['inc']
        if len(dic) > 0:
            # if '$set' in dic:
            #     dic['$set'].update({'update_time': current_timestamp()})
            # else:
            #     dic['$set'] = {'update_time': current_timestamp()}
            self.coll.update_one({self.id_col: request_id}, dic)

    # def clear_cache(self, cond):
    #     self.coll.update_many(cond, {'$set': {'cache_id': ''}})

    def find_request(self, request_id):
        # return dict
        return self.coll.find_one({self.id_col: request_id})

    def find_requests_by_status(self, status):
        if status == "all_":
            jobs = list(self.coll.find().sort([(self.id_col, pymongo.ASCENDING)]))
        elif isinstance(status, (set, list, tuple)):
            jobs = list(self.coll.find({'status': {"$in": status}}).sort([(self.id_col, pymongo.ASCENDING)]))
        else:
            jobs = list(self.coll.find({'status': status}).sort([(self.id_col, pymongo.ASCENDING)]))
        return jobs

    def clear_requests(self, request_ids):
        if request_ids == "all_":
            self.coll.delete_many({})
        elif isinstance(request_ids, (set, list, tuple)):
            self.coll.delete_many({self.id_col: {"$in": request_ids}})
        else:
            self.coll.delete_many({self.id_col: request_ids})
        return 'Success'

    def clear_requests_by_status(self, status):
        if status == "all":
            self.coll.delete_many({})
        elif isinstance(status, (set, list, tuple)):
            self.coll.delete_many({"status": {"$in": list(status)}})
        else:
            self.coll.delete_many({"status": status})
        return 'Success'

    # def has_valid_cache(self, cache_id):
    #     return cache_id != '' and \
    #         self.coll.find_one({'cache_id': cache_id, 'status': {'$in': self.valid_cache_status}}) is not None
    #
    # def has_queued_cache(self, cache_id):
    #     return cache_id != '' and \
    #         self.coll.find_one({'cache_id': cache_id, 'status': {'$in': self.queued_cache_status}}) is not None
    #
    # def get_finished_cache_request(self, cache_id):
    #     if cache_id != '':
    #         r = list(self.coll.find({'cache_id': cache_id, 'status': {'$in': self.finished_cache_status}}).
    #                  sort([('update_time', pymongo.DESCENDING)]))
    #         if r:
    #             return r[0]
    #         else:
    #             return None
    #     else:
    #         return None
    #
    # def get_admin_info(self):
    #     status_stat = list(self.coll.aggregate([{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]))
    #     waiting_job = self.find_requests_by_status('WAITING')
    #     waiting_cache_job = self.find_requests_by_status('WAITING_CACHE')
    #     spark_running_job = self.find_requests_by_status('SPARK_RUNNING')
    #     return status_stat, waiting_job, waiting_cache_job, spark_running_job

if __name__ == "__main__":
    import pprint
    # mong = MongoSevice(my_set="kol_bank", id_col="kol_id")
    # mong = MongoSevice()
    # print(mong.find_requests_by_status("running"))
    # mong.clear_requests_by_status("running")
    # mong.update_request('81d4dfcf43953bf01db2d7eaf3047e8b', set={"status": "--"})
    # mong.find_request('81d4dfcf43953bf01db2d7eaf3047e8b')
    # mong.insert_request({"application_id": "up", "status": "-"})
    # pprint.pprint(, indent=4)
    # mong.clear_requests(["5982432257"])
    # mong.create_collection()
    # mong.update_request(request_id="hahah", set={"status": "kk", "msg": "just a test"})
    # print(list(mong.find_requests_by_status("all_")))
    # print(len(mong.find_requests_by_status("waiting")), "个kol")
    # print(mong.find_request("5834040068"))
    # for i in list(mong.coll.find()):
    #     del i['_id']
    #     if len(i['profile']) <= 3:
    #         mong.clear_requests([i['kol_id']])
    # pprint.pprint(mong.find_requests_by_status(["finished"]), indent=4)
    # mong.clear_requests_by_status(["running", "waiting"])
    # mongo = MongoSevice(my_db="chatbot_my", my_set="aiml_rules", id_col="rid")
    mongo = MongoSevice(my_db="chatbot", my_set="weather", id_col="uid")

    # mongo.create_collection()
    # mongo.insert_request(doc={"rid": hash("明天去公园吗"),
    #                           "q": "明天去公园吗",
    #                           "a": "当然好啦"})
    pprint.pprint(mongo.find_requests_by_status("all_"), indent=4)
    print("ok")