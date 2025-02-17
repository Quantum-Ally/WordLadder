import pygame
import json
import math
from typing import Dict, List, Set, Tuple
from ..render import draw_button, create_gradient_surface
from src.utils.config import load_config
from src.algorithms.astar import AStarPathFinder
from src.algorithms.ucs import UCSPathFinder

class MapScreen:
    def __init__(self, screen, start_word: str, end_word: str, current_word: str, mode: str):
        self.screen = screen
        self.config = load_config()
        self.start_word = start_word
        self.end_word = end_word
        self.current_word = current_word
        self.mode = mode
        
        # Load graph
        self.load_graph(len(start_word))
        
        # Initialize fonts
        self.title_font = pygame.font.SysFont(
            self.config['fonts']['title'],
            self.config['setup']['title_size']
        )
        self.text_font = pygame.font.SysFont(
            self.config['fonts']['text'],
            self.config['setup']['input_size']
        )
        
        # Algorithm selection
        self.algorithms = ['A*', 'UCS', 'BFS']
        self.selected_algo = 'A*'
        self.path_info = self.calculate_path(self.selected_algo)
        
        # Colors
        self.colors = {
            'background': (30, 30, 50),
            'node': (100, 100, 100),
            'start': (100, 255, 100),
            'end': (255, 100, 100),
            'current': (255, 255, 100),
            'path': (100, 200, 255),
            'explored': (150, 150, 150),
            'text': (255, 255, 255)
        }
        
        # Add graph view state
        self.show_full_graph = False
        
        # Add colors for different algorithm paths
        self.algo_colors = {
            'A*': (255, 100, 100),    # Red
            'UCS': (100, 255, 100),   # Green
            'BFS': (100, 100, 255)    # Blue
        }
    
    def load_graph(self, word_length: int):
        """Load word ladder graph"""
        with open(f"data/graphs/graph_{word_length}.json") as f:
            data = json.load(f)
            self.graph = data["graph"]
            self.words = set(data["words"])
    
    def calculate_path(self, algorithm: str) -> Dict:
        """Calculate path and stats using selected algorithm"""
        pathfinder = None
        
        if algorithm == 'A*':
            pathfinder = AStarPathFinder({"graph": self.graph, "words": self.words})
        elif algorithm == 'UCS':
            pathfinder = UCSPathFinder({"graph": self.graph, "words": self.words})
        elif algorithm == 'BFS':
            # Implement BFS pathfinder
            class BFSPathFinder:
                def __init__(self, graph_data):
                    self.graph = graph_data["graph"]
                    self.words = graph_data["words"]
                
                def find_path(self, start: str, end: str) -> Tuple[List[str], Dict]:
                    visited = {start}
                    queue = [(start, [start], 0)]
                    nodes_explored = 0
                    
                    while queue:
                        current, path, cost = queue.pop(0)
                        nodes_explored += 1
                        
                        if current == end:
                            return path, {
                                "nodes_explored": nodes_explored,
                                "path_length": len(path) - 1,
                                "total_cost": cost
                            }
                        
                        for next_word, edge_cost in self.graph[current].items():
                            if next_word not in visited:
                                visited.add(next_word)
                                queue.append((next_word, path + [next_word], cost + edge_cost))
                    
                    return [], {
                        "nodes_explored": nodes_explored,
                        "path_length": 0,
                        "total_cost": 0
                    }
            
            pathfinder = BFSPathFinder({"graph": self.graph, "words": self.words})
        
        if pathfinder is None:
            return {
                'path': [],
                'stats': {
                    'nodes_explored': 0,
                    'path_length': 0,
                    'total_cost': 0
                }
            }
        
        path, stats = pathfinder.find_path(self.start_word, self.end_word)
        return {
            'path': path,
            'stats': stats,
            'explored_nodes': stats['nodes_explored'],
            'path_length': stats['path_length'],
            'total_cost': stats['total_cost']
        }
    
    def draw(self):
        # Create background
        gradient = create_gradient_surface(
            self.config['screen']['width'],
            self.config['screen']['height'],
            self.colors['background'],
            (50, 50, 80)
        )
        self.screen.blit(gradient, (0, 0))
        
        # Draw algorithm selection buttons
        self.draw_algo_buttons()
        
        # Draw view toggle button
        self.draw_view_toggle()
        
        # Draw either path or full graph visualization
        if self.show_full_graph:
            self.draw_full_graph()
        else:
            self.draw_path_visualization()
        
        # Draw statistics
        self.draw_statistics()
        
        # Draw back button
        self.draw_back_button()
        
        pygame.display.flip()
    
    def draw_algo_buttons(self):
        button_width = 100
        spacing = 20
        total_width = len(self.algorithms) * button_width + (len(self.algorithms) - 1) * spacing
        start_x = (self.config['screen']['width'] - total_width) // 2
        
        self.algo_buttons = {}
        for i, algo in enumerate(self.algorithms):
            x = start_x + i * (button_width + spacing)
            button_rect = pygame.Rect(x, 50, button_width, 40)
            color = (100, 200, 255) if algo == self.selected_algo else (100, 100, 100)
            
            pygame.draw.rect(self.screen, color, button_rect)
            text = self.text_font.render(algo, True, (0, 0, 0))
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            self.algo_buttons[algo] = button_rect
    
    def draw_path_visualization(self):
        # Draw nodes and connections
        node_size = 40
        start_y = 150
        max_nodes_per_row = 8
        
        # Calculate positions for all words in path
        path = self.path_info['path']
        positions = {}
        
        for i, word in enumerate(path):
            row = i // max_nodes_per_row
            col = i % max_nodes_per_row
            x = 100 + col * (node_size + 60)
            y = start_y + row * (node_size + 40)
            positions[word] = (x, y)
            
            # Draw node
            color = self.colors['start'] if word == self.start_word else \
                   self.colors['end'] if word == self.end_word else \
                   self.colors['current'] if word == self.current_word else \
                   self.colors['path']
            
            pygame.draw.rect(self.screen, color, (x, y, node_size, node_size))
            text = self.text_font.render(word, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + node_size//2, y + node_size//2))
            self.screen.blit(text, text_rect)
            
            # Draw connection line to previous node
            if i > 0:
                prev_word = path[i-1]
                prev_x, prev_y = positions[prev_word]
                pygame.draw.line(self.screen, self.colors['path'],
                               (prev_x + node_size, prev_y + node_size//2),
                               (x, y + node_size//2), 2)
    
    def draw_statistics(self):
        stats = self.path_info['stats']
        y = self.config['screen']['height'] - 200
        
        stats_text = [
            f"Algorithm: {self.selected_algo}",
            f"Path Length: {stats['path_length']} steps",
            f"Total Cost: {stats['total_cost']:.2f}",
            f"Nodes Explored: {stats['nodes_explored']}"
        ]
        
        for i, text in enumerate(stats_text):
            surface = self.text_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (50, y + i * 30))
    
    def draw_back_button(self):
        back_text = self.text_font.render("Back to Game", True, (200, 100, 100))
        self.back_button = back_text.get_rect(center=(100, self.config['screen']['height'] - 50))
        self.screen.blit(back_text, self.back_button)
    
    def draw_view_toggle(self):
        text = "Show Full Graph" if not self.show_full_graph else "Show Path"
        toggle_text = self.text_font.render(text, True, (200, 200, 200))
        self.view_toggle_button = toggle_text.get_rect(
            center=(self.config['screen']['width'] - 100, 50)
        )
        self.screen.blit(toggle_text, self.view_toggle_button)
    
    def draw_full_graph(self):
        """Draw the complete word graph with all connections"""
        # Calculate node positions using circular layout
        nodes = list(self.words)
        node_positions = {}
        center_x = self.config['screen']['width'] // 2
        center_y = self.config['screen']['height'] // 2
        radius = min(center_x, center_y) - 100
        
        # Position nodes in a circle
        for i, word in enumerate(nodes):
            angle = (2 * math.pi * i) / len(nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node_positions[word] = (int(x), int(y))
        
        # Draw edges first (behind nodes)
        for word in self.graph:
            for neighbor in self.graph[word]:
                start_pos = node_positions[word]
                end_pos = node_positions[neighbor]
                pygame.draw.line(self.screen, (50, 50, 50), start_pos, end_pos, 1)
        
        # Calculate paths for all algorithms
        paths = {}
        for algo in self.algorithms:
            path_info = self.calculate_path(algo)
            paths[algo] = path_info['path']
        
        # Draw highlighted paths for each algorithm
        for algo, path in paths.items():
            if path:
                color = self.algo_colors[algo]
                for i in range(len(path) - 1):
                    start_pos = node_positions[path[i]]
                    end_pos = node_positions[path[i + 1]]
                    pygame.draw.line(self.screen, color, start_pos, end_pos, 3)
        
        # Draw nodes
        node_size = 30
        for word in nodes:
            x, y = node_positions[word]
            
            # Determine node color
            if word == self.start_word:
                color = self.colors['start']
            elif word == self.end_word:
                color = self.colors['end']
            elif word == self.current_word:
                color = self.colors['current']
            else:
                color = self.colors['node']
            
            # Draw node circle
            pygame.draw.circle(self.screen, color, (int(x), int(y)), node_size)
            
            # Draw word text
            text = self.text_font.render(word, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # Draw legend
        legend_y = 100
        for algo in self.algorithms:
            color = self.algo_colors[algo]
            text = self.text_font.render(f"{algo} path", True, color)
            self.screen.blit(text, (50, legend_y))
            legend_y += 30
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check view toggle button
            if hasattr(self, 'view_toggle_button') and self.view_toggle_button.collidepoint(mouse_pos):
                self.show_full_graph = not self.show_full_graph
                return None
            
            # Check algorithm buttons
            for algo, button in self.algo_buttons.items():
                if button.collidepoint(mouse_pos):
                    self.selected_algo = algo
                    self.path_info = self.calculate_path(algo)
                    return None
            
            # Check back button
            if self.back_button.collidepoint(mouse_pos):
                return {'action': 'back_to_game'}
        
        return None