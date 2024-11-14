from web_api import chat_ollama,chat_ollama_stream,chat_ollama_stream_post,timestamp


# 第1章 他叫白小纯 帽儿山，位于东林山脉中，山下有一个村子，民风淳朴，以耕田为生，与世隔绝。清晨，村庄的大门前，整个村子里的乡亲，正为一个十五六岁少年送别，这少年瘦弱，但却白白净净，看起来很是乖巧，衣着尽管是寻常的青衫，可却洗的泛白，穿在这少年的身上，与他目中的纯净搭配在一起，透出一股子灵动。他叫白小纯。“父老乡亲们，我要去修仙了，可我舍不得你们啊。”少年满脸不舍，原本就乖巧的样子，此刻看起来更为纯朴。四周的乡亲，面面相觑，顿时摆出难舍之色。“小纯，你爹娘走的早，你是个……好孩子！！难道你不想长生了么，成为仙人就可以长生，能活的很久很久，走吧，雏鹰长大，总有飞出去的那一天。”人群内走出一个头发花白的老者，说道好孩子三个字时，他顿了一下。“在外面遇到任何事情，都要坚持下去，走出村子，就不要回来，因为你的路在前方！”老人神色慈祥，拍了拍少年的肩膀。“长生……”白小纯身体一震，目中慢慢坚定起来，在老者以及四周乡亲鼓励的目光下，他重重的点了点头，深深的看了一眼四周的乡亲，转身迈着大步，渐渐走出了村子。眼看少年的身影远去，村中的众人，一个个都激动起来，目中的难舍刹那就被喜悦代替，那之前满脸慈祥的老者，此刻也在颤抖，眼中流下泪水。“苍天有眼，这白鼠狼，他终于……终于走了，是谁告诉他在附近看到仙人的，你为村子立下了大功！”“这白鼠狼终于肯离开了，可怜我家的几只鸡，就因为这白鼠狼怕鸡打鸣，不知用了什么方法，唆使一群孩子吃鸡肉，把全村的鸡都给吃的干干净净……”“今天过年了！”欢呼之声，立刻在这不大的村子里，沸腾而起，

#十日终焉  故事梗概：十个衣着各异的人在一个封闭房间中醒来，发现自己被神秘力量控制，参与一个游戏。游戏规则是参与者需要通过讲述故事来判断谁是说谎者，游戏过程中不断有人死去。齐夏凭借智慧和观察力，带领团队成员分析线索，共同面对挑战。经历了一系列的游戏后，团队被告知需要在十天内找到三千六百个“道”以拯救他们所在的世界。人龙出现并给予团队“道”的线索，同时暗示了更广阔的背景和即将到来的挑战。故事的结尾留下了悬念，参与者的未来和他们所在的世界的命运仍然未知。

import json
import time
import os

# 读取JSON文件
with open('role.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
data=data['system']

# 打印每个描述和对应的角色简称
for item in data:
    # print(f"角色简称: {item['role']}")
    # print(f"描述: {item['description']}")
    # print(f"优化建议: {item['optimization']}")
    # print("\n")
    pass

timestamp = 0
path='out/'
Character_Card='/Character_Card.txt' #存放角色卡片的路径
Outline='/Outline.txt' #存放小说大纲的路径
DetailedOutline='/DetailedOutline.txt' #存放小说详细大纲的路径
Chapter='/Chapter.txt' #存放小说章节的路径

if timestamp==0:
    # 获取当前时间戳
    timestamp = time.time()
    # 将时间戳转换为月日时分秒格式
    timestamp = time.strftime('%m-%d-%H-%M-%S', time.localtime(timestamp))
    #创建文件夹
    path=f"out/{timestamp}"
    if not os.path.exists(path):
        os.makedirs(path)


input_message = input("\nEnter message: ")
begin=True
for item in data:
    if item['role'] == "人物卡生成器":
        character_message=chat_ollama_stream_post(input_message,item)
        with open(path+Character_Card, "a", encoding="utf-8") as f:
            f.write(character_message)
        break

for item in data:
    if item['role'] == "大纲生成器":
        main_message=chat_ollama_stream_post("小说情节\n"+input_message+"人物卡\n"+character_message,item)
        with open(path+Outline, "a", encoding="utf-8") as f:
            f.write(Outline)
        break


while True:
    # out=chat_ollama(message,100)
    # out=chat_ollama_stream(message)

    for item in data:
        if item['role'] == "细纲生成器":
            if begin:
                message=main_message+character_message
                message=chat_ollama_stream_post(message,item)
                begin=False
                break
            else:
                message="大纲\n"+main_message+"上一章\n"+message
                message=chat_ollama_stream_post(message,item)
                break
    with open(path+DetailedOutline, "a", encoding="utf-8") as f:
        f.write(message)
        
    message=message
    for item in data:
        if item['role'] == "章节撰写器":
            message=chat_ollama_stream_post("人物\n"+character_message+"章节细纲\n"+message,item)
            break
    with open(path+Chapter, "a", encoding="utf-8") as f:
        f.write(message)
