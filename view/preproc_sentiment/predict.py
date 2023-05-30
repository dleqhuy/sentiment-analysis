import torch
from transformers import RobertaForSequenceClassification, AutoTokenizer
import pandas as pd
from tqdm import tqdm

model = RobertaForSequenceClassification.from_pretrained(
    "wonrax/phobert-base-vietnamese-sentiment")

tokenizer = AutoTokenizer.from_pretrained(
    "wonrax/phobert-base-vietnamese-sentiment", use_fast=False)

# Just like PhoBERT: INPUT TEXT MUST BE ALREADY WORD-SEGMENTED!

# sentence = 
df_txts = []
df_lbls = []
lbl_map = {
    0: 'negative',  
    1: 'positive', 
    2: 'neutral',  
}
prob_pos = []
with open(
        'view/csv/sentences.txt',
        'r') as f:
    sentences = f.readlines()
    sentences = [sentence.strip() for sentence in sentences][:]
    sentences = [sentence for sentence in sentences if len(sentence) > 0]
    print(len(sentences))
    sentences_ids = [tokenizer.encode(sentence, max_length=256, truncation=True, padding=True) for sentence in sentences]
    for i in tqdm(range(0, len(sentences_ids))):
        input_ids = torch.tensor([sentences_ids[i]])
        with torch.no_grad():
            out = model(input_ids)
            prob = out.logits.softmax(dim=-1)
            lbl = torch.argmax(prob, dim=-1)
            df_lbls.append(lbl_map[lbl.item()])

df_txts = sentences
df = pd.DataFrame({'txt': df_txts, 'lbl': df_lbls})
stat = df.groupby('lbl').count()
print(stat)
df.to_csv('view/csv/sentences_pseudo.csv', index=False)