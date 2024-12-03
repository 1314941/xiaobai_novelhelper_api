########################################################################################################
# The RWKV Language Model - https://github.com/BlinkDL/RWKV-LM
########################################################################################################

import os
import copy
import types
import torch
from rwkv.model import RWKV
from rwkv.utils import PIPELINE
from fastapi import FastAPI
from pydantic import BaseModel
from tqdm import trange
import uvicorn
import ollama
import requests
import json
import time
from datetime import datetime
from requests.exceptions import RequestException


from template import add_template,add_prompt

app = FastAPI()



begin=False

running=False


BookPath='book/' #存放小说的路径

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


with open('role.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

data=data['system']

add_template(data)
add_prompt(data)

#将data写入json
with open(path+'/data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)



"""
"options": {
    "num_keep": 5,
    "seed": 42,
    "num_predict": 100,
    "top_k": 20,
    "top_p": 0.9,
    "tfs_z": 0.5,
    "typical_p": 0.7,
    "repeat_last_n": 33,
    "temperature": 0.8,
    "repeat_penalty": 1.2,
    "presence_penalty": 1.5,
    "frequency_penalty": 1.0,
    "mirostat": 1,
    "mirostat_tau": 0.8,
    "mirostat_eta": 0.6,
    "penalize_newline": true,
    "stop": ["\n", "user:"],
    "numa": false,
    "num_ctx": 1024,
    "num_batch": 2,
    "num_gpu": 1,
    "main_gpu": 0,
    "low_vram": false,
    "f16_kv": true,
    "vocab_only": false,
    "use_mmap": true,
    "use_mlock": false,
    "num_thread": 8
  }
"""

#修饰器
def check_running(func):
    def wrapper(*args, **kwargs):
        if running:
            return {"message": "模型正在运行，请稍后再试！"}
        else:
            return func(*args, **kwargs)
    return wrapper


# rwkv  电脑3060不够强 7b速度太慢了,有时还因为显存不足报错  3b很傻 回复字数很少(可能是配置问题,几十个字电脑风扇转的比ollama的qwen2.5:7b还快)
def chat_rwkv_stream_post(message:str,role:dict):
    #改为从文件读取
    

    #写入文件
    base_url ="http://127.0.0.1:8001/completions"
    if role['template']['user']=="none" or role['template']['assistant']=="none":
        pass
    else:
        message ="\n示例开始:\nuser:\n"+role['template']['user'] + "\nassistant:\n" + role['template']['assistant']+"\n示例结束。\n"+message
    # print(f"rwkv chat: \n{message}\n")

    data={
        "frequency_penalty": 0.5,
        "max_tokens": 2000,
        "model": "rwkv",
        "presence_penalty": 0,
        "prompt": message,
        "stream": True,
        "temperature": 2,
        "top_p": 0.3
    }

    content=""
    print("rwkv result:\n")



    # 使用 requests 库来连接服务器，并传递参数
    try:
        with  requests.post(base_url, json=data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    # 当服务器发送消息时，解码并打印出来
                    decoded_line = line.decode('utf-8')
                    #打印出来 方便调试
                    print(decoded_line[5:], end='\n')
                    print(json.loads(decoded_line[5:])["choices"][0]["text"], end="\n")
    except Exception as e:
        print(f'\nAn error occurred: {e}\n')
  
    return content




def on_message(message, free_gen_len, chunk_len):
    running=True
    srv = 'dummy_server'
    # 将消息中的换行符 \n 替换为实际换行符，并去除消息两端的空白字符。
    msg = message.replace('\\n','\n').strip()

    x_temp = 0.7
    x_top_p = 0.9
    # 消息中提取生成参数 x_temp（温度）和 x_top_p（核采样概率），并确保它们在有效范围内
    if "-temp=" in msg:
        x_temp = float(msg.split("-temp=")[1].split(" ")[0])
        msg = msg.replace("-temp="+f'{x_temp:g}', "")
        print(f"temp: {x_temp}")
    if "-top_p=" in msg:
        x_top_p = float(msg.split("-top_p=")[1].split(" ")[0])
        msg = msg.replace("-top_p="+f'{x_top_p:g}', "")
        print(f"top_p: {x_top_p}")
    x_temp = min(max(0, 2, x_temp), 5)
    x_top_p = max(0, x_top_p)
    
    msg = msg.strip()
    outline=read_outline()

    if outline is None:
        pass
    else:
        msg= "大纲"+"\n"+outline+"\n"+"上文：\n"+msg
    
    global data
    for role in data:
        if role['role'] == "文笔优化器":
            out = chat_rwkv_stream_post(msg,role)
            break
    result_msg = out
    array = [char for char in result_msg]
    res = {
        "label": result_msg,
        "kind": 0,
        # "insertText": array,
        "insertText": result_msg,
        "detail": result_msg
    }
    # template={
    #     "label": msg+"test\n",
    #     "kind": 0,
    #     "insertText": "test\n",
    #     "detail": "test\n"
    # }
    # print(f"result: \n{result_msg}")
    running=False
    # return [res,template]
    return [res]

def read_outline():
    a_path=BookPath+Outline
    if os.path.exists(a_path):
        with open(a_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    else:
        print("outline file not exist")
        return None


def save_outline(content):
    a_path=BookPath+Outline
    if os.path.exists(a_path):
        # 获取文件名和后缀
        file_name, file_extension = os.path.splitext(a_path)
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # 生成新的文件名
        new_file_name = f"{file_name}_{timestamp}{file_extension}"
        # 重命名文件
        os.rename(a_path, new_file_name)

    with open(BookPath+Outline, 'w', encoding='utf-8') as file:
        file.write(content)


########################################################################################################
class Data(BaseModel):
    msg: str
    generatorLength: int = 256
    chunkLength: int = 512


@app.post("/gen/")
def gen(data: Data):
    if running:
        return [{"label": "正在生成中，请稍后再试。", "kind": 0, "insertText": "正在生成中，请稍后再试。", "detail": "正在生成中，请稍后再试。"}]
    return on_message(data.msg, data.generatorLength, data.chunkLength)

#大纲接口  插件读取文章内容 发送到端口  端口先将原有文件重命名为时间戳  再将文章内容写入文件  
#也可以调用ollama接口生成
@app.post("/outline/")
def gen(data: Data):
    return on_message(data.msg, data.generatorLength, data.chunkLength)




if __name__ == '__main__':
    uvicorn.run(
        app='web_api:app',
        host="127.0.0.1",
        port=6288,
        reload=True,
        workers=1,
        log_config="log_conf.yaml",
    )


