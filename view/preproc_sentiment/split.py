import py_vncorenlp
rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir='.')

from splitwords import Splitter
import re
import pandas as pd
from tqdm import tqdm

splitter = Splitter(language='vi')

def run(paragraph):
    sentence_ls = []
    pat = re.compile(r"([.()!])")
    paragraph = pat.sub(" \\1 ", paragraph)
    new_paragraph = []
    new_w = None
    for w in paragraph.split():
        if len(w) > 3:
            new_w = splitter.split(w.upper())
        else:
            new_w = None
        new_paragraph += [
            ' '.join(new_w).lower() if new_w is not None else w.lower()
        ]
    new_paragraph = ' '.join(new_paragraph)
    sentence_ls = rdrsegmenter.word_segment(new_paragraph)
    res = []
    for sentence in sentence_ls:
        res += sentence.split('.')
    return res


df = pd.read_csv('view/csv/pdp_comment_raw.csv').dropna(subset=['comment'])
paragraphs = df['comment'].values.tolist()
sentences = []
for paragraph in tqdm(paragraphs):
    
    sentences += run(paragraph)

with open(
        'view/csv/sentences.txt',
        'w') as f:
    for sentence in sentences:
        if len(sentence) > 5:
            f.write(sentence.strip() + '\n')
print(len(sentences))