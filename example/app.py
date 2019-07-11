#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import sqlite3
from flask import request, jsonify

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
db_name = '/home/pi/flask/Flask-SocketIO/example/com4016.db'


def create_db():
    # 连接
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 创建表 
    c.execute('''DROP TABLE IF EXISTS TB4016''') # 删除旧表，如果存在（因为这是临时数据）
    c.execute('''CREATE TABLE TB4016 (id INTEGER PRIMARY KEY AUTOINCREMENT, port text,insert_time text,device text, step int, valuec float, absval float)''')

    # 关闭
    conn.close()

def get_db():
    db = sqlite3.connect(db_name)
    db.row_factory = sqlite3.Row
    return db


def save_to_db(room, data):
    '''参数data格式：['00:01',3.5, 5.9, 0.7, 29.6]'''
    # 建立连接
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    strsql = "CREATE TABLE IF not exists TB" + room +"  (id INTEGER PRIMARY KEY AUTOINCREMENT, port text,insert_time text,device text, step int, valuec float, absval float)"
    print(strsql)
    c.execute(strsql)
    sqlStr = "INSERT INTO TB" + room +"(port,insert_time,device,step,valuec,absval) VALUES (?,?,?,?,?,?)"
    # 插入数据
    print(sqlStr)
    c.execute(sqlStr, data)
    
    # 提交！！！
    conn.commit()
    
    # 关闭连接
    conn.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        #socketio.emit('my_response',
        #              {'data': 'Server generated event', 'count': count, 'response':""},
        #              namespace='/test')

def PyHtml(content):
    content = "<b>\n\n"+content +"\n\n</b>"
    return content

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route("/concentration", methods=["POST"])
def get_concentration():
    if request.method == "POST":
        id1 = query_db("SELECT MAX(id) FROM TB4016", args=())
        reqId = 0
        try:
            if int(id1[0][0]) < 30:
                reqId = int(request.form['id'])
            else:
                reqId = int(id1[0][0]) - 30
            res = query_db("SELECT * FROM TB4016 WHERE id>=(?)", args=(reqId+1,))
            return jsonify(insert_time = [x[2] for x in res],
                   concentration = [x[5] for x in res],
                   detail = [x[1] for x in res] + [x[3] for x in res] + [x[4] for x in res])
        
        except Exception as e:
            print('error', repr(e))
            pass
        return jsonify(insert_time="0:0", concentration=[0.0,0.0], detail="0,0,0,")
    # 返回json格式


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 
          'count': session['receive_count'],
          'response':message['data'],
	  'port':"FFFF"})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count'],
         'response':PyHtml(message['data']),
	 'port':"FFFF"},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count'],
          'response':PyHtml('In rooms: ' + ', '.join(rooms())),
	  'port':message['room']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    #session['receive_count'] = session.get('receive_count', 0) + 1
    
@socketio.on('leaveall', namespace='/test')
def leaveall(message):
    emit('my_response',
         {'data': 'Leave rooms: ' + ', '.join(rooms())+'\n',
          'count': session['receive_count'], 
          'response':PyHtml('Leave rooms: ' + ', '.join(rooms())),
	  'port':"FFFF"})
    for ro in rooms():
        leave_room(ro)
        print("leave ",	ro) 


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count'],
                         'response':PyHtml('Room ' + message['room'] + ' is closing.'),
			 'port':message['room']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message1(message):
    #session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 
	  'count': 0, 
          'response':message['response'],
	  'port':message['room']},
         room=message['room'])



@socketio.on('my_sql_event', namespace='/test')
def send_room_message2(message):
    #session['receive_count'] = session.get('receive_count', 0) + 1
    print('sql message:', message['data'])
    sqlData = message['data'].split(',')
    print('sql message:', sqlData)
    room=message['room']
    save_to_db(room,sqlData)


@socketio.on('my_send_event', namespace='/test')
def send_room_message(message):
    #session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_send',
         {'data': message['data'], 
	  'count': 0, 
          'response':message['room'], 
	  'port':message['room']},
         room=message['room'])

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!\n', 
	  'count': session['receive_count'],
          'response':PyHtml('Disconnected'),
	  'port':message['room']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    #emit('my_response','test123')


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected\n', request.sid)



if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', debug=True)
