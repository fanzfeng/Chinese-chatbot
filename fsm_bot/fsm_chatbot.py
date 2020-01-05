# -*- coding: utf-8 -*-
# @Date  : 09/08/2018
# @Author  : fanzfeng

import pandas as pd
import elasticsearch
import os, sys
botPath = "/".join(os.path.split(os.path.realpath(__file__))[0].split('/')[:-1])
print(botPath)
sys.path.append(botPath)

ip = ["10.1.8.105", "101.200.61.56", "39.108.171.231"][-1]
es = elasticsearch.Elasticsearch([ip], http_auth=('elastic', 'changeme'))
state = pd.read_csv(os.path.join(botPath, "data/explan"), sep="\t", encoding="utf-8", header=None)
transfer = pd.read_csv(os.path.join(botPath, "data/transfer"), sep="\t", encoding="utf-8", header=None)
transfer[1] = transfer[1].apply(lambda xs: xs.split('，'))
state_dict = state.set_index(0)[1].to_dict()
state_origin = "is_single"


class FSM(object):
    _globalSessionID = "_global"

    def __init__(self, sessionStore=None):
        self.final_response = "没听懂，"
        self.nota_response = "，接着上个问题，"
        self.text_len = 3
        if sessionStore is not None:
            self._sessions = sessionStore
        else:
            self._sessions = {}
        self._addSession(self._globalSessionID)

    def _addSession(self, sessionID):
        """Create a new session with the specified ID string."""
        if sessionID not in self._sessions:
            self._sessions[sessionID] = None

    def bot(self, user_input, sessionID=_globalSessionID):
        input_ = user_input.strip().replace(" ", "")
        self._addSession(sessionID)
        if self._sessions[sessionID] is None:
            self._sessions[sessionID] = state_origin
            return state_dict[state_origin]
        elif "end" == self._sessions[sessionID]:
            return state_dict[self._sessions[sessionID]]
        elif len(input_) <= 0:
            return state_dict[self._sessions[sessionID]]
        elif len(input_) <= self.text_len:
            for i in range(len(transfer)):
                if self._sessions[sessionID] == transfer.loc[i, 0]:
                    if "-" in transfer.loc[i, 1]:
                        return state_dict[transfer.loc[i, 2]]
                    elif sum(u in input_ for u in transfer.loc[i, 1]) > 0:
                        self._sessions[sessionID] = transfer.loc[i, 2]
                        return state_dict[transfer.loc[i, 2]]
            # print("remain:", self._sessions[sessionID])
            return self.final_response+state_dict[self._sessions[sessionID]]
        else:
            res = es.search(index="fanzfeng", doc_type="fsm_za", body={"query": {"match": {"question": input_}}})
            res_cnt = len(res["hits"]["hits"])
            if res_cnt > 0:
                return res["hits"]["hits"][0]["_source"]["answer"]+self.nota_response+state_dict[self._sessions[sessionID]]
            else:
                return self.final_response+state_dict[self._sessions[sessionID]]


if __name__ == "__main__":
    fsm = FSM()
    while True:
        user_input = input("> ").strip().replace(" ", "")
        if user_input in ("bye", "quit"):
            print("再见")
            break
        print(fsm.bot(user_input))
