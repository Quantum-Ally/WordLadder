import os
import urllib.request
from src.scripts.build_graph import build_graph

def download_dictionary():
	"""Download and prepare dictionary files"""
	# Create directories if they don't exist
	os.makedirs("data/dictionaries", exist_ok=True)
	
	# Download SOWPODS dictionary if not exists
	sowpods_path = "data/dictionaries/sowpods.txt"
	if not os.path.exists(sowpods_path):
		print("Downloading dictionary...")
		url = "https://raw.githubusercontent.com/jesstess/Scrabble/master/sowpods.txt"
		urllib.request.urlretrieve(url, sowpods_path)
	
	# Create length-specific dictionaries
	def create_length_dictionary(length):
		output_path = f"data/dictionaries/{length}_letter.txt"
		if not os.path.exists(output_path):
			print(f"Creating {length}-letter dictionary...")
			with open(sowpods_path, 'r', encoding='utf-8') as infile:
				words = [word.strip().lower() for word in infile if len(word.strip()) == length]
			
			with open(output_path, 'w', encoding='utf-8') as outfile:
				outfile.write('\n'.join(words))
			print(f"Created {length}-letter dictionary with {len(words)} words")
	
	# Create dictionaries for both 3 and 5 letter words
	create_length_dictionary(3)
	create_length_dictionary(5)

if __name__ == "__main__":
	print("Setting up Word Ladder Adventure...")
	download_dictionary()
	
	# Build initial graphs
	print("\nBuilding word graphs...")
	build_graph(3)
	build_graph(5)
	
	print("\nSetup complete! You can now run main.py")