import pygame
from pygame.locals import *

def create_gradient_surface(width, height, color1, color2):
    """Create a vertical gradient surface between two colors"""
    gradient = pygame.Surface((width, height))
    for y in range(height):
        # Calculate color for current line
        ratio = y / height
        color = [
            color1[i] + (color2[i] - color1[i]) * ratio
            for i in range(3)
        ]
        # Draw the line with calculated color
        pygame.draw.line(gradient, color, (0, y), (width, y))
    return gradient

def draw_button(screen, text, x, y, width, height, font, color, border_radius=10):
    """Draw a button with shadow, rounded corners, and hover effects"""
    button_rect = pygame.Rect(x, y, width, height)
    
    # Draw shadow
    shadow_rect = button_rect.copy()
    shadow_rect.y += 3
    pygame.draw.rect(
        screen,
        (0, 0, 0, 100),
        shadow_rect,
        border_radius=border_radius
    )
    
    # Draw main button
    pygame.draw.rect(
        screen,
        color,
        button_rect,
        border_radius=border_radius
    )
    
    # Add highlight effect at top
    # highlight_rect = pygame.Rect(x, y, width, height//2)
    # pygame.draw.rect(
    #     screen,
    #     (255, 255, 255, 30),
    #     highlight_rect,
    #     border_radius=border_radius
    # )
    
    # Draw text with shadow
    text_shadow = font.render(text, True, (0, 0, 0))
    text_main = font.render(text, True, (255, 255, 255))
    
    # Center text
    text_rect = text_main.get_rect(center=button_rect.center)
    shadow_rect = text_shadow.get_rect(
        center=(button_rect.centerx + 1, button_rect.centery + 1)
    )
    
    screen.blit(text_shadow, shadow_rect)
    screen.blit(text_main, text_rect)
    
    return button_rect

def draw_input_box(screen, rect, text, font, color, border_radius=10):
    """Draw an input box with rounded corners and visual effects"""
    # Draw main box
    pygame.draw.rect(
        screen,
        color,
        rect,
        2,
        border_radius=border_radius
    )
    
    # Draw text
    txt_surface = font.render(text, True, (255, 255, 255))
    text_rect = txt_surface.get_rect(center=rect.center)
    screen.blit(txt_surface, text_rect)
    
    # Draw placeholder if empty
    if not text:
        placeholder = font.render("Enter word...", True, (100, 100, 100))
        placeholder_rect = placeholder.get_rect(center=rect.center)
        screen.blit(placeholder, placeholder_rect)
    
    return rect

# Export all functions
__all__ = ['create_gradient_surface', 'draw_button', 'draw_input_box']