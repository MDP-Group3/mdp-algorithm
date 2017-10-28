import time
from comm.comm import CommMgr
from robot.robotconstant import Action

def main():
	CommMgr.connect()
	while True:
		if CommMgr.recv() == 'EX_START':
			CommMgr.send(Action.FORWARD.value, CommMgr.ANDROID)
			time.sleep(1)
			CommMgr.send(Action.LEFT.value, CommMgr.ANDROID)
	CommMgr.close()

if __name__ == "__main__":
	main()