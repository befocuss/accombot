from zhipuai import ZhipuAI
import base64
import cv2
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
                "text": "你是一个智能对话体的'眼睛'部分，你需要将图片转化为'大脑'能理解的文字描述。你可以对图片中你觉得在对话中会用到的细节进行详细描述。"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image
                }
            }
            ]
        }
        ]
    )
    return(response.choices[0].message.content)

def decision(text):
    prompt = '用户询问' + text
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的决策部分，你将接收到用户询问作为输入，判断是否需要获取视觉信息。视觉信息是聊天中的重要部分问题，只有当问及一些常识问题或者知识时你才不需要视觉信息，当用户未发出询问时你需要获取视觉信息。你的输出只有'need photo'或者'no photo'.例如你觉得这次对话需要视觉信息，则只需要输出'need photo'，反之则只需要输出'no photo'."}, 
                  {"role": "user", "content": prompt}],
        temperature=0.95

    )             
    return(response.choices[0].message.content)


def conversation(history,text,visual):
    prompt = '历史对话:'+ history + '用户询问：' + text + '视觉信息：' + visual
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体，所以你的思维和说话方式与人类相似。你将接收到以下部分作为输入：历史对话，用户询问，视觉信息。历史对话是你与用户聊天历史记录的摘要，作为你的记忆。用户询问是用户想聊的话题或者问题，若为未发出询问则需要你通过视觉信息或者历史纪录中你感兴趣的点发起谈话。视觉信息是你和用户聊天时你观察到的用户或者用户周围环境的信息，在你觉得必要时请利用好视觉信息与用户聊天，若为空则说明视觉信息包含在了历史对话之中。你的输出即为你对用户说的话。"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.95
    )
    return(response.choices[0].message.content)

def get_historty(uhistory,ahistory):
    prompt = '用户:'+ uhistory + "回答:" + ahistory
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的记忆处理部分。你将接收到你与用户聊天的历史纪录，格式为：'用户:+回答：'。你需要提取出历史纪录中的关键信息，注意要保留你觉得后续聊天会提到的细节。输出格式为:'1. 2. 3.'"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=200,
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
    cap.release()
    # 将帧编码成jpg格式的二进制数据
    ret, buffer = cv2.imencode('.jpg', frame)

    # 将二进制数据转换成bytes格式
    image_bytes = np.array(buffer).tobytes()
    # cv2.imwrite(f'{n}photo.jpg', frame)
    return image_bytes

def parseResponse(response):
    if response.startswith('need photo') or response.startswith('Need photo') or response.startswith('Need Photo'):
        return '1'
    else:
        return '0'

def main():
    history = ""
    visual_inf = ""
    n=0
    while True:
        user_text = input("user:")
        photo = decision(user_text)
        de = parseResponse(photo)
        print(photo)
        if de == '1':
            image = get_image()
            # cv2.imshow('Camera', image)
            # cv2.waitKey()
            base64_str = base64.b64encode(image).decode('utf-8')
            visual_inf = get_visual(base64_str)
            print(visual_inf)
        ans = conversation(history,user_text, visual_inf)
        print("ans:",ans)
        history = get_historty(user_text,ans)
        print("histpry:",history)
        visual_inf = ""
        user_text = ''
        n += 1
    
if __name__ =='__main__':
    main()