#codegeex 本地模型 连接 
# [2024-12-03T10:46:34.074Z] uvicorn.access INFO:     127.0.0.1:8856 - "POST /completions/ HTTP/1.1" 422
# 失败原因：参数错误

import os
import copy
import types
import torch
from fastapi import FastAPI
from tqdm import trange
import uvicorn
from pydantic import BaseModel
import ollama
import requests
import json
import time
from datetime import datetime

from template import add_template,add_prompt

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定具体的源
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


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

# def check_timestamp(func):
#     def wrapper(*args, **kwargs):
#         # if begin==False:
#         if timestamp==0:
#             # 获取当前时间戳
#             timestamp = time.time()
#             # 将时间戳转换为月日时分格式
#             timestamp = time.strftime('%m-%d %H:%M', time.localtime(timestamp))
#             # begin=True
#         func(*args, **kwargs)
#     return wrapper



def chat_ollama(tokens):
    print(f"ollama chat: \n{tokens}")
    #参数说明 https://gitee.com/ollama/ollama/blob/main/docs/modelfile.md
    # options = {
    # "temperature": 0.7,  # 控制生成文本的随机性
    # "num_ctx": 4096,     # 控制上下文长度
    # "top_p": 0.7,        # 控制生成文本的多样性
    # "seed": 1234567890,           # 随机种子
    # "num_predict": 100,    # 控制生成文本的长度
    # "presence_penalty": 0.4,  # 存在惩罚参数
    # "frequency_penalty": 0.5,  # 频率惩罚参数
    # }

    system_message = {"role": "system","content": "你是一个杰出的作家，请根据输入的小说片段完善小说情节。"}
    result = ollama.chat(model="novel:latest",
                       messages=[{"role": "user","content": tokens}],
                    #    options=options,
                       format="json",
                       stream = False)
    # 处理返回结果
    back=""

    # 提取 done_reason 字段
    data=result
    # done_reason = data.get("done_reason")

    # 提取 done 字段
   
   
    print("ollama result:", data)

    done = data.get("done")
    if not done:
        return chat_ollama(tokens)
    # print("done_reason:",done_reason,"\ndone:",done)


    # 提取 content 字段
    back = data.get("message", {}).get("content")
    return back

def chat_ollama_stream(tokens,prefix="续写"):
    #参数说明 https://gitee.com/ollama/ollama/blob/main/docs/modelfile.md
    # options = {
    # "temperature": 0.7,  # 控制生成文本的随机性
    # "num_ctx": 4096,     # 控制上下文长度
    # "top_p": 0.7,        # 控制生成文本的多样性
    # "seed": 1234567890,           # 随机种子
    # "num_predict": 100,    # 控制生成文本的长度
    # "presence_penalty": 0.4,  # 存在惩罚参数
    # "frequency_penalty": 0.5,  # 频率惩罚参数
    # }

    options = {
        "stop": ["\n", "user:","\t"]
    }

    tokens = prefix + " " + tokens
    print(f"ollama chat: \n{tokens}")
    system_message = {"role": "system","content": "你是一个杰出的作家，请根据输入的小说片段完善小说情节。"}
    result = ollama.chat(model="novel:latest",
                       messages=[{"role": "user","content": tokens}],
                       options=options,
                       format="json",
                       stream = True)
    content=""
    print("ollama result:\n")
    for line in result:
        if isinstance(line, dict):  # 确保 line 是字典类型
            text = line['message']['content']
        else:
            data = json.loads(line)  # 使用 JSON 加载
            text = data['message']['content']
        print(text, end='')
        content += text
    return content

