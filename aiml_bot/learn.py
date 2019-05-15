#!/usr/bin/env python

import sys
sys.path.insert(0, "../")

from aiml.constants import *
from aiml.LangSupport import mergeChineseSpace

from utils_fanzfeng.mongo_service import MongoSevice

template = """<?xml version="1.0" encoding="UTF-8"?>
<aiml version="1.0">

<meta name="author" content="autogen"/>
<meta name="language" content="zh"/>
{rules}
</aiml>
"""

category_template = """
<category>
<pattern>{pattern}</pattern>
<template>{answer}</template>
</category>
"""
mongo = MongoSevice(my_db="chatbot_my", my_set="aiml_rules", id_col="rid")
# mongo.insert_request(doc={"rid": hash("明天去公园吗"),
#                           "q": "明天去公园吗",
#                           "a": "当然好啦"})


def refresh_rules():
    all_rules = mongo.find_requests_by_status("all_")
    if len(all_rules) > 0:
        rules = []
        for r in all_rules:
            rules.append(category_template.format(pattern=r["q"],
                                                  answer=r["a"]))
        content = template.format(rules='\n'.join(rules))
        with open("auto-gen.aiml", 'w') as fp:
            fp.write(content)


if len(sys.argv) == 3:
    _, rule, temp = sys.argv
    rule = mergeChineseSpace(rule)
    temp = mergeChineseSpace(temp)
    mongo.insert_request({"q": rule, "a": temp, "rid": hash(rule)})
    refresh_rules()
elif len(sys.argv) == 2:
    if sys.argv[1] == "refresh":
        refresh_rules()
        print("refresh learned rules down!")
