import gradio as gr
from normaliser import normalize_text
from unigram import generate_candidates, subword_frequency, generate_probabilty_distribution, baum_welch, viterbi

words = generate_candidates('output.txt')
freq = subword_frequency('output.txt', words)
for subword in words:
    freq[subword] += 1.0 
prob_dist = generate_probabilty_distribution(freq)
final_prob_dist = baum_welch('output.txt', words, 1e-7, prob_dist)

def segment_sentence(sentence):
    normalized = normalize_text(sentence)
    corpus = normalized.replace("<pad>", "") 
    segmentation = viterbi(corpus, final_prob_dist)
    return segmentation

gr.Interface(
    fn=segment_sentence,
    inputs=gr.Textbox(lines=2, placeholder="Enter a sentence..."),
    outputs=gr.Textbox(label="Segmented Tokens"),
    title="Token Separator (Viterbi)",
    description="This demo normalizes the sentence and segments it using Viterbi based on a unigram model."
).launch()