#使用generate接口!!!  chat接口前言不搭后语 之前没注意，用了旧代码的chat接口，导致一堆换行符
# @check_timestamp
def chat_ollama_stream_post(message:str,role:dict):
    #改为从文件读取
  
    tokens = message
    #写入文件
    base_url ="http://localhost:11434/api/generate"
    if role['template']['user']=="none" or role['template']['assistant']=="none":
        pass
    elif role['template']['user']=="" or role['template']['assistant']=="":
        pass
    else:
        tokens ="\n示例开始:\nuser:\n```\n"+role['template']['user'] + "\n```\nassistant:\n```\n" + role['template']['assistant']+"\n```\n示例结束。\n"+tokens
    print(f"ollama chat: \n{tokens}\n")

    data = {
        "model": "novel:latest",
        # "model": "yinian:latest",
        # "model": "llama3_novel:latest",
        # "model": "little_text",
        "system": role['description'], 
        "options": role['options'], 
        "prompt": tokens,
        "stream": True
    }
    response = requests.post(base_url, json=data, stream=True)
    content=""
    print("ollama result:\n")

    for line in response.iter_lines():
        line = json.loads(line.decode('utf-8'))
        if isinstance(line, dict):  # 确保 line 是字典类型  generate 接口 返回response 字段
            text = line['response']
        else:
            data = json.loads(line)  # 使用 JSON 加载
            text = data['response']
        print(text, end='')
        content += text
    print("\n")
  
    return content


def chat_ollama_flowise(tokens,prefix="续写"):
    #参数说明 https://gitee.com/ollama/ollama/blob/main/docs/modelfile.md
    options = {
    "temperature": 0.7,  # 控制生成文本的随机性
    "num_ctx": 4096,     # 控制上下文长度
    "top_p": 0.7,        # 控制生成文本的多样性
    "seed": 1234567890,           # 随机种子
    "num_predict": 100,    # 控制生成文本的长度
    "presence_penalty": 0.4,  # 存在惩罚参数
    "frequency_penalty": 0.5,  # 频率惩罚参数
    }


    tokens = prefix + " " + tokens
    print(f"ollama chat: \n{tokens}")
    system_message = {"role": "system","content": "你是一个杰出的作家，请根据输入的小说片段完善小说情节。"}
    result = ollama.chat(model="novel:latest",
                       messages=[{"role": "user","content": tokens}],
                       options=options,
                       format="json",
                       stream = False)
    # 处理返回结果
    back=""

    # 提取 done_reason 字段
    data=result
    # done_reason = data.get("done_reason")

   
   
    print("ollama result:", data)

    done = data.get("done")
    if not done:
        return chat_ollama(tokens)
    # print("done_reason:",done_reason,"\ndone:",done)


    # 提取 content 字段
    back = data.get("message", {}).get("content")
    return back




def on_message(message, free_gen_len, chunk_len):
    running=True
    srv = 'dummy_server'
    # 将消息中的换行符 \n 替换为实际换行符，并去除消息两端的空白字符。
    msg = message.replace('\\n','\n').strip()

    msg = msg.strip()
    outline=read_outline()

    if outline is None:
        pass
    else:
        msg= "大纲"+"\n"+outline+"\n"+"上文：\n"+msg
    
    global data
    for role in data:
        if role['role'] == "文本填充器":
            out = chat_ollama_stream_post(msg,role)
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


    # print(f"result: \n{result_msg}")
    running=False
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

"""
{​
  "model": "<MODEL NAME>",​
  "messages": [​
    {​
      "role": "user",​
      "content": "CodeGeeX is awesome!"​
    }​
  ],​
  "temperature": "<TEMPERATURE>",​
  "top_p": "<TOP_P>",​
  "max_tokens": "<MAX_TOKENS>",​
  "presence_penalty": "<PENALTY>",​
  "stream": true,​
  "stop": []​
}
"""


class Message(BaseModel):
    role: str
    content: str

 
class Data(BaseModel):
    model: str
    messages: list[Message]
    temperature: str
    top_p: str
    max_tokens: str
    presence_penalty: str
    stream : bool
    stop: list[str]



#示例
#http://localhost:6288/completions/?msg=你好&generatorLength=256&chunkLengt=512
@app.post("/completions/")
def completions(data:Data):
# def completions(model, messages, temperature, top_p, max_tokens, presence_penalty, stream, stop):
    try:
        print(data)
        # 处理逻辑
    except Exception as e:
        print(f"处理请求时发生错误: {e}")
    # if running:
        # return [{"label": "正在生成中，请稍后再试。", "kind": 0, "insertText": "正在生成中，请稍后再试。", "detail": "正在生成中，请稍后再试。"}]
    # return on_message(data.msg, data.generatorLength, data.chunkLength)




if __name__ == '__main__':
    uvicorn.run(
        app='codegeex_api_local:app',
        host="127.0.0.1",
        port=6288,
        reload=True,
        workers=1,
        log_config="log_conf.yaml",
    )

