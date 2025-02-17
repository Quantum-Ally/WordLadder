import heapq
from typing import Dict, List, Set, Tuple

class AStarPathFinder:
	def __init__(self, graph_data: Dict):
		self.graph = graph_data["graph"]
		self.words = set(graph_data["words"])
		self.stats = {
			"nodes_explored": 0,
			"path_length": 0,
			"total_cost": 0,
			"execution_time": 0
		}
	
	def hamming_distance(self, word1: str, word2: str) -> int:
		"""Calculate Hamming distance (number of differing positions)"""
		return sum(1 for a, b in zip(word1, word2) if a != b)
	
	def find_path(self, start: str, target: str) -> Tuple[List[str], Dict]:
		"""
		Find shortest path using A* with Hamming distance heuristic
		f(n) = g(n) + h(n) where:
		g(n) = path cost to reach node
		h(n) = Hamming distance to target (admissible heuristic)
		"""
		if start not in self.words or target not in self.words:
			return [], self.stats
			
		# Priority queue entries are (f_score, g_score, word, path)
		# f_score = g_score + h_score (Hamming distance)
		start_h = self.hamming_distance(start, target)
		frontier = [(start_h, 0, start, [start])]  # Initial f_score is just h_score
		visited = {start: 0}  # word -> g_score
		self.stats["nodes_explored"] = 0
		
		while frontier:
			f_score, g_score, current_word, path = heapq.heappop(frontier)
			self.stats["nodes_explored"] += 1
			
			if current_word == target:
				self.stats["path_length"] = len(path) - 1
				self.stats["total_cost"] = g_score
				return path, self.stats
			
			# Skip if we've found a better path
			if current_word in visited and g_score > visited[current_word]:
				continue
			
			# Explore neighbors
			for next_word, edge_cost in self.graph[current_word].items():
				new_g_score = g_score + edge_cost
				
				if next_word not in visited or new_g_score < visited[next_word]:
					visited[next_word] = new_g_score
					h_score = self.hamming_distance(next_word, target)
					f_score = new_g_score + h_score  # f(n) = g(n) + h(n)
					heapq.heappush(frontier, (f_score, new_g_score, next_word, path + [next_word]))
		
		return [], self.stats
	
	def get_next_step(self, current: str, target: str) -> str:
		"""Get next word in the path for hint system"""
		path, _ = self.find_path(current, target)
		return path[1] if len(path) > 1 else current