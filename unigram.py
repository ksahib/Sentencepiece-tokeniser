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
                            start += len(subword) 
                        else:
                            start += 1
    #print(freq)
    return freq

def generate_probabilty_distribution(freq):
    total = sum(freq.values())
    prob_dist = {subword: count / total for subword, count in freq.items()}
    #print(prob_dist)
    return prob_dist

def remove_spaces(corpus):
    with open(corpus, 'r', encoding='utf-8') as file:
        text = file.read()       
    text = text.replace(' ', '') 
    text = text.strip()          
    print("Spaces removed")
    print(text)
    return text


def viterbi(corpus, prob_dist, max_word_length=20, prob_unknown=1e-20):
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
    #print(segmentation)
    return segmentation

def calculate_likelihood(corpus, prob_dist, segmentation):
    return sum(math.log(prob_dist.get(subword, 1e-30)) for subword in segmentation)

def prune_vocabulary(corpus, vocab, prob_dist, target_size):
    while len(vocab) > target_size:
        print("Current vocabulary size:", len(vocab))
        min_drop = float('inf')
        subword_to_remove = None
        for subword in vocab:
            print("Subword to remove:", subword)
            temp_vocab = vocab - {subword}
            temp_prob_dist = {k: v for k, v in prob_dist.items() if k in temp_vocab}
            segmentation = viterbi(corpus, temp_prob_dist)
            original_likelihood = calculate_likelihood(corpus, prob_dist, segmentation)
            likelihood = calculate_likelihood(corpus, temp_prob_dist, segmentation)
            drop = original_likelihood - likelihood 
            if drop < min_drop:
                min_drop = drop
                subword_to_remove = subword
        print("*******Removing subword:**********", subword_to_remove)
        vocab.remove(subword_to_remove)
        prob_dist = {k: v for k, v in prob_dist.items() if k in vocab}
    return vocab

#generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt')))
with open("output.txt", "r", encoding="utf-8") as f:
    normalized_text = f.read().replace("▁", "").strip()
seg = viterbi(normalized_text, generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt'))))
print("Segmentation:", seg)
new_vocab = prune_vocabulary(normalized_text, set(generate_candidates('output.txt')), generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt'))), 500)
print("Final vocabulary size:", len(new_vocab))
print("Final vocabulary:", new_vocab)
