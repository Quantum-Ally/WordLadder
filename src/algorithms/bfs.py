from collections import deque
from typing import Dict, List, Set, Tuple

class BFSPathFinder:
	def __init__(self, graph_data: Dict):
		self.graph = graph_data["graph"]
		self.words = set(graph_data["words"])
		self.stats = {
			"nodes_explored": 0,
			"path_length": 0,
			"execution_time": 0
		}
	
	def find_path(self, start: str, target: str) -> Tuple[List[str], Dict]:
		"""
		Find shortest path using BFS
		Returns: (path, statistics)
		"""
		if start not in self.words or target not in self.words:
			return [], self.stats
			
		queue = deque([(start, [start])])
		visited = {start}
		self.stats["nodes_explored"] = 0
		
		while queue:
			current_word, path = queue.popleft()
			self.stats["nodes_explored"] += 1
			
			if current_word == target:
				self.stats["path_length"] = len(path) - 1
				return path, self.stats
			
			# Explore neighbors
			for next_word in self.graph[current_word]:
				if next_word not in visited:
					visited.add(next_word)
					new_path = path + [next_word]
					queue.append((next_word, new_path))
		
		return [], self.stats
	
	def get_next_step(self, current: str, target: str) -> str:
		"""Get next word in the path for hint system"""
		path, _ = self.find_path(current, target)
		return path[1] if len(path) > 1 else current