from zhipuai import ZhipuAI
import time

client = ZhipuAI(api_key="5185a14380b13a7bb9ef2c14a97ed105.oLXPHRnX7SnqCLLR") # 填写您自己的APIKey

def get_history(uhistory,ahistory):
    prompt = '用户:'+ uhistory + "回答:" + ahistory
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的记忆处理部分。你将接收到你与用户对话的历史纪录，格式为：'用户:+回答：'。你需要提取出对话的主题或者核心关键词，同时概括对话内容提取关键信息，注意保留你觉得后续聊天会提到的细节。输出格式例子：['颜色喜好','1.主要讲了用户的颜色喜好2.用户喜欢绿色']"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.95
    )             
    return(response.choices[0].message.content)

def find_key(user,keywords):
    prompt = '用户:'+ user + '关键词：'+ keywords
    response = client.chat.completions.creat(
          model="glm-4",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": "你是一个智能对话体的记忆查询部分。你将接收到用户的问询和你所有记忆的关键词，请通过对用户的问询和你所有记忆的关键词的相关性对比，选出其中你觉得相关性最大的几个关键词。输出格式为：'关键词1','关键词2'"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.95
    )
    return(response.choices[0].message.content)


def to_dict(x):
    stripped_string = x.strip('[]').replace("'", "")
    split_strings = stripped_string.split(', ')
    result_dict = {split_strings[0]: split_strings[1]+" #对话时间："+time.strftime('%Y-%m-%d %H:%M:%S')}
    return result_dict

memory = {}
related_memory = []

user = '我今天带哪个杯子去上班比较好，我比较喜欢绿色'
ans = "看起来你今天在选择带上哪个杯子去上班有些犹豫不决。我注意到你手中的两个杯子，一个是黑色盖子，另一个是白色盖子。如果你想要搭配你的黑色头发和灰色的毛衣，我建议你可以选择黑色盖子的杯子，这样看起来会更协调一些。当然，如果你想要一个更清爽的感觉，白色盖子的杯子也是个不错的选择。你更喜欢哪一个？"

original_string = get_history(user,ans)
result_dict = to_dict(original_string)

memory.update(result_dict)

keywords = list(memory.keys())
cur_key = find_key(keywords).split(',')
for i in cur_key:
    related_memory.append(i)

print(result_dict)

