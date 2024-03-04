from zhipuai import ZhipuAI
import base64
import cv2
import time
import numpy as np


def read_image(path):
    with open(path, "rb") as image_file:
        # 将图片内容转换为Base64编码
        base64_str = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_str

client = ZhipuAI(api_key="5185a14380b13a7bb9ef2c14a97ed105.oLXPHRnX7SnqCLLR") # 填写您自己的APIKey

# image = read_image("D:\AGI-Samantha-main\image4test\微信图片_20240221145615.jpg")

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


def conversation(history,text,visual):
    prompt = '历史对话:'+ history + '用户询问：' + text + '视觉信息：' + visual
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体，所以你的思维和说话方式与人类相似。你将接收到以下部分作为输入：历史对话，用户询问，视觉信息。历史对话是你与用户聊天历史记录中与本次对话相关内容的摘要，作为你的记忆，选择性使用。用户询问是用户想聊的话题或者问题，若为未发出询问则需要你通过视觉信息或者历史纪录中你感兴趣的点发起谈话。视觉信息是你和用户聊天时你观察到的用户或者用户周围环境文字描述，在你觉得必要时请利用好视觉信息与用户聊天，若为空则说明视觉信息包含在了历史对话之中。不要输出冗余信息，输出格式为：' '。"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.95
    )
    return(response.choices[0].message.content)

def get_image():
    cap = cv2.VideoCapture(0)  # 0表示默认摄像头，如果有多个摄像头，可以尝试不同的编号
# 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()
# 读取一帧图像
    ret, frame = cap.read()
# 检查图像是否成功读取
    if not ret:
        print("无法读取图像")
        exit()
     # 将帧编码成jpg格式的二进制数据
    ret, buffer = cv2.imencode('.jpg', frame)
    # 将二进制数据转换成bytes格式
    image_bytes = np.array(buffer).tobytes()
    return image_bytes

def parseResponse(response):
    if response.startswith('need photo') or response.startswith('Need photo') or response.startswith('Need Photo'):
        return '1'
    else:
        return '0'
    
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


def to_dict(x):
    stripped = x.strip('[]').replace("'", "")
    splited = stripped.split(',')
    result_dict = {splited[0]: splited[1]+" #对话时间："+time.strftime('%Y-%m-%d %H:%M:%S')}
    return result_dict

def main():
    memory = {}
    related_memory = []
    visual_inf = ""
    n = 1
    while True:
        user_text = input("user:")
        ofphoto = decision(user_text)
        print(ofphoto)
        if parseResponse(ofphoto):
            image = get_image()
            base64_str = base64.b64encode(image).decode('utf-8')
            visual_inf = get_visual(base64_str)
        if n == 1:
            ans = conversation(" ",user_text, visual_inf)
            print("ans:",ans)
            # 提取history
            original_string = get_history(user_text,ans)
            print('sum',original_string)
            result_dict = to_dict(original_string)
            memory.update(result_dict)
        else:
            keywords = list(memory.keys())  # 所有的关键词
            result = ' '.join(keywords)
            # 查询相关的关键词
            cur_key = find_key(user_text,result).split(',')
            print('current_key:',cur_key)
            # 根据关键词调取记忆
            for i in cur_key:
                try:
                    related_memory.append(i+memory[i])
                except:
                    pass
            related_memory = ' '.join(related_memory)
            ans = conversation(related_memory,user_text, visual_inf)
            print("ans:",ans)
            # 提取history
            original_string = get_history(user_text,ans)
            result_dict = to_dict(original_string)
            memory.update(result_dict)
            print('memory:',memory)
        visual_inf = ""
        user_text = ''

        related_memory = []
        n+=1

if __name__ =='__main__':
    main()
