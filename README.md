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
