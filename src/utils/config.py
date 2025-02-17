import json
import os

def load_config():
    """
    Load configuration from config.json file
    Returns a dictionary with configuration settings
    """
    config_path = os.path.join(os.path.dirname(__file__), '../../config.json')
    
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        # Default configuration
        return {
            "screen": {
                "width": 800,
                "height": 600
            },
            "fonts": {
                "title": "Arial",
                "button": "Arial",
                "text": "Arial"
            },
            "colors": {
                "background": [20, 20, 40],
                "title": [255, 255, 255],
                "text": [200, 200, 200],
                "button": [100, 100, 100],
                "input_active": [0, 120, 255],
                "input_inactive": [100, 100, 100]
            },
            "welcome": {
                "title_size": 64,
                "button_size": 32
            },
            "setup": {
                "title_size": 48,
                "input_size": 32
            }
        }

# Make sure to export the function
__all__ = ['load_config']
