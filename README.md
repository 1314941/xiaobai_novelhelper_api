# 20241203 
才发现**codegeex**插件有个本地模式,可以连接本地的ollama。
[本地模型文档](https://zhipu-ai.feishu.cn/wiki/DAtfwkaqniX9erkxvIScCkSonKh)
尝试了一下修改本项目，以适配本地模式。
目标流程:
>接受信息\n
>加上人物卡信息\n
>发送给ollama\n
>返回信息


可惜，倒在了第一步，
>[2024-12-03T10:46:34.074Z] uvicorn.access INFO:     127.0.0.1:8856 - "POST /completions/ HTTP/1.1" 422

失败原因：参数错误  

不过，现在本地模型也够用了。
修改环境变量
![image](https://github.com/user-attachments/assets/5bb619ee-acb0-40dc-925d-48ca7289e896)

连接

![image](https://github.com/user-attachments/assets/894a23c7-5a6b-4a2f-9b5a-0888ed823f98)

## 修改提示词(根据需要修改)
### 自定义聊天提示词
```
你是一个杰出的作家,精通各种写作技巧,擅长写小说,能将复杂的想法和故事转化为易读易懂的文字。
```
### 自定义系统提示词
```
你是一个杰出的作家,精通各种写作技巧,擅长写小说,能将复杂的想法和故事转化为易读易懂的文字。你善于发现新鲜的想法,并将其应用到自己的作品中。你是一个优秀的网络小说作者,擅长将自己的创意和想法通过文字表达出来。我会给你一些文本片段，结构如下<|code_prefix|>：上文
 <|code_middle|>：你需要在这后面预测光标处的句子
 <|code_suffix|>：下文
 你需要根据上下文为我填充合适的句子；不要废话，不要输出 code_suffix、code_prefix、code_middle
```


# 介绍
[xiaobai_novelhelper](https://github.com/1314941/xiaobai_novelhelper)连接的接口。基于[ChatRWKV-Novel-api](https://github.com/Tlntin/ChatRWKV-Novel-api)
## 讲解
### book
目前用来存放小说大纲。outline.txt。
当收到输入时，将大纲加到输入的小说内容前，一并输入给本地ollama模型。
### input
之前尝试仿写小说时用到的小说内容。已分章
### out
仿写小说输出的存放点。
>outline 大纲
>detailed_outline 细纲
>chapter 具体章节
>character_card 角色卡
>data.json 本次仿写用到的模型参数文件。避免错过效果好的参数。
### template
目前只摸索出来6个ai组件。在role.json文件夹里记录着每个组件的参数，在运行时输入给模型。每个组件有对应id，根据id读取template里的文件夹，读取prompt，输出和输出示例。实在找不到如何使用ollama的template参数，只能取巧的在每次输出时在原有内容前加上示例。
### start.bat
我个人喜欢用这个。一键开启。.sh那个没修好。如果关闭了之后再次启动，可能会报
>接口被占用

的错误。以我个人经验，等一会就ok了。
或者可以用下面的命令
>netstat -ano | findstr :6288   找到占用接口的家伙
taskkill /PID 6288 /T /F   杀死它！！！一般不行
### ollama.bat 
start.bat用到的，用于启动ollama(居然无法通过ollama serve启动)。
### py文件
web_api.py  主要文件  接口
rwkv_api.py  旧的使用rwkv模型，参考用
人如其名，test.py，test2.py都是仿写小说的实验品。后面在b站看了相关视频和广大网友的评论，感觉对于我这种技术与财力都没有的小白太难啦，就将目标放在了帮助小白作家(我这个梦想宅在家里写小说，能活就行的)提升文笔上。

