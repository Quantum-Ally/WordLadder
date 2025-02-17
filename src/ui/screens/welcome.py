import pygame
from pygame.locals import *
from ..render import draw_button
from src.utils.config import load_config

__all__ = ['WelcomeScreen']

class WelcomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.config = load_config()
        self.buttons = []
        self.title_font = pygame.font.SysFont(
            self.config['fonts']['title'], 
            self.config['welcome']['title_size']
        )
        self.button_font = pygame.font.SysFont(
            self.config['fonts']['button'], 
            self.config['welcome']['button_size']
        )
        self.selected_button = None

    def draw(self):
        """Render all welcome screen elements"""
        self.screen.fill(self.config['colors']['background'])
        self._draw_title()
        self._draw_buttons()
        pygame.display.flip()

    def _draw_title(self):
        title_text = self.title_font.render(
            "Word Ladder Adventure", 
            True, 
            self.config['colors']['title']
        )
        title_rect = title_text.get_rect(
            center=(self.config['screen']['width']//2, 150)
        )
        self.screen.blit(title_text, title_rect)

    def _draw_buttons(self):
        button_specs = [
            {"text": "Easy Mode", "action": "easy", "color": (46, 204, 113)},
            {"text": "Advanced Mode", "action": "advanced", "color": (241, 196, 15)},
            {"text": "Challenge Mode", "action": "challenge", "color": (231, 76, 60)}
        ]
        
        self.buttons.clear()
        mouse_pos = pygame.mouse.get_pos()
        
        for idx, spec in enumerate(button_specs):
            # Calculate button position
            x = self.config['screen']['width']//2 - 150
            y = 300 + idx * 100
            
            # Check if mouse is hovering over button
            button_rect = pygame.Rect(x, y, 300, 70)
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Adjust color based on hover state
            color = spec['color']
            if is_hovered:
                # Brighten the color when hovered
                color = tuple(min(c + 30, 255) for c in color)
            
            btn = draw_button(
                self.screen,
                spec['text'],
                x, y,
                300, 70,
                self.button_font,
                color
            )
            self.buttons.append((btn, spec['action']))

    def handle_event(self, event):
        """Handle mouse clicks and return the selected action"""
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = event.pos
            for button, action in self.buttons:
                if button.collidepoint(mouse_pos):
                    return action
        return None