def handle_welcome_input(buttons, mouse_pos):
    """Handles button clicks on the welcome screen."""
    from ..core.game import GameState  # Import your game state class
    
    for idx, btn in enumerate(buttons):
        if btn.collidepoint(mouse_pos):
            if idx == 0:  # Start Game
                return GameState.PLAYING
            elif idx == 1:  # Options
                return GameState.OPTIONS
            elif idx == 2:  # Quit
                return GameState.QUIT
    return GameState.WELCOME