import unicodedata
import re

def normalize_text(text):
    normalized = unicodedata.normalize('NFKC', text).lower()
    #Note:
    # r'() denotes raw string input, [,.!?;:] is the capturing group, r' \1 ' means will replace the puncutations 
    # in the capturing group with itself wrapped in spaces
    #/1 means the first punctuation mark encountered.
    # Example: "Hello, world!" will be replaced with "Hello , World !", 
    # it matches the comma, /1 is now comma, and then it replaces it with r' \1 ' which is " , "
    normalized = re.sub(r'([,.!?;:])', r' \1 ', normalized) 
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = normalized.replace(" ", "▁")
    return normalized

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences

def extract_unique_characters(normalized_file):
    unique_chars = set()
    with open(normalized_file, "r", encoding="utf-8") as f:
        for line in f:
            unique_chars.update(line.strip()) 
    return sorted(list(unique_chars))

def prepare_and_extract(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as output_file:
        sentences = split_into_sentences(infile.read())
        for sentence in sentences:
            normalized_sentence = normalize_text(sentence.strip())
            output_file.write(normalized_sentence + '\n')

    vocab_chars = extract_unique_characters(output_file.name)

    special_tokens = ["<unk>", "<s>", "</s>", "<pad>"]
    final_vocab = special_tokens + vocab_chars

    token2idx = {token: idx for idx, token in enumerate(final_vocab)}
    print(token2idx)
    return token2idx


prepare_and_extract('input.txt', 'output.txt') 