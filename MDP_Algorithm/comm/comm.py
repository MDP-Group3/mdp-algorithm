import socket, time, sys

class CommMgr:
	_socket = None
	ANDROID = 'T'
	ARDUINO = 'A'
	_reconnect_count = 0
	_reconnect_limit = 5

	@staticmethod
	def connect(ip_addr='192.168.3.1', port=1818):
		try:
			print('Connecting to {}:{} ......'.format(ip_addr, port))
			CommMgr._socket = socket.socket()
			CommMgr._socket.connect((ip_addr, port))
			print('Connection to {}:{} Established!'.format(ip_addr, port))
			CommMgr._reconnect_count = 0
		except Exception as ex:
			if CommMgr._reconnect_count != CommMgr._reconnect_limit:
				print(ex)
				print('Reconnect Count: {}'.format(CommMgr._reconnect_count))
				print('No Connection, Attempting to reconnect {}:{} ......'.format(ip_addr, port))
				CommMgr._reconnect_count += 1
				CommMgr.close()
				time.sleep(1)
				CommMgr.connect()
			else:
				print('Unable to connect for {} times! Terminating Program'.format(CommMgr._reconnect_limit))
				CommMgr.close()
				sys.exit()

	@staticmethod
	def recv():
		try:
			if CommMgr._socket is not None :
				print('Awaiting Message ......')
				return CommMgr._socket.recv(1024).decode()
		except:
			print('Connection Lost!')
			CommMgr.close()
			CommMgr.connect()

	@staticmethod
	def send(msg, endpoint):
		try:
			if CommMgr._socket is not None:
				if endpoint == CommMgr.ANDROID:
					msg = CommMgr.ANDROID + msg
					print('Sending \'{}\' to {}'.format(msg, 'Android'))
				elif endpoint == CommMgr.ARDUINO:
					msg = CommMgr.ARDUINO + msg
					print('Sending \'{}\' to {}'.format(msg, 'Arduino'))
				else:
					print('Unknown Sender Location')
					return

				CommMgr._socket.send(msg.encode())
		except:
			print('Connection Lost!')
			CommMgr.close()
			CommMgr.connect()

	@staticmethod
	def close():
		if CommMgr._socket is not None:
			CommMgr._socket.close()
			CommMgr._socket = None