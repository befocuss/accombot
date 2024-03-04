from zhipuai import ZhipuAI
import base64
client = ZhipuAI(api_key="5185a14380b13a7bb9ef2c14a97ed105.oLXPHRnX7SnqCLLR") # 填写您自己的APIKey

def find_key(user,keywords):
    prompt = '用户:'+ user + '关键词：'+ keywords
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的记忆查询部分。你将接收到用户的问询和你所记忆的关键词，输入的关键词格式为：'关键词1,关键词2'请通过对用户的问询和你所记忆的关键词的相关性对比，选出其中你觉得相关性最大的几个关键词。输出必需从输入的关键词中选择，输出格式为：['关键词1','关键词2'],不要输出冗余信息，只输出你的答案即可"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.95
    )
    return(response.choices[0].message.content)

user = '好紧张'
keywords = '穿着打扮'

print(find_key(user,keywords))