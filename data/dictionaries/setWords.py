def filter_words(input_file, output_file, word_length):
    words = []
    with open(input_file, 'r') as infile:
        for word in infile:
            word = word.strip()
            if len(word) == word_length:
                words.append(word)
    
    words.sort()
    
    with open(output_file, 'w') as outfile:
        for word in words:
            outfile.write(word + '\n')

# Filter 5-letter words
filter_words('sowpods.txt', '5_letter.txt', 5)

# Filter 3-letter words
filter_words('sowpods.txt', '3_letter.txt', 3)