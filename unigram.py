from collections import Counter

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
                    freq[subword] += word.count(subword)
    print(freq)
    return freq


subword_frequency('output.txt', generate_candidates('output.txt'))