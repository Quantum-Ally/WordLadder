import heapq
from typing import Dict, List, Set, Tuple

class UCSPathFinder:
	def __init__(self, graph_data: Dict):
		self.graph = graph_data["graph"]
		self.words = set(graph_data["words"])
		self.stats = {
			"nodes_explored": 0,
			"path_length": 0,
			"total_cost": 0,
			"execution_time": 0
		}
	
	def find_path(self, start: str, target: str) -> Tuple[List[str], Dict]:
		"""
		Find shortest path using UCS - expands node with lowest path cost g(n)
		Returns: (path, statistics)
		"""
		if start not in self.words or target not in self.words:
			return [], self.stats
			
		# Priority queue entries are (total_cost, word, path)
		frontier = [(0, start, [start])]
		visited = {start: 0}  # word -> total_cost to reach this word
		self.stats["nodes_explored"] = 0
		
		while frontier:
			current_cost, current_word, path = heapq.heappop(frontier)
			self.stats["nodes_explored"] += 1
			
			# Found target
			if current_word == target:
				self.stats["path_length"] = len(path) - 1
				self.stats["total_cost"] = current_cost
				return path, self.stats
			
			# Skip if we've found a better path to current_word
			if current_word in visited and current_cost > visited[current_word]:
				continue
			
			# Explore neighbors based on edge costs
			for next_word, edge_cost in self.graph[current_word].items():
				new_cost = current_cost + edge_cost
				
				# Only add to frontier if it's a better path
				if next_word not in visited or new_cost < visited[next_word]:
					visited[next_word] = new_cost
					heapq.heappush(frontier, (new_cost, next_word, path + [next_word]))
		
		return [], self.stats
	
	def get_next_step(self, current: str, target: str) -> str:
		"""Get next word in the path for hint system"""
		path, _ = self.find_path(current, target)
		return path[1] if len(path) > 1 else current