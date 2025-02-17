import pygame
from pygame.locals import *
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.screens.game_setup_screen import GameSetupScreen
from src.ui.screens.welcome import WelcomeScreen
from src.ui.screens.game_screen import GameScreen
from src.ui.screens.map_screen import MapScreen
from src.utils.config import load_config

class Game:
    def __init__(self):
        pygame.init()
        self.config = load_config()
        self.screen = pygame.display.set_mode((
            self.config['screen']['width'],
            self.config['screen']['height']
        ))
        pygame.display.set_caption("Word Ladder")
        
        self.current_state = "welcome"
        self.welcome_screen = WelcomeScreen(self.screen)
        self.game_setup = None
        self.game_screen = None
        self.map_screen = None
        self.running = True

    def run(self):
        while self.running:
            self._handle_events()
            self._update_screen()
        
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if self.current_state == "welcome":
                mode = self.welcome_screen.handle_event(event)
                if mode:
                    self.game_setup = GameSetupScreen(self.screen, mode)
                    self.current_state = "setup"
            
            elif self.current_state == "setup" and self.game_setup:
                result = self.game_setup.handle_event(event)
                if result:
                    if result['action'] == 'back_to_welcome':
                        self.current_state = "welcome"
                        self.game_setup = None
                    elif result['action'] == 'start_game':
                        self.game_screen = GameScreen(
                            self.screen,
                            result['start'],
                            result['end'],
                            result['mode']
                        )
                        self.current_state = "playing"
                        self.game_setup = None
            
            elif self.current_state == "playing" and self.game_screen:
                result = self.game_screen.handle_event(event)
                if result:
                    if result['action'] == 'back_to_setup':
                        self.current_state = "setup"
                        self.game_screen = None
                        self.game_setup = GameSetupScreen(self.screen, result['mode'])
                    elif result['action'] == 'game_won':
                        self.current_state = "welcome"
                        self.game_screen = None
                    elif result['action'] == 'show_map':
                        print("Transitioning to map view")
                        self.map_screen = MapScreen(
                            self.screen,
                            result['start'],
                            result['end'],
                            result['current_word'],
                            result['mode']
                        )
                        self.current_state = "map_view"
            
            elif self.current_state == "map_view" and self.map_screen:
                result = self.map_screen.handle_event(event)
                if result and result['action'] == 'back_to_game':
                    print("Returning to game")
                    self.current_state = "playing"
                    self.map_screen = None

    def _update_screen(self):
        if self.current_state == "welcome":
            self.welcome_screen.draw()
        elif self.current_state == "setup":
            self.game_setup.draw()
        elif self.current_state == "playing" and self.game_screen:
            self.game_screen.draw()
        elif self.current_state == "map_view" and self.map_screen:
            self.map_screen.draw()
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()