import glob
import regex
from multiprocessing import Pool
import tqdm
import mmap
from collections import Counter
import scipy
import numpy as np
import os
import torch
import random
from scipy.special import softmax
from transformers import AutoTokenizer, BertForMaskedLM
from scipy.spatial import distance
import sys

tokenizer = AutoTokenizer.from_pretrained("Jihuai/bert-ancient-chinese")
model = BertForMaskedLM.from_pretrained("Jihuai/bert-ancient-chinese")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

model.to(device)
model.eval()

hidden_size = model.config.hidden_size
num_layers = model.config.num_hidden_layers

print(f"Hidden size: {hidden_size}, num_layers: {num_layers}")

targets = []
with open("parallel_passages.csv") as infile:
	targets = infile.readlines()[1:]

targets = [t.split(",") for t in targets]

embeddings = []

for profile,kr_number,direction,index,l_a,a,r_a,l_b,b,r_b in tqdm.tqdm(targets):
	inputs = tokenizer(["".join((l_a, a, r_a))],
		return_tensors="pt", padding=True).to(device)
	
	with torch.no_grad():
		hidden = model(**inputs, output_hidden_states=True).hidden_states
		e = [h[0,1 + len(l_a)].detach().cpu().numpy() for h in hidden[1:]]
		embeddings.extend(e)

input("Press enter to start writing to file.")

embeddings = np.array(embeddings)
np.save(f"embeddings.npy", embeddings)
