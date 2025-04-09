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
    #print(segmentation)
    return segmentation

def calculate_likelihood(prob_dist, segmentation):
    return sum(math.log(prob_dist.get(subword, 1e-30)) for subword in segmentation)

def em_training(corpus, prob_dist, max_iterations=10, prune_threshold=1e-7):
    candidates = generate_candidates(corpus)
    print(f"Initial candidate vocabulary size: {len(candidates)}")

    freq = subword_frequency(corpus, candidates)
    prob_dist = generate_probabilty_distribution(freq)

    corpus_path = corpus
    corpus = remove_spaces(corpus)
    
    for it in range(max_iterations):
        print(f"\nIteration {it + 1}")
        new_counts = Counter()

        with open(corpus_path, 'r', encoding='utf-8') as file, open("outputnew.txt", "w", encoding='utf-8') as output_file:
            corpus = corpus.replace("▁", "").strip()
            print("Corpus after removing spaces:", corpus)
            output_file.write(corpus)
            segmentation = viterbi(corpus, prob_dist)
            new_counts.update(segmentation)

        prob_dist = generate_probabilty_distribution(new_counts)

        pruned_candidates = {subword for subword, prob in prob_dist.items() if prob > prune_threshold}
        candidates = pruned_candidates
        prob_dist = {subword: prob for subword, prob in prob_dist.items() if subword in pruned_candidates}
        print(f"Vocabulary size after iteration {it + 1}: {len(candidates)}")
    
    return candidates, prob_dist

#generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt')))
# with open("output.txt", "r", encoding="utf-8") as f:
    # normalized_text = f.read().replace("▁", "").strip()

final_candidates, final_prob_dist = em_training('output.txt', generate_probabilty_distribution(subword_frequency('output.txt', generate_candidates('output.txt'))), prune_threshold=1e-7)
print(f"Final candidate vocabulary size: {len(final_candidates)}")
print(f"Final probability distribution size:", final_prob_dist)
print(final_candidates)

