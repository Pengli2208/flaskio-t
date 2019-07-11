import psutil
import sqlite3
import time

'''
说明：四个cpu使用率，显然是临时数据，所以最好用内存数据库，如Redis等
但是这里强行使用sqlite3，不管了，哪个叫他是内置的呢？！
'''

db_name = 'com4016.db'


def create_db():
    # 连接
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 创建表 
    c.execute('''DROP TABLE IF EXISTS com4016''') # 删除旧表，如果存在（因为这是临时数据）
    c.execute('''CREATE TABLE com4016 (id INTEGER PRIMARY KEY AUTOINCREMENT, port text,insert_time text,device text, step int, valuec float, absval float)''')

    # 关闭
    conn.close()


def save_to_db(data):
    '''参数data格式：['00:01',3.5, 5.9, 0.7, 29.6]'''
    # 建立连接
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # 插入数据
    c.execute('INSERT INTO com4016(port,insert_time,device,step,value,abs) VALUES (?,?,?,?,?, ?)', data)
    
    # 提交！！！
    conn.commit()
    
    # 关闭连接
    conn.close()

    

# 创建表
create_db()

# 通过循环，对系统进行监控
while True:
    # 获取系统cpu使用率（每隔1秒）
    cpus = psutil.cpu_percent(interval=1, percpu=True)
    
    # 获取系统时间（只取分:秒）
    t = time.strftime('%M:%S', time.localtime())
    
    # 保存到数据库
    #save_to_db((t, *cpus))