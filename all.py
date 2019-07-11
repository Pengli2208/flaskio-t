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
from common1 import ThreadConn

import sys
import threading
import time
import os
from multiprocessing import Process
		
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
	
	#sio.sleep(1)
	sio1 = 0
	#print('connect to server')
	tlist = []  # 线程列表，最终存放两个线程对象
	for mapCon1 in mapCon:
		p = Process(target=ThreadConn, args=(sio1, mapCon1))
		#p = threading.Thread(target=ThreadConn, args=(sio1, mapCon1))
		tlist.append(p)
	
	for t in tlist:
		t.start()
		
	for t in tlist:
		t.join()