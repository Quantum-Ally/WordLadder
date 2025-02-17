import pygame
import json
from ..render import draw_button, create_gradient_surface
from src.utils.config import load_config

class GameScreen:
	def __init__(self, screen, start_word, end_word, mode):
		self.screen = screen
		self.config = load_config()
		self.start_word = start_word
		self.end_word = end_word
		self.mode = mode
		self.current_word = start_word
		
		# Load appropriate graph based on word length
		word_length = len(start_word)
		self.load_graph(word_length)
		
		# Initialize fonts
		self.title_font = pygame.font.SysFont(
			self.config['fonts']['title'],
			self.config['setup']['title_size']
		)
		self.word_font = pygame.font.SysFont(
			self.config['fonts']['text'],
			self.config['setup']['input_size']
		)
		
		# Game state
		self.moves = []
		self.game_over = False
		
		# Input state
		self.selected_position = None
		self.letter_input = ""
		
		# Hint system initialization
		self.show_hint_options = False
		self.hint_position = None
		self.hint_letter = None
		self.hint_algo_buttons = {}
		self.hint_algorithms = ['A*', 'UCS', 'BFS']
		self.last_hint_algo = None
		
		# Colors for algorithms
		self.algo_colors = {
			'A*': (255, 100, 100),    # Red
			'UCS': (100, 255, 100),   # Green
			'BFS': (100, 100, 255)    # Blue
		}
		
		# Verify path exists
		if not self.verify_path():
			raise ValueError("No valid path exists between words")
	
	def load_graph(self, word_length):
		"""Load word ladder graph"""
		graph_file = f"data/graphs/graph_{word_length}.json"
		try:
			with open(graph_file) as f:
				graph_data = json.load(f)
				self.graph = graph_data["graph"]
				self.valid_words = set(graph_data["words"])
				print(f"Loaded graph with {len(self.valid_words)} words")
				print(f"Graph connections for {self.start_word}: {self.graph.get(self.start_word, {})}")
		except Exception as e:
			print(f"Error loading graph: {e}")
			raise
	
	def verify_path(self):
		"""Verify that a path exists between start and end words"""
		if self.start_word not in self.valid_words or self.end_word not in self.valid_words:
			return False
			
		# Simple BFS to verify path exists
		visited = {self.start_word}
		queue = [(self.start_word, [self.start_word])]
		
		while queue:
			current, path = queue.pop(0)
			if current == self.end_word:
				print(f"Found path: {path}")  # Debug print
				return True
				
			for next_word in self.graph.get(current, {}):
				if next_word not in visited:
					visited.add(next_word)
					queue.append((next_word, path + [next_word]))
		
		return False
	
	def draw(self):
		# Create background
		gradient = create_gradient_surface(
			self.config['screen']['width'],
			self.config['screen']['height'],
			(30, 30, 50),
			(50, 50, 80)
		)
		self.screen.blit(gradient, (0, 0))
		
		# Draw game elements
		self._draw_words()
		self._draw_moves()
		self._draw_letter_input()
		self._draw_controls()
		
		# Draw hint options if shown
		if self.show_hint_options:
			self._draw_hint_options()
		
		# Draw current hint if available
		if self.hint_position is not None and self.hint_letter is not None:
			hint_text = self.word_font.render(
				f"Hint: Change position {self.hint_position + 1} to '{self.hint_letter}'",
				True,
				(255, 200, 100)
			)
			hint_rect = hint_text.get_rect(
				center=(self.config['screen']['width']//2, 
					   self.config['screen']['height'] - 100)
			)
			self.screen.blit(hint_text, hint_rect)
		
		# Draw winner message if game is over
		if self.game_over:
			winner_text = self.title_font.render("You Won!", True, (255, 215, 0))
			text_rect = winner_text.get_rect(center=(
				self.config['screen']['width']//2,
				self.config['screen']['height']//2 + 100
			))
			self.screen.blit(winner_text, text_rect)
		
		pygame.display.flip()
	
	def _draw_words(self):
		# Draw current word with clickable letters
		word_x = self.config['screen']['width']//2 - (len(self.current_word) * 30)
		word_y = 200
		self.letter_rects = []  # Store letter positions for clicking
		
		for i, letter in enumerate(self.current_word):
			color = (255, 255, 100) if i == self.selected_position else (255, 255, 255)
			letter_surface = self.word_font.render(letter, True, color)
			letter_rect = letter_surface.get_rect(topleft=(word_x + i*60, word_y))
			self.screen.blit(letter_surface, letter_rect)
			self.letter_rects.append((letter_rect, i))
			
			# Draw box around letter
			pygame.draw.rect(self.screen, color, letter_rect.inflate(10, 10), 2)
		
		# Draw start and end words
		start = self.word_font.render(f"Start: {self.start_word}", True, (100, 255, 100))
		end = self.word_font.render(f"Target: {self.end_word}", True, (255, 100, 100))
		
		self.screen.blit(start, (50, 50))
		self.screen.blit(end, (50, 100))
	
	def _draw_letter_input(self):
		if self.selected_position is not None and not self.game_over:
			# Draw input box
			input_rect = pygame.Rect(
				self.config['screen']['width']//2 - 100,
				300,
				200,
				50
			)
			pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2)
			
			# Draw current input
			if self.letter_input:
				text = self.word_font.render(self.letter_input, True, (255, 255, 255))
				text_rect = text.get_rect(center=input_rect.center)
				self.screen.blit(text, text_rect)
			
			# Draw enter button if we have input
			if self.letter_input:
				self.enter_button = pygame.Rect(
					self.config['screen']['width']//2 - 50,
					370,
					100,
					40
				)
				pygame.draw.rect(self.screen, (100, 255, 100), self.enter_button)
				enter_text = self.word_font.render("Enter", True, (0, 0, 0))
				enter_rect = enter_text.get_rect(center=self.enter_button.center)
				self.screen.blit(enter_text, enter_rect)
	
	def _draw_moves(self):
		moves_text = f"Moves: {len(self.moves)}"
		moves = self.word_font.render(moves_text, True, (200, 200, 200))
		self.screen.blit(moves, (50, 150))
	
	def _draw_controls(self):
		"""Draw all control buttons"""
		# Draw back button
		back_text = self.word_font.render("Back", True, (200, 100, 100))
		self.back_button = back_text.get_rect(center=(100, self.config['screen']['height'] - 50))
		self.screen.blit(back_text, self.back_button)
		
		# Draw map button
		map_text = self.word_font.render("View Map", True, (100, 200, 255))
		self.map_button = map_text.get_rect(
			center=(self.config['screen']['width'] - 200, 
				   self.config['screen']['height'] - 50)
		)
		pygame.draw.rect(self.screen, (40, 40, 60), self.map_button.inflate(20, 10))
		self.screen.blit(map_text, self.map_button)
		
		# Draw hint button
		hint_text = self.word_font.render("Hint", True, (255, 200, 100))
		self.hint_button = hint_text.get_rect(
			center=(self.config['screen']['width'] - 100, 
				   self.config['screen']['height'] - 50)
		)
		pygame.draw.rect(self.screen, (40, 40, 60), self.hint_button.inflate(20, 10))
		self.screen.blit(hint_text, self.hint_button)
	
	def _draw_hint_options(self):
		"""Draw algorithm selection buttons for hint"""
		# Draw background panel for hint options
		panel_width = 140
		panel_height = len(self.hint_algorithms) * 40 + 20
		panel_x = self.config['screen']['width'] - 150
		panel_y = self.config['screen']['height'] - 200  # Position above the hint button
		
		# Draw panel background
		panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
		pygame.draw.rect(self.screen, (40, 40, 60), panel_rect)
		pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
		
		# Draw algorithm buttons
		self.hint_algo_buttons = {}  # Reset buttons dictionary
		button_width = 120
		button_height = 30
		
		for i, algo in enumerate(self.hint_algorithms):
			# Calculate button position
			button_x = panel_x + 10
			button_y = panel_y + 10 + (i * 40)
			
			# Create button rectangle
			button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
			
			# Draw button
			color = self.algo_colors.get(algo, (100, 100, 100))
			pygame.draw.rect(self.screen, color, button_rect)
			
			# Draw algorithm text
			text = self.word_font.render(algo, True, (255, 255, 255))
			text_rect = text.get_rect(center=button_rect.center)
			self.screen.blit(text, text_rect)
			
			# Store button rect for click detection
			self.hint_algo_buttons[algo] = button_rect
			
			# If this algorithm has been selected and there's a hint, show indicator
			if hasattr(self, 'last_hint_algo') and self.last_hint_algo == algo:
				pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2)
	
	def _try_word_change(self, new_word):
		"""Check if the new word is a valid move"""
		# Check if word exists and is connected in graph
		if new_word in self.valid_words and new_word in self.graph.get(self.current_word, {}):
			self.current_word = new_word
			self.moves.append(new_word)
			
			if new_word == self.end_word:
				self.game_over = True
				self.selected_position = None  # Clear selection when game is won
				self.letter_input = ""  # Clear input when game is won
			return True
		return False
	
	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_pos = event.pos
			
			# If game is over, any click returns to welcome screen
			if self.game_over:
				return {'action': 'back_to_welcome'}
			
			# Check map button
			if hasattr(self, 'map_button') and self.map_button.collidepoint(mouse_pos):
				return {
					'action': 'show_map',
					'start': self.start_word,
					'end': self.end_word,
					'mode': self.mode,
					'current_word': self.current_word
				}
			
			# Check hint button
			if hasattr(self, 'hint_button') and self.hint_button.collidepoint(mouse_pos):
				self.show_hint_options = not self.show_hint_options
				if not self.show_hint_options:  # If closing the hint menu
					self.hint_position = None
					self.hint_letter = None
				return None
			
			# Check hint algorithm selection
			if self.show_hint_options and hasattr(self, 'hint_algo_buttons'):
				for algo, button in self.hint_algo_buttons.items():
					if button.collidepoint(mouse_pos):
						hint_result = self.get_hint(algo)
						if hint_result:
							self.hint_position, self.hint_letter = hint_result
							self.last_hint_algo = algo
							self.show_hint_options = False
						return None
			
			# Check letter selection
			for rect, pos in getattr(self, 'letter_rects', []):
				if rect.collidepoint(mouse_pos):
					self.selected_position = pos
					self.letter_input = ""
					return None
			
			# Check back button
			if hasattr(self, 'back_button') and self.back_button.collidepoint(mouse_pos):
				return {'action': 'back_to_setup', 'mode': self.mode}
		
		# Handle keyboard input
		elif event.type == pygame.KEYDOWN and self.selected_position is not None and not self.game_over:
			if event.unicode.isalpha() and len(self.letter_input) < 1:
				self.letter_input = event.unicode.lower()
			elif event.key == pygame.K_RETURN and self.letter_input:
				new_word = (
					self.current_word[:self.selected_position] + 
					self.letter_input + 
					self.current_word[self.selected_position + 1:]
				)
				if self._try_word_change(new_word):
					self.selected_position = None
					self.letter_input = ""
		
		return None