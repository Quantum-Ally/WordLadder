import json
from collections import defaultdict
from itertools import combinations
import os

def build_graph(word_length):
    """Build a word ladder graph for specified word length"""
    # File paths
    dict_file = f"data/dictionaries/{word_length}_letter.txt"
    graph_file = f"data/graphs/graph_{word_length}.json"
    
    # Ensure directories exist
    os.makedirs("data/graphs", exist_ok=True)
    os.makedirs("data/dictionaries", exist_ok=True)
    
    try:
        # Load words
        if not os.path.exists(dict_file):
            print(f"Dictionary file not found: {dict_file}")
            return False
            
        with open(dict_file, 'r', encoding='utf-8') as f:
            words = [word.strip().lower() for word in f.readlines() if word.strip()]
        
        if not words:
            print(f"No words found in {dict_file}")
            return False
        
        # Create adjacency list with costs
        graph = defaultdict(dict)
        
        # Build graph using pattern matching for efficiency
        pattern_buckets = defaultdict(list)
        for word in words:
            # Create patterns for each possible single letter change
            for i in range(len(word)):
                pattern = word[:i] + "*" + word[i+1:]
                pattern_buckets[pattern].append(word)
        
        # Connect words that differ by one letter
        for pattern, word_list in pattern_buckets.items():
            for word1, word2 in combinations(word_list, 2):
                # Calculate edge cost based on multiple factors
                cost = calculate_edge_cost(word1, word2)
                graph[word1][word2] = cost
                graph[word2][word1] = cost
        
        # Convert defaultdict to regular dict for JSON serialization
        graph_dict = {k: dict(v) for k, v in graph.items()}
        
        # Save graph with metadata
        graph_data = {
            "metadata": {
                "word_length": word_length,
                "node_count": len(words),
                "edge_count": sum(len(edges) for edges in graph.values()) // 2
            },
            "words": words,
            "graph": graph_dict
        }
        
        # Save graph
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully built graph for {word_length}-letter words")
        print(f"Total words: {len(words)}")
        print(f"Total edges: {graph_data['metadata']['edge_count']}")
        return True
        
    except Exception as e:
        print(f"Error building graph: {str(e)}")
        return False

def calculate_edge_cost(word1, word2):
    """Calculate weighted cost between words based on multiple factors"""
    # Find position where words differ
    diff_pos = next(i for i, (c1, c2) in enumerate(zip(word1, word2)) if c1 != c2)
    
    # Base cost (higher for changes at the start of the word)
    position_cost = 1.0 + (len(word1) - diff_pos) * 0.2
    
    # Vowel transition cost
    c1, c2 = word1[diff_pos], word2[diff_pos]
    vowel_cost = 0.5 if is_vowel(c1) != is_vowel(c2) else 0
    
    # Keyboard distance cost
    keyboard_cost = calculate_keyboard_distance(c1, c2)
    
    # Frequency cost (common letters have lower cost)
    freq_cost = calculate_frequency_cost(c1, c2)
    
    return position_cost + vowel_cost + keyboard_cost + freq_cost

def is_vowel(c):
    """Check if character is a vowel"""
    return c.lower() in 'aeiou'

def calculate_keyboard_distance(c1, c2):
    """Calculate normalized QWERTY keyboard distance"""
    keyboard = {
        'q': (0,0), 'w': (0,1), 'e': (0,2), 'r': (0,3), 't': (0,4),
        'y': (0,5), 'u': (0,6), 'i': (0,7), 'o': (0,8), 'p': (0,9),
        'a': (1,0), 's': (1,1), 'd': (1,2), 'f': (1,3), 'g': (1,4),
        'h': (1,5), 'j': (1,6), 'k': (1,7), 'l': (1,8),
        'z': (2,0), 'x': (2,1), 'c': (2,2), 'v': (2,3), 'b': (2,4),
        'n': (2,5), 'm': (2,6)
    }
    
    try:
        x1, y1 = keyboard[c1.lower()]
        x2, y2 = keyboard[c2.lower()]
        return 0.2 * ((abs(x1 - x2) + abs(y1 - y2)) / 10.0)
    except KeyError:
        return 0.5

def calculate_frequency_cost(c1, c2):
    """Calculate cost based on letter frequencies"""
    frequencies = {
        'e': 0.1, 'a': 0.09, 'r': 0.08, 'i': 0.07, 'o': 0.07,
        't': 0.07, 'n': 0.07, 's': 0.06, 'l': 0.05, 'c': 0.04,
        'u': 0.04, 'd': 0.03, 'p': 0.03, 'm': 0.03, 'h': 0.03,
        'g': 0.02, 'b': 0.02, 'f': 0.02, 'y': 0.02, 'w': 0.02,
        'k': 0.01, 'v': 0.01, 'x': 0.01, 'z': 0.01, 'j': 0.01, 'q': 0.01
    }
    
    # Higher cost for transitioning to/from rare letters
    return 0.3 * (1.0 - (frequencies.get(c1.lower(), 0) + frequencies.get(c2.lower(), 0)) / 2)

if __name__ == "__main__":
    # Build both graphs
    build_graph(3)
    build_graph(5)
    print("Graphs built successfully!")