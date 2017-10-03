from simulator.simulator import Simulator
from robot.robot import Robot
from arena.arena import Arena
from arena.arenautils import ArenaUtils
from algorithm.exploration import Exploration
from algorithm.fastestpath import FastestPath

def main():
	robot = Robot((18,1), False)
	# _real_map = Arena(robot)
	# ArenaUtils.load_arena_from_file(_real_map, 'map/SampleWeek11.txt')


	# _explore_map = Arena(robot)
	# _explore_map.set_allunexplored()
	# _explore = Exploration(_explore_map, _real_map, robot, 300, 3600)
	# _explore.run()
	# print(_explore_map.get_block((8,1)).is_virtualwall())
	# fp = FastestPath(_explore_map, robot, _real_map)
	# fp.do_fastest_path((18,1))

	simulator = Simulator()
	simulator.run_exploration(robot, 'map/SampleWeek11.txt')
	
if __name__ == "__main__":
	main()