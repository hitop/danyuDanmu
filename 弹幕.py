#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket,re,time,random,sys
import threading,json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QTextEdit

class douYuTVDanmu(object):
	def __init__(self,roomid,dmShow=0):
		if dmShow != 0: #是否启用弹幕窗口
			dmShow.show() 

		self.dmShow = dmShow
		self.threadsFlag = 1
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.codeLocalToServer = 689
		self.serverToLocal = 690
		self.gid = -9999
		self.rid = roomid
		self.danmuCi = []
		self.connectToDanMuServer()
		threading.Thread(target=douYuTVDanmu.danmuWhile,args=(self,)).start()
		# self.terminateTread()
		
	def printStr(self,str):
		print(str)
		# now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		# res = now_time + '\t' + str
		# with open('log.txt','a',encoding='utf-8')as f:
			# f.writelines(log + '\n')
		# print(res)

	def sendMsg(self,msg):
			msg = msg.encode('utf-8')
			data_length= len(msg)+8
			msgHead=int.to_bytes(data_length,4,'little')+int.to_bytes(data_length,4,'little')+int.to_bytes(self.codeLocalToServer,4,'little')
			self.sock.send(msgHead)
			self.sock.sendall(msg)

	def keeplive(self):
		while True:
			if self.threadsFlag == 0:
				break
			msg='type@=mrkl/\x00'
			# msg='type@=keeplive/tick@='+str(int(time.time()))+'/\x00'
			self.sendMsg(msg)
			time.sleep(30)

	def connectToDanMuServer(self):
		HOST = 'openbarrage.douyutv.com'
		PORT = 8601
		self.sock.connect((HOST, PORT))

		msg = 'type@=loginreq/username@=/password@=/roomid@='+str(self.rid)+'/\x00'
		self.sendMsg(msg)
		data = self.sock.recv(1024)

		a = re.search(b'type@=(\w*)', data)
		if a.group(1)!=b'loginres':
			self.printStr("登录失败,程序退出...")
			exit(0)
		self.printStr("登录成功")

		msg = 'type@=joingroup/rid@='+str(self.rid)+'/gid@=-9999/\x00'
		self.sendMsg(msg)
		# self.printStr("进入弹幕服务器...")
		threading.Thread(target=douYuTVDanmu.keeplive,args=(self,)).start()
		# self.printStr("心跳包机制启动...")
		# data = self.sock.recv(1024)
		# print('Received', repr(data))

	def danmuWhile(self):
		# self.printStr("监听中")
		nnandtxtRe = re.compile(b'/nn@=(.[^/]*?)/txt@=(.[^/]*?)/')
		while True:
			if self.threadsFlag == 0:
				break
			data = self.sock.recv(1024)
			a = re.search(b'type@=(\w*)', data)
			if a:
				if a.group(1)==b'chatmsg':
					danmu_more = nnandtxtRe.findall(data)
					for i in range(0, len(danmu_more)):
						try:
							self.danmuCi.append(danmu_more[i][1].decode('utf-8'))
							if self.dmShow == 0:
								self.printStr('[{}] : {}'.format(danmu_more[i][0].decode('utf-8'),danmu_more[i][1].decode('utf-8')))
							else:
								self.dmShow.showTxt('[{}] : {}'.format(danmu_more[i][0].decode('utf-8'),danmu_more[i][1].decode('utf-8')))
						except BaseException as e:
							# self.printStr("\t__解析弹幕信息失败:")
							continue
		# print(self.danmuCi)

	def terminateTread(self,n=16):
		print("开始终止。。。。 ",n," 秒合倒计时")
		for i in range(0,n):
			time.sleep(1)
			print(n-i)
		self.threadsFlag = 0

		print("终止完成")


class DanmuWin(QWidget):
	"""弹幕显示窗口"""
	def __init__(self):
		super().__init__()
		self.initUI()
		
	def initUI(self):
		self.desktop = QApplication.desktop()
		self.winWidth = 640
		self.winHeight = 150
		self.leftPadding = 10
		self.labelHeight = 50
		self.setGeometry(10, 10, self.winWidth, self.winHeight)
		self.setWindowTitle("弹幕显示窗口")
		self.setWindowIcon(QIcon("ico.png"))
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint) #Qt.FramelessWindowHint|
		self.setAttribute(Qt.WA_TranslucentBackground)
		# self.setWindowOpacity(0.5)

		self.dmText = QLabel("弹幕显示窗口",self)
		self.dmText.setGeometry(self.leftPadding, 20, self.winWidth-self.leftPadding*2, self.labelHeight*3)
		self.dmText.setWordWrap(True)
		self.dmText.setAlignment(Qt.AlignTop)
		self.dmText.setStyleSheet("QLabel{background:transparent;color:red;font-size:30px;font-weight:bold;font-family:'Microsoft YaHei';}")

		# self.show()

	def showTxt(self,txt):
		self.dmText.setText(txt)
		# threading.Thread(target=self.dmText.setText,args=(txt))
		# self.dmText.textChanged(txt)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	dmtxt = DanmuWin()

	$roomid = "67673" #房间号
	# danmu = douYuTVDanmu($roomid)  #不带显示窗口
	danmu = douYuTVDanmu($roomid,dmtxt)  #屏幕左上角显示弹幕

	sys.exit(app.exec_())