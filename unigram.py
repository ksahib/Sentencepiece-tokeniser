from collections import Counter
import math

def generate_candidates(normalised_file):
    candidates = set()
    cache = {}
    with open(normalised_file, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.strip()
            if not sentence:
                continue
            for word in sentence.split('▁'):
                if not word:
                    continue
                if word in cache:
                    candidates.update(cache[word])
                    continue
                n = len(word)
                word_subs = [word[i:j] 
                            for i in range(n) 
                            for j in range(i+1, n+1)]
                cache[word] = word_subs 
                candidates.update(word_subs)
    #print(candidates)
    return candidates

#generate_candidates('output.txt')
def subword_frequency(corpus, subwords):
    freq = Counter()
    with open(corpus, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.strip()
            if not sentence:
                continue
            for word in sentence.split('▁'):
                if not word:
                    continue
                for subword in subwords:
                    start = 0
                    while start <= len(word) - len(subword):
                        if word[start:start+len(subword)] == subword:
                            freq[subword] += 1
                            start += len(subword)  # Skip overlapping matches
                        else:
                            start += 1
    print(freq)
    return freq

def generate_probabilty_distribution(freq):
    total = sum(freq.values())
    prob_dist = {subword: count / total for subword, count in freq.items()}
    print(prob_dist)
    return prob_dist

def remove_spaces(corpus):
    with open(corpus, 'r', encoding='utf-8') as file:
        text = file.read()       
    text = text.replace(' ', '') 
    text = text.strip()          
    print("Spaces removed")
    print(text)
    return text


def viterbi(corpus, prob_dist, max_word_length=20, prob_unknown=1e-30):
    n = len(corpus)
    dp = [-float('inf')] * (n + 1)
    dp[0] = 0
    backpointer = [None] * (n + 1)
    for i in range(1, n + 1):
        for j in range(max(0, i - max_word_length), i):
            subword = corpus[j:i]
            if subword in prob_dist:
                score = dp[j] + math.log(prob_dist[subword])
            else:
                score = dp[j] + math.log(prob_unknown)
            if score > dp[i]:
                dp[i] = score
                backpointer[i] = j
    segmentation = []
    i = n
    while i > 0:
        j = backpointer[i]
        segmentation.insert(0, corpus[j:i])
        i = j
    print(segmentation)
    return segmentation

#generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt')))
with open("output.txt", "r", encoding="utf-8") as f:
    normalized_text = f.read().replace("▁", "").strip()
viterbi(normalized_text, generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt'))))