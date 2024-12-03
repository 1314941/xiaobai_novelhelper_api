from web_api import chat_ollama_stream_post
from template import add_template,add_prompt


# 第1章 他叫白小纯 帽儿山，位于东林山脉中，山下有一个村子，民风淳朴，以耕田为生，与世隔绝。清晨，村庄的大门前，整个村子里的乡亲，正为一个十五六岁少年送别，这少年瘦弱，但却白白净净，看起来很是乖巧，衣着尽管是寻常的青衫，可却洗的泛白，穿在这少年的身上，与他目中的纯净搭配在一起，透出一股子灵动。他叫白小纯。“父老乡亲们，我要去修仙了，可我舍不得你们啊。”少年满脸不舍，原本就乖巧的样子，此刻看起来更为纯朴。四周的乡亲，面面相觑，顿时摆出难舍之色。“小纯，你爹娘走的早，你是个……好孩子！！难道你不想长生了么，成为仙人就可以长生，能活的很久很久，走吧，雏鹰长大，总有飞出去的那一天。”人群内走出一个头发花白的老者，说道好孩子三个字时，他顿了一下。“在外面遇到任何事情，都要坚持下去，走出村子，就不要回来，因为你的路在前方！”老人神色慈祥，拍了拍少年的肩膀。“长生……”白小纯身体一震，目中慢慢坚定起来，在老者以及四周乡亲鼓励的目光下，他重重的点了点头，深深的看了一眼四周的乡亲，转身迈着大步，渐渐走出了村子。眼看少年的身影远去，村中的众人，一个个都激动起来，目中的难舍刹那就被喜悦代替，那之前满脸慈祥的老者，此刻也在颤抖，眼中流下泪水。“苍天有眼，这白鼠狼，他终于……终于走了，是谁告诉他在附近看到仙人的，你为村子立下了大功！”“这白鼠狼终于肯离开了，可怜我家的几只鸡，就因为这白鼠狼怕鸡打鸣，不知用了什么方法，唆使一群孩子吃鸡肉，把全村的鸡都给吃的干干净净……”“今天过年了！”欢呼之声，立刻在这不大的村子里，沸腾而起，

#十日终焉  故事梗概：十个衣着各异的人在一个封闭房间中醒来，发现自己被神秘力量控制，参与一个游戏。游戏规则是参与者需要通过讲述故事来判断谁是说谎者，游戏过程中不断有人死去。齐夏凭借智慧和观察力，带领团队成员分析线索，共同面对挑战。经历了一系列的游戏后，团队被告知需要在十天内找到三千六百个“道”以拯救他们所在的世界。人龙出现并给予团队“道”的线索，同时暗示了更广阔的背景和即将到来的挑战。故事的结尾留下了悬念，参与者的未来和他们所在的世界的命运仍然未知。

import json
import time
import os



role={
      "id": 6,
      "description": "你是一个杰出的作家,能灵活地根据输入的小说内容,进行完美流畅的续写",
      "role": "测试",
      "options": {
        "num_keep": 5,
        "num_predict": 500,
        "top_k": 20,
        "top_p": 0.9,
        "repeat_last_n": 33,
        "temperature": 0.8,
        "repeat_penalty": 1.2,
        "presence_penalty": 1.5,
        "num_ctx": 10240,
        "frequency_penalty": 1.0,
        "stop": ["user:", "\t", "十日终焉"]
        },
        "template":{
            "user":"",
            "assistant":""
        },
}


log_path=os.path.join(os.path.dirname(__file__),'chat_log.md')

def record_time():
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write("#"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')


def record(message,role):
    with open(log_path, 'a', encoding='utf-8') as f:
        if role==0:
            f.write("user:\n"+message+'\n')
        elif role==1:
            f.write("assistant:\n"+message+'\n')
    

def call_tool(message,role):
    message=chat_ollama_stream_post(message,role=role)
    return message

while True:
    message=input("请输入：")
    record(message,0)
    message=call_tool(message,role)
    record(message,1)