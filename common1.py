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
from multiprocessing import Process
 
sio = socketio.Client()
name_space = '/test'
gSocketCon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
buffRev = ""
timeRev = ""
room_adr = ""
connectState = 0

@sio.on('connect')
def on_connect():
	"""创建连接"""
	global connectState
	print('I am connected!, state', connectState, room_adr)
	connectState = 1
	
@sio.on('my message')
def on_message(data):
	print('I received a custom message!',room_adr)
     

@sio.on('disconnect')
def on_disconnect():
	"""关闭连接"""
	global connectState
	print('I m disconnected!,state,',connectState, room_adr)
	connectState = 0
	InitConnection()
     
@sio.on('callback message', namespace=name_space)
def my_event_handler(msg):
	# 客户端接收服务端的回调消息
	print("disconnect with new msg:", msg)
	# 接收完消息关闭连接
	#sio.disconnect()
	return "ok!"
     
@sio.on('my_response', namespace=name_space)
def my_msg_handler(msg):
	return "OK"    
    
    
@sio.on('my_send', namespace=name_space)
def my_msg_send(msg):
	global gSocketCon
	print('my_send message',room_adr)
	# 客户端接收服务端的回调消息
	try:
		print(msg['port'],room_adr)
		try:
			print(msg['data'],room_adr)
			a = msg['data']
			b = a.encode(encoding='gbk')
			b += b'\n'
		except Exception as e:
			print(e,room_adr)
			pass
		try:
			gSocketCon.send(b)
		except Exception as e:
			print(e,room_adr)
			pass
	except Exception as e:
		print(e,room_adr)
		print('exception',room_adr)   
		pass 
		
		
def HandleMeasureData(bb):
	global buffRev	
	global timeRev 
	
	bb1 = buffRev + bb
	
	if bb.find('\n') == -1:
		buffRev = buffRev + bb
		return
	else:
		buffRev = bb
	
	
	
	buff1 = bb1.split('\n')
	
	for buff in buff1:
		if buff.find('type,1') != -1:
			buff = buff.replace('\033[33m','')
			buff = buff.replace('\033[31m','')
			buff = buff.replace('\033[35m','')
			buff = buff.replace('\033[0m','')
			buff = buff.replace('\t','')
			str_split = buff.split(',')
			if len(str_split) > 10 and timeRev != str_split[0]:
				timeRev = str_split[0]
				# port, time, device, step, value, abs
				data = room_adr+","+str_split[0]+","+str_split[1]+","+str_split[2]+","+str_split[6]+","+str_split[10]
				print(room_adr,data);
				try:
					sio.emit('my_sql_event', {'room': room_adr, 'data': data, 'response':str(data)}, namespace=name_space)
				except Exception as e:
					print(e,room_adr)
					print('excep,HandleMeasureData',room_adr)
					pass
					
	    
def InitConnection():
	global connectState
	while True:
		
		try:
			print('connect try again_ 1,state', connectState, room_adr)
			if connectState != 0:
				sio.disconnect()
			sio.sleep(4)
			sio.connect('http://procontrol.top:5000/')
			sio.emit('join', {'room': room_adr, 'port': room_adr}, namespace=name_space)
			print(room_adr, 'connect try again')
			break
		except Exception as e:
			sio.disconnect()
			print('except, InitConnection',room_adr)
			print(e,room_adr)
			connectState = 1
			sio.sleep(4)
			pass
			
	print('connected,',connectState, room_adr)
	
	
def ConnectRoom(st):
	sio.connect('http://procontrol.top:5000/')
	sio.emit('my_broadcast_event', {'data': "I am new connected: "+room_adr, 'count': 23}, namespace=name_space)
	sio.emit('join', {'room': room_adr, 'port': room_adr}, namespace=name_space)
	print('ConnectRoom,', connectState, room_adr)			

def ThreadConn(ts, cfg):
	global gSocketCon
	global room_adr
	while True:
		room_adr = str(cfg[2])
		try:
			gSocketCon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			gSocketCon.connect((cfg[0], cfg[1])) 
			
			ConnectRoom(False)
			
			
			while True:
				try:
					buff = gSocketCon.recv(0x100)
					utfstr1 = buff.decode('utf-8','ignore')
					utfstr2 = utfstr1
					#1 - msg
					utfstr1 = utfstr1.replace('\033[33m','<font color="#FFFF00">')
					utfstr1 = utfstr1.replace('\033[0m','</font>')
					#3 user
					utfstr1 = utfstr1.replace('\033[35m','<font color="#FF00FF">')  
					#2 debug
					utfstr1 = utfstr1.replace('\033[31m','<font color="#FF0000">')  
					#print(room_adr,utfstr1)
					utfstr = utfstr1
				except Exception as e:
					
					print('except, gSocketCon',room_adr)
					print(e,room_adr)
					pass 
				try:	
					HandleMeasureData(utfstr2)
					sio.emit('my_room_event', {'room': room_adr, 'data': "", 'response':str(utfstr)}, namespace=name_space)
				except Exception as e:
					print('emit, exception', room_adr)
					print(e,room_adr)
					break
		except Exception as e:
			print('ThreadConn',room_adr)
			print(e,room_adr)
			pass 
		
		
if __name__ == '__main__':
	mapCon =[ 
	#['192.168.1.201', 4196, 4011],
	#['192.168.1.202', 4196, 4012],
	#['192.168.1.203', 4196, 4013],
	#['192.168.1.204', 4196, 4014],
	['192.168.1.205', 4196, 4015],
	#['192.168.1.206', 4196, 4016],
	#['192.168.1.207', 4196, 4017],
	#['192.168.1.208', 4196, 4018],
	
	#['192.168.1.211', 4196, 4021],
	#['192.168.1.212', 4196, 4022],
	#['192.168.1.213', 4196, 4023],
	#['192.168.1.214', 4196, 4024],
	#['192.168.1.215', 4196, 4025],
	#['192.168.1.216', 4196, 4026],
	#['192.168.1.217', 4196, 4027],
	#['192.168.1.218', 4196, 4028],
	
	#['192.168.1.221', 4196, 4031],
	#['192.168.1.222', 4196, 4032],
	#['192.168.1.223', 4196, 4033],
	#['192.168.1.224', 4196, 4034],
	#['192.168.1.225', 4196, 4035],
	#['192.168.1.226', 4196, 4036],
	#['192.168.1.227', 4196, 4037],
	#['192.168.1.228', 4196, 4038],
		]
	sio.connect('http://procontrol.top:5000/')
	sio.sleep(1)
	print('connect to server')
	tlist = []  # 线程列表，最终存放两个线程对象
	for mapCon1 in mapCon:
		#p = Process(target=ThreadConn, args=(sio, mapCon1))
		p = threading.Thread(target=ThreadConn, args=(sio, mapCon1))
		tlist.append(p)
	
	for t in tlist:
		t.start()
		
	for t in tlist:
		t.join()