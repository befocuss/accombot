# start_server.py
from flask import Flask, request,render_template
from zhipuai import ZhipuAI
from OpenSSL import SSL

app = Flask(__name__)

client = ZhipuAI(api_key="5185a14380b13a7bb9ef2c14a97ed105.oLXPHRnX7SnqCLLR")
# SSL上下文
context = SSL.Context(SSL.TLSv1_2_METHOD)
context.use_privatekey_file('D:/AGI-Samantha-main/zhipuai.com/accombot/4web/private.key')
context.use_certificate_file('D:/AGI-Samantha-main/zhipuai.com/accombot/4web/certificate.pem')

def conversation(text):
    prompt = '用户询问：' + text
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[ {"role": "user", "content": prompt}],
        temperature=0.95,
        tool_choice = None,
        max_tokens=50,

    )             
    return(response.choices[0].message.content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    input_text = request.form['text']


    # 生成响应
    result = generate_response(input_text)


    return render_template("index.html",user_input=input_text, bot_response=result)

def generate_response(input_text):
    generated_text = conversation(input_text)
    return generated_text

	
if __name__ == '__main__':
    context = (r'D:\AGI-Samantha-main\zhipuai.com\accombot\4web\private.key',r'D:/AGI-Samantha-main/zhipuai.com/accombot/4web/certificate.pem')
    app.run(host='0.0.0.0', port=8000,ssl_context=context)

