# 一个基于微信公众号的中文文本对话机器人
1. 基于词典检索的人格模块
  - 分词+倒排索引
  - 相似问题文本检索（Q-Q检索）
2. 基于规则的笑话模块
3. 基于填槽的天气查询模块
   - 对话管理：槽位填充+if-else
   - 文本理解：jieba ner+规则
   - 天气查询：高德API
4. 闲聊模块
   - 图灵接口
5. 其他

# 快速上手
1. 依赖安装
  - mysql
  - mongo
  - 高德API
  - 图灵API
2. py包安装: pip3 install -r requirements.txt
3. 运行final_bot.py
4. 部署公众号后台
  - token获取
  - 服务端: wx_server.py，启动脚本
  
# 各类型的文本对话机器人
1. 基于标记语言
2. 基于NLP生成模型（应用：闲聊/创意文本生成）
3. 基于词典检索的问答机器人（应用：客服问答）
4. 基于填槽的任务式对话机器人（应用：业务办理）
5. 基于规则/有限状态机的对话机器人（应用：问卷调查、营销初筛）

# 相关
1. 文章介绍: https://zhuanlan.zhihu.com/p/100403598
2. 公众号成品：

![avatar](data/doc/xiaopang_7.jpg)


# 项目结构
```
├── aiml_bot 基于aiml标记语言的对话机器人
│   ├── aiml
│   ├── app.py
│   ├── auto-gen.aiml
│   ├── getweather.py
│   ├── learn.py
│   ├── startup.xml
│   ├── subbers.ini
│   └── test.aiml
├── char_bot 取名机器：给我一个姓氏，还你一堆姓名
│   ├── __init__.py
│   ├── char_gen.py
│   └── model.py
├── data 数据依赖
│   ├── 3w_bot.csv  人格问答知识库
│   ├── joke        笑话知识库
│   ├── explan      fsm的状态表
│   ├── transfer    fsm的跳转表
│   ├── save     取名机器人的模型文件
│   ├── stop_words.txt
├── frame_bot 天气助手
│   ├── __init__.py
│   └── frame_chatbot.py
├── fsm_bot  基于规则/fsm的对话机器人
│   ├── __init__.py
│   └── fsm_chatbot.py
├── s2s_bot   闲聊机器人
│   ├── __init__.py
│   ├── config.py
│   ├── min_bot.py
│   └── model.py
├── se_bot  基于词典检索的对话机器人
│   ├── __init__.py
│   └── qa_search.py
├── utils 
│   ├── __init__.py
│   ├── mongo_service.py
│   ├── mysql_service.py
│   ├── nlp_utils.py
│   ├── tf_utils.py
│   └── weather.py
├── weixin 微信公众号后台
│   ├── __init__.py
│   ├── receive.py
│   └── reply.py
├── bot_config.py    对话机器人配置
├── final_bot.py     模块融合
├── app.sh           微信公众号服务端启动sh脚本
└── wx_server.py     微信公众号服务端

```