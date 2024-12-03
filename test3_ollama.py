from web_api import chat_ollama_stream_post
from template import add_template,add_prompt


# 第1章 他叫白小纯 帽儿山，位于东林山脉中，山下有一个村子，民风淳朴，以耕田为生，与世隔绝。清晨，村庄的大门前，整个村子里的乡亲，正为一个十五六岁少年送别，这少年瘦弱，但却白白净净，看起来很是乖巧，衣着尽管是寻常的青衫，可却洗的泛白，穿在这少年的身上，与他目中的纯净搭配在一起，透出一股子灵动。他叫白小纯。“父老乡亲们，我要去修仙了，可我舍不得你们啊。”少年满脸不舍，原本就乖巧的样子，此刻看起来更为纯朴。四周的乡亲，面面相觑，顿时摆出难舍之色。“小纯，你爹娘走的早，你是个……好孩子！！难道你不想长生了么，成为仙人就可以长生，能活的很久很久，走吧，雏鹰长大，总有飞出去的那一天。”人群内走出一个头发花白的老者，说道好孩子三个字时，他顿了一下。“在外面遇到任何事情，都要坚持下去，走出村子，就不要回来，因为你的路在前方！”老人神色慈祥，拍了拍少年的肩膀。“长生……”白小纯身体一震，目中慢慢坚定起来，在老者以及四周乡亲鼓励的目光下，他重重的点了点头，深深的看了一眼四周的乡亲，转身迈着大步，渐渐走出了村子。眼看少年的身影远去，村中的众人，一个个都激动起来，目中的难舍刹那就被喜悦代替，那之前满脸慈祥的老者，此刻也在颤抖，眼中流下泪水。“苍天有眼，这白鼠狼，他终于……终于走了，是谁告诉他在附近看到仙人的，你为村子立下了大功！”“这白鼠狼终于肯离开了，可怜我家的几只鸡，就因为这白鼠狼怕鸡打鸣，不知用了什么方法，唆使一群孩子吃鸡肉，把全村的鸡都给吃的干干净净……”“今天过年了！”欢呼之声，立刻在这不大的村子里，沸腾而起，

#十日终焉  故事梗概：十个衣着各异的人在一个封闭房间中醒来，发现自己被神秘力量控制，参与一个游戏。游戏规则是参与者需要通过讲述故事来判断谁是说谎者，游戏过程中不断有人死去。齐夏凭借智慧和观察力，带领团队成员分析线索，共同面对挑战。经历了一系列的游戏后，团队被告知需要在十天内找到三千六百个“道”以拯救他们所在的世界。人龙出现并给予团队“道”的线索，同时暗示了更广阔的背景和即将到来的挑战。故事的结尾留下了悬念，参与者的未来和他们所在的世界的命运仍然未知。

import json
import time
import os


def call_tool(message,tool:str):
    for item in data:
        if item['role'] == tool:
            message=chat_ollama_stream_post(message,item)
            break
    return message

def call_tool_json(message,tool:str):
    while True:
        try:
            for item in data:
                if item['role'] == tool:
                    result=chat_ollama_stream_post(message,item)
                    break
            # 分割字符串
            parts = result.split('[')

            # 去掉第一个部分
            parts = parts[1:]

            # 分割剩余部分
            parts = parts[0].split(']')

            # 去掉最后一个部分
            parts = parts[:-1]

            # 重新组合字符串
            result = ''.join(parts)

            print(result)
            re_js=json.loads(result)
            break
        except Exception as e:
            print("error while calling tool for json result, retrying... ",e,"\n")
            message="user:\n"+message+"你的回答：\n"+result+"老师批改：\n需要修改,理由:"+e+"无需提出修改的思路，只能直接给出修改后的回答"
            time.sleep(1)
            continue
    return re_js


def call_tool_with_feedback(message,tool:str,demand=""):
    feedback:dict={
        "pass": "true",
        "reason": ""
    }
    while True:
        result=call_tool(message,tool)


        # feedback=call_tool(message,"老师批改器")
        # feedback=json.loads(feedback)
        for item in data:
                if item['role'] == tool:
                    demand=item['optimization']
                    break

        
        tea_message="user:\n"+message+"回答：\n"+result+"希望的回答需要达到的要求：\n"+demand+"请给出能否满足要求的选择，如果为否，给出修改建议"

        feedback=call_tool_json(tea_message,"老师批改器")

        if feedback['pass']=="false":
            message="user:\n"+message+"你的回答：\n"+result+"老师批改：\n需要修改,理由:"+feedback['reason']+"无需提出修改的思路，只能直接给出修改后的回答"
        else:
            break

    return result

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

add_template(data)
add_prompt(data)


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


#将data写入json
with open(path+'/data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

begin=True

input_dir = 'input'
files = os.listdir(input_dir)

# 过滤出符合条件的文件
txt_files = [f for f in files if f.endswith('.txt') and f.startswith('novel_part_')]

# 按文件名中的数字排序
txt_files.sort(key=lambda x: int(x.split('_')[2][:-4]))


character_message=""
main_message=""

count=1
# 依次读取并打印文件内容
for file in txt_files:
    with open(input_dir+'/'+file, 'r', encoding='utf-8') as f:
        input_message=f.read()
    if input_message=="":
        continue

    message="小说情节\n"+input_message+"\n旧的人物卡\n"+character_message+"\n生成新的人物卡"
    character_message=call_tool(message,"人物卡生成器")
    with open(path+Character_Card, "a", encoding="utf-8") as f:
                f.write(character_message)

    if begin:
        message="人物卡\n"+character_message+f"生成第{count}章的细纲"
        message=call_tool(message,"章节提取器")
        begin=False
    else:
        message="人物卡\n"+character_message+"上一章\n"+message+f"生成第{count}章的细纲"
        message=call_tool(message,"细纲生成器")
            
    with open(path+DetailedOutline, "a", encoding="utf-8") as f:
        f.write(message)
        
    message=message+f"以上是第{count}章的细纲，分析该细纲并生成一个或多个场景"
    message=call_tool(message,"细纲转场景器")

    message=call_tool(message=message,tool="场景大纲转json器")


    scene_num=len(message)    
    RoughChapter:str = ""
 
    #注意，range不包含终点， 例如 range(5) 输出 0 1 2 3 4
    for i in range(scene_num):
        message=message+f"根据该场景大纲，生成第{count}章第{i+1}个场景"

        message=call_tool(message=message,tool="场景填充器")
        RoughChapter+=message

    #已废弃
    # chapter_begin=True
    # feedback:dict={
    #     "pass": "true",
    #     "reason": ""
    # }


    message="人物卡\n"+character_message+RoughChapter+f"以上是第{count}章内容"
    RoughChapter=call_tool_with_feedback(message,"情节填充器")

    message="人物卡\n"+character_message+RoughChapter+f"以上是第{count}章内容"
    RoughChapter=call_tool_with_feedback(message,"角色刻画器")
    
    message="人物卡\n"+character_message+RoughChapter+f"以上是第{count}章内容"
    RoughChapter=call_tool_with_feedback(message,"对话润色器")

    message=RoughChapter+f"以上是第{count}章内容，清洗该章节，以通过审核，去掉全部与小说无关的字眼"
    RoughChapter=call_tool_with_feedback(message,"章节清洗器")


    with open(path+Chapter, "a", encoding="utf-8") as f:
        f.write(RoughChapter)

    count+=1