from enum import Enum

class ArenaConstant(Enum):
	ARENA_SIZE = 300 # Total number of blocks
	ARENA_ROW = 20 # Total number of rows
	ARENA_COL = 15 # Total number of cols
	GOAL_POS = (1, 13) # Center Position of Goal Area -> (row, col)

	EXPLORED = 1
	UNEXPLORED = 0

	OBSTACLE = 1
	CLEARED = 0
	UNKNOWN = 2

	C_START = (0,100,0)
	C_GOAL = (255,140,0)
	C_UNEXPLORED = (169,169,169)
	C_OBSTACLE = (0,0,0)
	C_CLEARED = (255,255,255)
	C_WAYPOINT = (255,0,0)

	BLOCK_SIZE = 30 # Block Size in Simulator (pixels)