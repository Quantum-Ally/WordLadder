import os
import json
import pygame
from pygame.locals import *
import math
import random
import time
from ..render import draw_button, draw_input_box, create_gradient_surface
from src.utils.config import load_config
from src.scripts.build_graph import build_graph

class GameSetupScreen:
    def __init__(self, screen, selected_mode):
        # Initialize core components
        self.screen = screen
        self.config = load_config()
        self.selected_mode = selected_mode
        
        # Start graph loading immediately
        self.is_loading = True
        self.loading_start_time = pygame.time.get_ticks()
        self.loading_message = "Loading word database..."
        self.word_graphs = {"words": set(), "graph": {}}
        self._load_word_graphs()
        
        # Initialize UI elements
        self.buttons = []
        self.particles = []  # Initialize empty particles list
        
        # Add error message handling
        self.error_message = ""
        self.error_timer = 0
        self.error_duration = 3000  # 3 seconds in milliseconds



        # Enable antialiasing for better text rendering
        pygame.font.init()
        
        # Add mode-specific colors
        self.mode_colors = {
            'easy': (46, 204, 113),      # Green
            'advanced': (241, 196, 15),   # Yellow
            'challenge': (231, 76, 60)    # Red
        }
        # Set current color based on mode
        self.current_color = self.mode_colors.get(self.selected_mode, (100, 100, 100))
        
        # Increase font sizes for better resolution
        title_size = int(self.config['setup']['title_size'] * 1.5)  # 50% larger
        input_size = int(self.config['setup']['input_size'] * 1.2)  # 20% larger
        
        # Initialize fonts with antialiasing
        self.title_font = pygame.font.SysFont(
            self.config['fonts']['title'],
            title_size
        )
        self.input_font = pygame.font.SysFont(
            self.config['fonts']['text'],
            input_size
        )
        
        # Input boxes for start and end words
        self.start_word = ""
        self.end_word = ""
        self.active_input = None
        
        # Create input box rects with increased sizes
        width = 400  # Increased from 300
        height = 60  # Increased from 50
        center_x = self.config['screen']['width'] // 2
        self.start_box = pygame.Rect(center_x - width//2, 250, width, height)
        self.end_box = pygame.Rect(center_x - width//2, 350, width, height)
        
        # Add gradient colors based on mode
        self.gradient_colors = {
            'easy': [(20, 40, 20), (40, 80, 40)],      # Green gradient
            'advanced': [(40, 40, 20), (80, 80, 40)],  # Yellow gradient
            'challenge': [(40, 20, 20), (80, 40, 40)]  # Red gradient
        }
        
        # Interactive button effects
        self.button_pulse = 0
        self.pulse_direction = 1
        
        # Add shimmer effect
        self.shimmer_pos = 0
        self.shimmer_speed = 0.5  # Reduced shimmer speed
        self.animation_time = 0
        
        # Buttons
        self.start_button = None
        self.back_button = None

    def draw(self):
        if self.is_loading:
            self._draw_loading_screen()
            return
            
        # Update animation time with slower rate
        self.animation_time += 0.01
        
        # Draw error message if exists
        if self.error_message and pygame.time.get_ticks() - self.error_timer < self.error_duration:
            self._draw_error_message()
        
        # Create dynamic gradient background based on mode
        base_colors = self.gradient_colors.get(
            self.selected_mode, 
            [(20, 20, 40), (40, 40, 80)]
        )
        
        # Add slight color variation over time
        color_shift = int(math.sin(self.animation_time) * 10)
        gradient_start = tuple(min(max(c + color_shift, 0), 255) for c in base_colors[0])
        gradient_end = tuple(min(max(c + color_shift, 0), 255) for c in base_colors[1])
        
        gradient = create_gradient_surface(
            self.config['screen']['width'],
            self.config['screen']['height'],
            gradient_start,
            gradient_end
        )
        self.screen.blit(gradient, (0, 0))

        # Update shimmer effect
        self.shimmer_pos = (self.shimmer_pos + self.shimmer_speed) % (self.config['screen']['width'] * 2)
        
        # Draw shimmer line with current color
        shimmer_points = []
        for i in range(self.config['screen']['width']):
            x = i
            y = int(math.sin((i + self.shimmer_pos) * 0.02) * 5) + 200
            shimmer_points.append((x, y))
        
        if len(shimmer_points) > 1:
            pygame.draw.lines(
                self.screen,
                (*self.current_color, 30),  # Use current_color with alpha
                False,
                shimmer_points,
                2
            )

        self._draw_background_effects()
        self._draw_title()
        self._draw_mode_indicator()
        self._draw_inputs()
        self._draw_buttons()
        self._draw_instructions()
        pygame.display.flip()

    def _draw_background_effects(self):
        # Update and draw particles with trails
        self._update_particles()
        for particle in self.particles:
            # Draw particle trail
            trail_length = 5
            for i in range(trail_length):
                alpha = int(50 * (1 - i/trail_length))
                size = max(1, particle['size'] - i)
                pos = (
                    int(particle['x'] - i * math.cos(self.animation_time) * particle['speed']),
                    int(particle['y'] - i * math.sin(self.animation_time) * particle['speed'])
                )
                pygame.draw.circle(
                    self.screen,
                    (*self.current_color[:3], alpha),
                    pos,
                    size
                )

    def _update_particles(self):
        # Maximum number of particles with increased count
        MAX_PARTICLES = 75  # Increased from 50
        
        # Create new particles if needed
        while len(self.particles) < MAX_PARTICLES:
            self.particles.append({
                'x': random.randint(0, self.config['screen']['width']),
                'y': random.randint(0, self.config['screen']['height']),
                'size': random.randint(3, 6),  # Increased size range
                'speed': random.uniform(0.2, 0.8)  # Reduced particle speed
            })
        
        # Update existing particles
        for particle in self.particles:
            particle['y'] += particle['speed']
            particle['x'] += math.sin(self.animation_time) * (particle['speed'] * 0.5)  # Reduced x movement
            
            # Reset particles that go off screen
            if particle['y'] > self.config['screen']['height']:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.config['screen']['width'])

    def _draw_buttons(self):
        # Update pulse effect
        self.button_pulse += 0.1 * self.pulse_direction
        if self.button_pulse > 1 or self.button_pulse < 0:
            self.pulse_direction *= -1
        
        # Draw Start button if both inputs have text
        if len(self.start_word) > 0 and len(self.end_word) > 0:
            center_x = self.config['screen']['width'] // 2
            button_width = 220
            button_height = 60
            
            button_rect = pygame.Rect(
                center_x - button_width//2,
                450,
                button_width,
                button_height
            )
            
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Create dynamic button colors
            base_color = self.current_color
            hover_color = tuple(min(c + 40, 255) for c in base_color)
            current_color = hover_color if is_hovered else base_color
            
            # Draw multiple layers for 3D effect
            for i in range(4, 0, -1):
                offset_rect = button_rect.copy()
                offset_rect.y += i * 2
                pygame.draw.rect(
                    self.screen,
                    tuple(max(0, c - 20 * i) for c in current_color),
                    offset_rect,
                    border_radius=15
                )
            
            # Draw main button
            pygame.draw.rect(
                self.screen,
                current_color,
                button_rect,
                border_radius=15
            )
            
            # Add gradient overlay
            gradient_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            for i in range(button_height):
                alpha = int(100 * (1 - i/button_height))
                pygame.draw.line(
                    gradient_surface,
                    (255, 255, 255, alpha),
                    (0, i),
                    (button_width, i)
                )
            gradient_surface = pygame.transform.scale(gradient_surface, (button_width, button_height))
            
            # Apply gradient with rounded corners
            pygame.draw.rect(
                gradient_surface,
                (0, 0, 0, 0),
                gradient_surface.get_rect(),
                border_radius=15
            )
            self.screen.blit(gradient_surface, button_rect)
            
            # Draw text with shadow
            text = "Start Game"
            shadow_surface = self.input_font.render(text, True, (0, 0, 0))
            text_surface = self.input_font.render(text, True, (255, 255, 255))
            
            # Add bounce effect when hovered
            text_y_offset = math.sin(self.animation_time * 5) * 2 if is_hovered else 0
            
            text_rect = text_surface.get_rect(center=button_rect.center)
            shadow_rect = shadow_surface.get_rect(
                center=(button_rect.centerx + 2, button_rect.centery + 2 + text_y_offset)
            )
            
            self.screen.blit(shadow_surface, shadow_rect)
            self.screen.blit(text_surface, text_rect)
            
            self.start_button = button_rect
        else:
            self.start_button = None

        # Simplified Back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        mouse_pos = pygame.mouse.get_pos()
        is_back_hovered = back_rect.collidepoint(mouse_pos)
        
        # Simple back button with basic hover effect
        back_color = (100, 100, 100) if is_back_hovered else (80, 80, 80)
        
        # Draw main back button
        pygame.draw.rect(
            self.screen,
            back_color,
            back_rect,
            border_radius=5
        )
        
        # Simple text without effects
        text = "Back"
        text_surface = self.input_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=back_rect.center)
        self.screen.blit(text_surface, text_rect)
        self.back_button = back_rect


    def _draw_title(self):
        title = "Word Ladder Setup"
        # Enable antialiasing for title
        title_surface = self.title_font.render(title, True, (255, 255, 255))
        # Add subtle shadow for better visibility
        shadow_surface = self.title_font.render(title, True, (0, 0, 0))
        
        title_rect = title_surface.get_rect(center=(self.config['screen']['width'] // 2, 100))
        shadow_rect = shadow_surface.get_rect(center=(self.config['screen']['width'] // 2 + 2, 102))
        
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_surface, title_rect)

    def _draw_mode_indicator(self):
        mode_text = f"Mode: {self.selected_mode.title()}"
        # Enable antialiasing for mode indicator
        mode_surface = self.input_font.render(mode_text, True, self.current_color)
        shadow_surface = self.input_font.render(mode_text, True, (0, 0, 0))
        
        mode_rect = mode_surface.get_rect(center=(self.config['screen']['width'] // 2, 170))
        shadow_rect = shadow_surface.get_rect(center=(self.config['screen']['width'] // 2 + 1, 171))
        
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(mode_surface, mode_rect)

    def _draw_inputs(self):
        # Draw start word input
        draw_input_box(
            self.screen,
            self.start_box,
            self.start_word,
            self.input_font,
            self.current_color if self.active_input == 'start' else (100, 100, 100)
        )
        
        # Draw end word input
        draw_input_box(
            self.screen,
            self.end_box,
            self.end_word,
            self.input_font,
            self.current_color if self.active_input == 'end' else (100, 100, 100)
        )

    def _draw_instructions(self):
        instructions = "Enter start and end words to begin"
        # Enable antialiasing for instructions
        inst_surface = self.input_font.render(instructions, True, (200, 200, 200))
        shadow_surface = self.input_font.render(instructions, True, (0, 0, 0))
        
        inst_rect = inst_surface.get_rect(center=(self.config['screen']['width'] // 2, 520))
        shadow_rect = shadow_surface.get_rect(center=(self.config['screen']['width'] // 2 + 1, 521))
        
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(inst_surface, inst_rect)

    def _draw_error_message(self):
        error_surface = self.input_font.render(self.error_message, True, (255, 100, 100))
        error_rect = error_surface.get_rect(center=(self.config['screen']['width'] // 2, 580))
        self.screen.blit(error_surface, error_rect)

    def _draw_loading_screen(self):
        """Draw loading screen with animation"""
        # Fill background
        self.screen.fill((30, 30, 40))
        
        # Calculate loading animation
        current_time = pygame.time.get_ticks()
        animation_time = (current_time - self.loading_start_time) / 1000.0
        
        # Draw spinning circle
        center = (self.config['screen']['width'] // 2, self.config['screen']['height'] // 2)
        radius = 30
        points = 8
        for i in range(points):
            angle = animation_time * 5 + (i * (360 / points))
            x = center[0] + radius * math.cos(math.radians(angle))
            y = center[1] + radius * math.sin(math.radians(angle))
            alpha = int(255 * (1 - (i / points)))
            pygame.draw.circle(self.screen, (*self.current_color[:3], alpha), (int(x), int(y)), 5)
        
        # Draw loading text
        text_surface = self.input_font.render(self.loading_message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(center[0], center[1] + 50))
        self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()

    def handle_event(self, event):
        # Don't handle events while loading
        if self.is_loading:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle input box selection
            if self.start_box.collidepoint(event.pos):
                self.active_input = 'start'
            elif self.end_box.collidepoint(event.pos):
                self.active_input = 'end'
            else:
                self.active_input = None
                
            # Handle button clicks
            if self.start_button and self.start_button.collidepoint(event.pos):
                return self._validate_and_start_game()
            elif self.back_button and self.back_button.collidepoint(event.pos):
                return {'action': 'back_to_welcome'}
        
        elif event.type == pygame.KEYDOWN:
            if self.active_input:
                if event.key == pygame.K_RETURN:
                    self.active_input = None
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_input == 'start':
                        self.start_word = self.start_word[:-1]
                    else:
                        self.end_word = self.end_word[:-1]
                else:
                    if event.unicode.isalpha():
                        # Check word length based on mode
                        max_length = 3 if self.selected_mode == 'easy' else 5
                        if self.active_input == 'start' and len(self.start_word) < max_length:
                            self.start_word = (self.start_word + event.unicode).lower()
                        elif self.active_input == 'end' and len(self.end_word) < max_length:
                            self.end_word = (self.end_word + event.unicode).lower()
        
        return None

    def _load_word_graphs(self):
        """Load or build word graphs based on mode"""
        word_length = 3 if self.selected_mode == 'easy' else 5
        graph_file = f"data/graphs/graph_{word_length}.json"
        
        try:
            # Ensure directories exist
            os.makedirs("data/graphs", exist_ok=True)
            os.makedirs("data/dictionaries", exist_ok=True)
            
            # Check if dictionary file exists
            dict_file = f"data/dictionaries/{word_length}_letter.txt"
            if not os.path.exists(dict_file):
                self.loading_message = f"Error: Missing dictionary file {dict_file}"
                self.error_message = "Missing required dictionary files"
                self.error_timer = pygame.time.get_ticks()
                self.is_loading = False
                return False
            
            # Build graph if it doesn't exist
            if not os.path.exists(graph_file):
                self.loading_message = f"Building {word_length}-letter word graph..."
                pygame.display.flip()
                
                # Import and run build_graph
                from src.scripts.build_graph import build_graph
                success = build_graph(word_length)
                
                if not success:
                    self.loading_message = "Failed to build word graph"
                    self.error_message = "Failed to build word database"
                    self.error_timer = pygame.time.get_ticks()
                    self.is_loading = False
                    return False
            
            # Load the graph
            with open(graph_file, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
                self.word_graphs = {
                    "words": set(graph_data["words"]),
                    "graph": graph_data["graph"]
                }
            
            # Ensure minimum loading time for better UX
            elapsed_time = pygame.time.get_ticks() - self.loading_start_time
            if elapsed_time < 1000:  # 1 second minimum
                pygame.time.wait(1000 - elapsed_time)
            
            self.is_loading = False
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            self.error_message = "Error loading word database"
            self.error_timer = pygame.time.get_ticks()
            self.is_loading = False
            return False
        except Exception as e:
            print(f"Error loading graph: {str(e)}")
            self.error_message = "Error loading word database"
            self.error_timer = pygame.time.get_ticks()
            self.is_loading = False
            return False

    def _validate_and_start_game(self):
        """Validate words and start game if valid"""
        # Add debug prints
        print(f"Validating game start:")
        print(f"Start word: {self.start_word}")
        print(f"End word: {self.end_word}")
        print(f"Mode: {self.selected_mode}")
        print(f"Word set size: {len(self.word_graphs['words'])}")
        
        # Check word lengths
        required_length = 3 if self.selected_mode == 'easy' else 5
        
        if len(self.start_word) != required_length:
            self.error_message = f"Start word must be {required_length} letters"
            self.error_timer = pygame.time.get_ticks()
            return None
            
        if len(self.end_word) != required_length:
            self.error_message = f"End word must be {required_length} letters"
            self.error_timer = pygame.time.get_ticks()
            return None

        # Check if words exist in dictionary
        if self.start_word not in self.word_graphs["words"]:
            print(f"Start word '{self.start_word}' not in word set")
            self.error_message = f"'{self.start_word}' is not a valid word"
            self.error_timer = pygame.time.get_ticks()
            return None
        
        if self.end_word not in self.word_graphs["words"]:
            print(f"End word '{self.end_word}' not in word set")
            self.error_message = f"'{self.end_word}' is not a valid word"
            self.error_timer = pygame.time.get_ticks()
            return None

        # Check if path exists
        print("Checking path existence...")
        if not self._check_path_exists():
            print(f"No path found between {self.start_word} and {self.end_word}")
            self.error_message = "No valid path exists between these words"
            self.error_timer = pygame.time.get_ticks()
            return None

        print("All validations passed, starting game")
        # All validations passed, start the game
        return {
            'action': 'start_game',
            'start': self.start_word,
            'end': self.end_word,
            'mode': self.selected_mode
        }

    def _check_path_exists(self):
        """Check if a path exists between start and end words"""
        # Simple BFS to check path existence
        visited = {self.start_word}
        queue = [self.start_word]
        
        while queue:
            current = queue.pop(0)
            if current == self.end_word:
                return True
            
            # Generate all possible one-letter changes
            for i in range(len(current)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    next_word = current[:i] + c + current[i+1:]
                    if (next_word in self.word_graphs["words"] and 
                        next_word not in visited):
                        visited.add(next_word)
                        queue.append(next_word)
        
        return False
