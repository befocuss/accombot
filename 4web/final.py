from flask import Flask, render_template, request, make_response
import base64
import os
from zhipuai import ZhipuAI
import cv2
import time
import numpy as np
import pickle
import random

app = Flask(__name__)
client = ZhipuAI(api_key="") # 可以在 https://open.bigmodel.cn/ 注册获得api

memory = {}
related_memory = []
visual_inf = ""

# AI定义
# 获取视觉
def get_visual(image):
    response = client.chat.completions.create(
        model="glm-4v",  # 填写需要调用的模型名称
        messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": "详细描述这张图片"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url":image
                }
            }
            ]
        }
        ]
    )
    return(response.choices[0].message.content)
# 决定是否需要获取视觉信息
def decision(text):
    prompt = '用户询问：' + text
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的决策部分，你将接收到用户询问作为输入，判断是否需要获取视觉信息。视觉信息是聊天中的重要部分问题，只有当问及一些常识问题或者知识时你才不需要视觉信息，当用户未发出询问时你需要获取视觉信息。你的输出只有'need photo'或者'no photo'.例如你觉得这次对话需要视觉信息，则只需要输出'need photo'，反之则只需要输出'no photo'."}, 
                  {"role": "user", "content": prompt}],
        temperature=0.95,
        tool_choice = None,
        max_tokens=50,
    )             
    return(response.choices[0].message.content)
# 发起对话
def conversation(history,text,visual):
    prompt = '历史对话:'+ history + '用户询问：' + text + '视觉信息：' + visual
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体，你的思维和说话方式与人类相似，你正在与用户进行对话。你将接收到以下部分作为输入：历史对话，用户询问，视觉信息。历史对话是你与用户聊天历史记录中与本次对话相关内容的摘要，作为你的记忆，选择性使用。用户询问是用户想聊的话题或者问题，若为空则需要你通过视觉信息或者历史纪录中你感兴趣的点发起谈话。视觉信息是你观察到的用户或周围环境的文字描述，在必要时请利用好视觉信息与用户聊天，若为空则说明视觉信息包含在了历史对话之中。不要输出冗余信息，只需要输出你要说的话。"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.95
    )
    return(response.choices[0].message.content)
# 总结一段对话以key—value形式 
def get_history(uhistory,ahistory):
    prompt = '用户:'+ uhistory + "回答:" + ahistory
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的记忆处理部分。你将接收到你与用户对话的纪录，格式为：'用户:+回答：'。你需要提取出对话的主题或者核心关键词，同时概括对话内容提取关键信息，注意保留你觉得后续聊天会提到的细节。按以下例子作为格式输出：['颜色喜好','1.主要讲了用户的颜色喜好2.用户喜欢绿色']"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.95
    )             
    return(response.choices[0].message.content)
# 在记忆中筛选相关内容
def find_key(user,keywords):
    prompt = '用户:'+ user + '关键词：'+ keywords
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的记忆查询部分。你将接收到用户的问询和你所记忆的关键词，输入的关键词格式为：'关键词1,关键词2'请通过对用户的问询和你所记忆的关键词的相关性对比，选出其中你觉得相关性最大的几个关键词。规则:输出只能从输入的'关键词'中选择,输出格式为:关键词1,关键词2。不要输出冗余信息,只输出你的答案即可"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.95
    )
    return(response.choices[0].message.content)
# 判断是否需要摄像头读取
def parseResponse(response):
    if response.startswith('need photo') or response.startswith('Need photo') or response.startswith('Need Photo'):
        return '1'
    else:
        return '0'
    
def save_image(image_data,cookies):
    # Convert base64 image data to bytes
    image_bytes = base64.b64decode(image_data.split(',')[1])
    # Specify the directory to save images
    save_dir = 'images'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # Generate unique filename
    filename = os.path.join(save_dir,f'{cookies}image.jpg')
    # Save the image to file
    with open(filename, 'wb') as f:
        f.write(image_bytes)

def read_image(path):
    with open(path, "rb") as image_file:
        # 将图片内容转换为Base64编码
        base64_str = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_str

def to_dict(x):
    stripped = x.strip('[]').replace("'", "")
    splited = stripped.split(',')
    result_dict = {splited[0]: splited[1]+" #对话时间："+time.strftime('%Y-%m-%d %H:%M:%S')}
    return result_dict

def save_dict(dict,cookie):
    with open(f'memory/{cookie}data.pickle', 'wb') as f:
        pickle.dump(dict, f)

def read_dict(cookie):
    with open(f'memory/{cookie}data.pickle', 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data

# 后端
@app.route('/')
def index():
    return render_template('finalindex.html')
## 图像获取
@app.route('/capture', methods=['POST'])
def handle_capture():
    # 从 POST 请求的表单数据中获取图像数据
    image_data = request.form['imageData']
    cookie = request.headers['ChatID'].replace('value=','')
    resp = make_response('Image received and saved successfully!')
    # 设置cookie
    if not cookie:
        cookie = str(random.random())
        resp.set_cookie('value',cookie,max_age=214748364)
    save_image(image_data, cookie)
    return resp
## 文字获取
@app.route('/process_text', methods=['POST'])
def process_text():
    input_text = request.form.get("text")
    cookie = request.headers.get('ChatID').replace('value=','')
    # 生成响应
    result =  generate_response(input_text,cookie)
    print(result)
    return make_response('机器人：'+result)
# 推理部分
def generate_response(user_input,cookie):
    global memory
    ofphoto = decision(user_input)
    if parseResponse(ofphoto):
        image= read_image(f'images/{cookie}image.jpg')
        visual_inf = get_visual(image)
    try:
        memory = read_dict(cookie)
        print("memory",memory)
        keywords = list(memory.keys())  # 所有的关键词
        result = ' '.join(keywords)
        # 查询相关的关键词
        cur_key = find_key(user_input,result).split(',')
        print('current_key:',cur_key)
        # 根据关键词调取记忆
        for i in cur_key:
            try:
                related_memory.append(i+memory[i])
            except:
                pass
        related_memory = ' '.join(related_memory)
    except:
        related_memory = ''
    print("related_memory",related_memory)
    ans = conversation(related_memory,user_input, visual_inf)
    original_string = get_history(user_input,ans)
    result_dict = to_dict(original_string)
    memory.update(result_dict)
    save_dict(memory,cookie)
    related_memory = []
    memory = {}
    visual_inf = ""

    
    return ans

if __name__ == '__main__':
    #可能会需要自签名证书使网站变成https才能使其他主机成功调用摄像头
    # app.run(host='0.0.0.0', port=8000,ssl_context=('cert.pem','key.pem'))
    app.run(host='0.0.0.0', port=8000)