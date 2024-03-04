from flask import Flask, render_template, request
import base64
import os
import datetime

app = Flask(__name__)
n = 0
@app.route('/')
def index():
    return render_template('index4video.html')

@app.route('/capture', methods=['POST'])
def handle_capture():
    # 从 POST 请求的表单数据中获取图像数据
    image_data = request.form['imageData']
    print(image_data)
    save_image(image_data)
    return 'Image received and saved successfully!'

def save_image(image_data):
    print("good")
    # Convert base64 image data to bytes
    image_bytes = base64.b64decode(image_data.split(',')[1])
    # Specify the directory to save images
    save_dir = 'images'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # Generate unique filename
    filename = os.path.join(save_dir,'_image.jpg')
    # Save the image to file
    with open(filename, 'wb') as f:
        f.write(image_bytes)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

