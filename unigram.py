from collections import Counter
import math
import re
import lattice


def generate_candidates(normalised_file):
    candidates = set()
    cache = set()
    with open(normalised_file, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.strip()
            if not sentence:
                continue
            for i in range(len(sentence)):
                for j in range(i+1, i+21):
                    word_subs = sentence[i:j]
                    if not word_subs:
                        continue
                    if word_subs in cache:
                        continue
                    candidates.add(word_subs)
                    cache.add(word_subs)
    #print(candidates)
    return candidates

# def generate_candidates(normalised_file):
#     candidates = set()
#     with open(normalised_file, 'r', encoding='utf-8') as file:
#         for line in file:
#             sentence = line.strip()  # Remove delimiters if needed
#             n = len(sentence)
#             # Generate all possible substrings
#             word_subs = [
#                 sentence[i:j] 
#                 for i in range(n) 
#                 for j in range(i+1, n+1)
#             ]
#             candidates.update(word_subs)
#     return candidates

#generate_candidates('output.txt')
# def subword_frequency(corpus, subwords):
#     freq = Counter()
#     with open(corpus, 'r', encoding='utf-8') as file:
#         for line in file:
#             sentence = line.strip()
#             if not sentence:
#                 continue
#             for word in sentence.split('_'):
#                 if not word:
#                     continue
#                 for subword in subwords:
#                     start = 0
#                     while start <= len(word) - len(subword):
#                         if word[start:start+len(subword)] == subword:
#                             freq[subword] += 1
#                             start += len(subword) 
#                         else:
#                             start += 1
#     #print(freq)
#     return freq

def subword_frequency(corpus, subwords):
    freq = Counter()
    i = 1
    print("Subword frequency calculation started")
    with open(corpus, 'r', encoding='utf-8') as file:
        for line in file:
            print(f"Line {i}: ")  # Debugging line
            i += 1
            sentence = line.strip()  # Remove delimiters
            if not sentence:
                continue
            for subword in subwords:
                pattern = r'(?={})'.format(re.escape(subword))
                freq[subword] += len(re.findall(pattern, sentence))
            # for subword in subwords:
            #     start = 0
            #     while start <= len(sentence) - len(subword):
            #         print(f"start: {start}, len: {len(sentence) - len(subword)}")
            #         if sentence[start:start+len(subword)] == subword:
            #             freq[subword] += 1
            #             start += len(subword)  # Non-overlapping counts
            #         else:
            #             start += 1
    print("freq: ", freq)  # Debugging line
    return freq

def generate_probabilty_distribution(freq):
    total = sum(freq.values())
    print("in")
    prob_dist = {subword: math.log(count / total) for subword, count in freq.items()}
    print("out")
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
            penalty = -20
            if subword in prob_dist:
                score = dp[j] + prob_dist[subword] + (penalty * len(subword)**2)
            else:
                score = dp[j] + math.log(prob_unknown) + (penalty * len(subword)**2)
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

# def em_training(corpus, prob_dist, max_iterations=10, prune_threshold=1e-7):
#     candidates = generate_candidates(corpus)
#     print(f"Initial candidate vocabulary size: {len(candidates)}")

#     freq = subword_frequency(corpus, candidates)
#     prob_dist = generate_probabilty_distribution(freq)

#     corpus_path = corpus
#     corpus = remove_spaces(corpus)
    
#     for it in range(max_iterations):
#         print(f"\nIteration {it + 1}")
#         new_counts = Counter()

#         with open(corpus_path, 'r', encoding='utf-8') as file, open("outputnew.txt", "w", encoding='utf-8') as output_file:
#             corpus = corpus.replace("▁", "").strip()
#             print("Corpus after removing spaces:", corpus)
#             output_file.write(corpus)
#             segmentation = viterbi(corpus, prob_dist)
#             new_counts.update(segmentation)

#         prob_dist = generate_probabilty_distribution(new_counts)

#         pruned_candidates = {subword for subword, prob in prob_dist.items() if prob > prune_threshold}
#         candidates = pruned_candidates
#         prob_dist = {subword: prob for subword, prob in prob_dist.items() if subword in pruned_candidates}
#         print(f"Vocabulary size after iteration {it + 1}: {len(candidates)}")
    
#     return candidates, prob_dist

# def logsumExp(a, b):
#     if not a or not b:
#         return -math.inf
#     if a == -math.inf and b == -math.inf:
#         return -math.inf
#     e1 = math.exp(a - max(a,b))
#     e2 = math.exp(b - max(a,b))
#     return max(a,b) + math.log(e1 + e2)

def logsumExp(a, b):
    if a == -math.inf and b == -math.inf:
        return -math.inf
    m = max(a, b)
    return m + math.log(math.exp(a-m) + math.exp(b-m))


def KL_divergence(p, q, vocab):
    d_kl = 0.0
    for v in vocab:
        d_kl += math.exp(p[v]) * (p[v] - q[v])
    return d_kl

def normalise_prob_dist(prob_dist):
    Z = -math.inf
    for value in prob_dist.values():
        Z = logsumExp(Z, value)
    for token in prob_dist.keys():
        prob_dist[token] = prob_dist[token] - Z
    return prob_dist

def baum_welch(corpus, vocab, epsilon: float, prob_dist):
    print("Baum-Welch algorithm started")
    global_EC = {token: -math.inf for token in vocab}
    print("Global EC initialized")
    global_EC['<BOS>'] = -math.inf
    global_EC['<EOS>'] = -math.inf
    with open(corpus, 'r', encoding='utf-8') as file:
        print("File opened")
        for line in file:
            sentence = line.strip()
            print(f"Sentence: {sentence}")
            if not sentence:
                continue
            lat = lattice.Lattice(sentence, prob_dist)
            lat.alpha = [-math.inf] * (len(sentence) + 3)
            lat.beta = [-math.inf] * (len(sentence) + 3)
            lat.alpha[0] = 0.0
            #old_prob_dist = prob_dist.copy()
            # old_prob_dist = {}
            iteration = 0
            while(True):
                # print(f"Iteration {test}")
                # if test > 2:
                #     return 0
                #forward pass
                print("Forward pass")
                for i in range(len(sentence)+1):
                    w_st = lat.end_nodes.get(i, [])
                    for w in w_st:
                        lat.alpha[i+1] = logsumExp(lat.alpha[i+1], (lat.alpha[w.pos+1] + w.score))
                        print(f"Node {i} alpha: {lat.alpha[i+1]}")  # Debugging
                #backward pass
                print("Backward pass")
                for i in range(len(sentence)+1, -1, -1):
                    if(i == len(sentence)+1):
                        lat.beta[i+1] = 0.0
                        print(f"Node {i} beta: {lat.beta[i+1]}")  # Debugging 
                    else:
                        w_st = lat.begin_nodes.get(i, [])
                        for w in w_st:
                            lat.beta[i+1] = logsumExp(lat.beta[i+1], (lat.beta[(w.pos+w.length)+1] + w.score))
                            print(f"Node {i} beta: {lat.beta[i+1]}")
                #E-step
                Z = lat.alpha[len(sentence)+1]
                for node in lat.nodes:
                    node.gamma = lat.alpha[node.pos+1] + lat.beta[(node.pos + node.length)+1] + node.score - Z
                    piece_bytes = node.piece.tobytes() if isinstance(node.piece, memoryview) else node.piece
                    piece_str = piece_bytes.decode()
                    print(f"Node {piece_str} gamma: {node.gamma}")
                EC = {}
                for node in lat.nodes:
                    piece_bytes = node.piece.tobytes() if isinstance(node.piece, memoryview) else node.piece
                    piece_str = piece_bytes.decode()
                    EC[piece_str] = -math.inf
                for node in lat.nodes:
                    piece_bytes = node.piece.tobytes() if isinstance(node.piece, memoryview) else node.piece
                    piece_str = piece_bytes.decode()
                    EC[piece_str] = logsumExp(EC[piece_str], node.gamma)
                #M-step
                EC_w_prime = - math.inf
                new_prob_dist = {}
                for value in EC.values():
                    EC_w_prime = logsumExp(EC_w_prime, value)
                for node in lat.nodes:
                    piece_bytes = node.piece.tobytes() if isinstance(node.piece, memoryview) else node.piece
                    piece_str = piece_bytes.decode()
                    node.score = EC[piece_str] - EC_w_prime
                    new_prob_dist[piece_str] = EC[piece_str] - EC_w_prime

                pruned_set = new_prob_dist.copy()
                #convergence check
                if iteration > 0:
                    theta = KL_divergence(prob_dist, new_prob_dist, new_prob_dist.keys())
                    if theta < epsilon:
                        prune_threshold = 1e-1000
                        for tok, logp in new_prob_dist.items():
                            p = math.exp(logp)
                            if p < prune_threshold and tok not in ['<BOS>', '<EOS>']:
                                del pruned_set[tok]
                                for node in lat.nodes:
                                    piece_bytes = node.piece.tobytes() if isinstance(node.piece, memoryview) else node.piece
                                    piece_str = piece_bytes.decode()
                                    if piece_str == tok:
                                        lat.remove_node(node)
                        normalise_prob_dist(pruned_set)
                        theta2 = KL_divergence(prob_dist, pruned_set, pruned_set.keys())
                        if theta2 < epsilon:
                            break
                # for token in old_prob_dist.keys():
                #     if token not in new_prob_dist:
                #         new_prob_dist[token] = math.log(1e-40)
                #vocab = set(pruned_set.keys())
                
                # for token in prob_dist.keys():
                #     if token not in pruned_set:
                #         del prob_dist[token]
                
                
                prob_dist = pruned_set
                lat = lattice.Lattice(sentence, prob_dist)
                lat.alpha = [-math.inf] * (len(sentence) + 3)
                lat.beta = [-math.inf] * (len(sentence) + 3)
                lat.alpha[0] = 0.0
                iteration += 1

            for node in lat.nodes:
                piece_bytes = node.piece.tobytes() if isinstance(node.piece, memoryview) else node.piece
                piece_str = piece_bytes.decode()
                global_EC[piece_str] = logsumExp(global_EC[piece_str], EC[piece_str])
        
        # for value in global_EC.values():
        #     global_EC[value] = logsumExp(global_EC[value], value)
        final_prob_dist = {}
        Z_final = -math.inf
        for values in global_EC.values():
            Z_final = logsumExp(Z_final, values)
        for token in vocab:
            final_prob_dist[token] = global_EC[token] - Z_final
    
    return final_prob_dist


# words = generate_candidates('output.txt')
# print(f"Candidates: {words}")
words = generate_candidates('output.txt')
print(f"Candidates: {words}")
freq = subword_frequency('output.txt', words)
for subword in words:
    freq[subword] += 1.0
print(f"Frequency: {freq}")
prob_dist2 = generate_probabilty_distribution(freq)
print(f"Probability distribution: {prob_dist2}")
prob = baum_welch('output.txt', generate_candidates('output.txt'), 1e-7, prob_dist2)
print(f"Candidates size: {words}")
print(f"Final probability distribution size: {prob}")
with open('output.txt', 'r', encoding='utf-8') as f:
    corpus_content = f.read().strip()

segmentation = viterbi(corpus_content, prob)
print(f"Segmentation: {segmentation}")
