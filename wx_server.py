# -*- coding: utf-8 -*-
# @Author  : fanzfeng

import sys, codecs
import web
import hashlib

import weixin.receive as receive
import weixin.reply as reply

from final_bot import one_bot, random, re
from bot_config import *
# import concurrent

try:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
except:
    pass

# executor = concurrent.futures.ThreadPoolExecutor(3)


class Handle(object):
    def GET(self):
        try:
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = weixin_token
            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            # print("handle/GET func: hashcode, signature: ", hashcode, signature)
            if hashcode == signature:
                return echostr
            else:
                return echostr
        except Exception as e:
            logging.error("Server Request GetError: {}".format(str(e)))
            return e

    def POST(self):
        try:
            webData = web.data()
            logging.debug("Handle Post webdata is: \n"+str(webData))
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg):
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                if recMsg.MsgType == "text":
                    text0 = str(recMsg.Content, encoding="utf-8")
                    logging.info("User {} say: {}".format(toUser, str(text0)))
                    if "收到不支持的消息类型，暂无法显示" in text0:
                        content = "".join(random.sample(emotions, 2))
                    elif re.match("\[[A-Za-z]*\]", text0) is not None or "/:" in text0:
                        content = "".join(random.sample(emotions, 2))
                    else:
                        try:
                            content = one_bot(text0, uid=toUser)
                        except Exception as e:
                            logging.error("Bot reply failed with log :{}".format(e))
                            content = "好可惜，没懂意思[捂脸]"
                    # content = yield executor.submit(chatbot.mix_bot, text=text0, user_name=toUser)
                elif recMsg.MsgType == 'image':
                    content = "好好打字，别发图[捂脸]"
                elif recMsg.MsgType == 'voice':
                    logging.info("Voice Msg id: {}".find(recMsg.MediaId))
                    content = "买不起耳机，语音|视频，某胖是不听的[奸笑]"
                else:
                    logging.warn("New Message Type!!!")
                    content = "好可惜，没懂意思[捂脸]"
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                logging.info("Bot {} say: \n{}".format(fromUser, content))
                return replyMsg.send()
            else:
                logging.error(str(webData))
                return "success"
        except Exception as e:
            logging.error("Server Request PostError: {}".format(str(e)))
            return "success"


urls = (
    '/wx', 'Handle',
)


if __name__ == '__main__':
    web.config.debug = False
    app = web.application(urls, globals())
    app.run()
