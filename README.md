# 多模态多轮对话机器人
This Bot use chatglm4—v and chatglm which provide by zhipu.You just need a api_key from zhipu (https://open.bigmodel.cn) to run this bot
## abstract
**功能**
1. 自主决定在恰当时间通过摄像头获取视觉信息并用于对话 
2. 将每轮对话信息提取保存，对不同的输入选取与输入内容相关的对话记忆并作为输入丰富对话内容。
**web**
1. 前端调取主机摄像头，每隔0.3秒传一帧回后端，后端需要时即可通过不同的cookie为每个主机选取其的帧作为视觉信息输入
2. 可以让局域网中的其他的主机访问服务端，并且通过cookie来判断主机身份，从而在下次对话中也能为其调取之前对话的记忆

## 模块组成
**视觉**
根据所给帧提取视觉信息用于对话模块
**对话内容总结**
以每轮对话作为输入，提取对话中的关键词、关键信息、当前时间作为记忆。格式为['关键词'：'关键信息1','关键信息2','时间']，会将不同主机用户的记忆以pickle形式保存，方便下次调用。
**记忆选择**
将用户输入与记忆中的所有关键词进行比较，选取相关关键词关键信息组作为记忆内容输入给对话模块
**对话模块**
输入包括：'视觉信息''记忆信息''用户输入',当用户输入为空时，会从视觉信息中没话找话跟用户聊

## 展示
**结合视觉信息回答**
![image]('https://github.com/befocuss/accombot/blob/main/image/cup.png')
![image]('https://github.com/befocuss/accombot/blob/main/image/穿搭.png')

## ps
1. main.py是在本地运行，通过terminal使用
2. 4web\final.py是server程序，运行后可以使其他主机使用到本服务
# AccomBot

## Getting started

This Bot use chatglm4—v and chatglm which provide by zhipu.You just need a api_key from zhipu (https://open.bigmodel.cn) to run this bot

## Component
* Visual:
Get visual information for conversation
* Conversation summary:
Summarize the topic and details of the conversation for easy use in subsequent conversations
* memory filter
Select some memories related to this conversation
* Conversation:
Input contains Visual、memories、use input
