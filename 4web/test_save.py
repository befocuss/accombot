import pickle
# 定义一个字典
    
with open('memory/0.977814896258434data.pickle', 'rb') as f:
    loaded_data = pickle.load(f)

# 使用加载的数据
print(loaded_data)
