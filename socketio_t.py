#!/usr/bin/env python  
# encoding: utf-8  
""" 
@version: v1.0 
@author: Paul Li 
@license: Apache Licence  
@contact: lpy_ren@163.com 
@software: Visual studio 
@file: socketio_t.py 
@time: 2019/6/27 10:31 
@describe: 采用 socketio 模块进行消息发布与接收
"""
import sys
import os
import socketio
import socket
import sys
import threading
import time
import os
 
sio = socketio.Client()
name_space = '/test'
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mapConDict = {}	
    
@sio.on('connect')
def on_connect():
	"""创建连接"""
	print('I am connected!')
	
@sio.on('my message')
def on_message(data):
	print('I received a custom message!')
     

@sio.on('disconnect')
def on_disconnect():
	"""关闭连接"""
	print('I m disconnected!')
     
	'''
	官方文档：
	事件回调:
	当客户端向服务器发送事件时，它可以选择提供回调函数，作为服务器处理事件的确认方式调用。
	虽然这完全由客户端管理，但服务器可以提供要传递给回调函数的值列表，只需从处理函数返回它们：
	@sio.on('my event', namespace='/chat')
	def my_event_handler(sid, data):
	# handle the message
	return "OK", 123
	同样，服务器可以请求在客户端处理事件后调用回调函数。该socketio.Server.emit()
	方法有一个可选callback参数，可以设置为可调用。如果给出了此参数，则在客户端处理完事件后将调用callable，
	并且客户端返回的任何值都将作为参数传递给此函数。不建议在向多个客户端广播时使用回调函数，
	因为将为接收消息的每个客户端调用一次回调函数。
	'''
     
@sio.on('callback message', namespace=name_space)
def my_event_handler(msg):
	# 客户端接收服务端的回调消息
	if len(msg.data) > 1:
		print("my receive new msg:", msg)
	# 接收完消息关闭连接
	sio.disconnect()
	return "ok!"
     
@sio.on('my_response', namespace=name_space)
def my_msg_handler(msg):
	return "OK"    
    
    
@sio.on('my_send', namespace=name_space)
def my_msg_send(msg):
	global mapConDict
	# 客户端接收服务端的回调消息
	try:
		print(msg['port'])
		connp = mapConDict.get(msg['port'],"TT")
		if connp != "TT":
			
			try:
				print(msg['data'])
				a = msg['data']
				b = a.encode(encoding='gbk')
				b += b'\n'
			except Exception as e:
				print(e)
				pass
			try:
				connp.send(b)
			except Exception as e:
				print(e)
				pass
	except Exception as e:
		print(e)
		pass    
		# 接收完消息关闭连接
		#sio.disconnect()
		#return "ok!"
		# 建立连接对象
    
def TestFunc(host, port_c, port):
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((host, port_c)) 
	sio.connect('http://processcontrol.f3322.net:5000/')
	room_id = str(port)
	sio.emit('my_broadcast_event', {'data': "I am new connected: "+room_id, 'count': 23}, namespace=name_space)
	sio.emit('join', {'room': room_id, 'port': room_id}, namespace=name_space)


	while True:
		buff = conn.recv(0x100)
		#buff = buff.replace('\n','<br>')
		utfstr1 = buff.decode('utf-8','ignore')
		#1 - msg
		utfstr1 = utfstr1.replace('\033[33m','<font color="#FFFF00">')
		utfstr1 = utfstr1.replace('\033[0m','</font>')
		#3 user
		utfstr1 = utfstr1.replace('\033[35m','<font color="#FF00FF">')  
		#2 debug
		utfstr1 = utfstr1.replace('\033[31m','<font color="#FF0000">')  
		#print(utfstr)
		utfstr = "<pre>"+utfstr1+"</pre>"
		#utfstr = utfstr.replace('\t','<br>')
		sio.emit('my_room_event', {'room': room_id, 'data': "", 'response':str(utfstr)}, namespace=name_space)
		#sio.emit('my_broadcast_event', {'data':" message['data']", 'count': 23}, namespace=name_space)
            	#sio.sleep(1)


def ThreadConn(sio1, room_id, connp):
	while True:
		try:
			buff = connp.recv(0x100)
			utfstr1 = buff.decode('utf-8','ignore')
			#1 - msg
			utfstr1 = utfstr1.replace('\033[33m','<font color="#FFFF00">')
			utfstr1 = utfstr1.replace('\033[0m','</font>')
			#3 user
			utfstr1 = utfstr1.replace('\033[35m','<font color="#FF00FF">')  
			#2 debug
			utfstr1 = utfstr1.replace('\033[31m','<font color="#FF0000">')  
			#print(room_id,utfstr1)
			utfstr = utfstr1
			sio1.emit('my_room_event', {'room': room_id, 'data': "", 'response':str(utfstr)}, namespace=name_space)
		except Exception as e:
			print(e)
			pass 
		
		
if __name__ == '__main__':
	mapCon =[ 
	['192.168.1.201', 4196, 4011],
	['192.168.1.202', 4196, 4012],
	['192.168.1.203', 4196, 4013],
	['192.168.1.204', 4196, 4014],
	['192.168.1.205', 4196, 4015],
	['192.168.1.206', 4196, 4016],
	['192.168.1.207', 4196, 4017],
	['192.168.1.208', 4196, 4018],
	
	['192.168.1.211', 4196, 4021],
	['192.168.1.212', 4196, 4022],
	['192.168.1.213', 4196, 4023],
	['192.168.1.214', 4196, 4024],
	['192.168.1.215', 4196, 4025],
	['192.168.1.216', 4196, 4026],
	['192.168.1.217', 4196, 4027],
	['192.168.1.218', 4196, 4028],
	
	['192.168.1.221', 4196, 4031],
	['192.168.1.222', 4196, 4032],
	['192.168.1.223', 4196, 4033],
	['192.168.1.224', 4196, 4034],
	['192.168.1.225', 4196, 4035],
	['192.168.1.226', 4196, 4036],
	['192.168.1.227', 4196, 4037],
	['192.168.1.228', 4196, 4038],
		]
	sio.connect('http://processcontrol.f3322.net:5000/')
	for cfg in mapCon:
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.connect((cfg[0], cfg[1])) 
		room_id = str(cfg[2])
		sio.emit('my_broadcast_event', {'data': "I am new connected: "+room_id, 'count': 23}, namespace=name_space)
		sio.emit('join', {'room': room_id}, namespace=name_space)
		mapConDict[ room_id ] = conn
		#print(mapConDict[ room_id ])
		
		
	tlist = []  # 线程列表，最终存放两个线程对象
	for key, connp in mapConDict.items():
		
		t = threading.Thread(target=ThreadConn, args=(sio,key,connp))
		tlist.append(t)
	
	for t in tlist:
		t.start()
		
	for t in tlist:
		t.join()