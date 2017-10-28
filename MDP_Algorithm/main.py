import time,sys
from simulator.simulator import Simulator
from robot.robot import Robot
from arena.arena import Arena
from arena.arenautils import ArenaUtils
from arena.arenaconstant import ArenaConstant
from algorithm.exploration import Exploration
from algorithm.fastestpath import FastestPath
from comm.comm import CommMgr

def main():
	#command = input('Enter 1: Actual Run, 2: Fastest Path => ')

	CommMgr.connect()
	
	#if int(command) == 1:
	explore()
	#else:
	#	fp()

	command = input('Press ENTER to close connection.... ')
	if command == '':
		CommMgr.close()

def explore():
	robot = Robot((18,1), True)
	_explore_map = Arena(robot)
	_explore_map.set_allunexplored()
	_explore = Exploration(_explore_map, robot, 300, 3600)
	_explore.run()

def fp():
	robot = Robot((18,1), True)
	_real_map = Arena(robot)
	ArenaUtils.load_arena_from_file(_real_map, 'map/17_week9.txt')
	print('Awaiting FP_START')
	while True:
		_command = CommMgr.recv()
		if _command == 'FP_START':
			CommMgr.send('X', CommMgr.ARDUINO)
			break

	_go_to_wp_goal = FastestPath(_real_map, robot)
	_status = _go_to_wp_goal.do_fastest_path_wp_goal((8,9), ArenaConstant.GOAL_POS.value)
	
if __name__ == "__main__":
	main()