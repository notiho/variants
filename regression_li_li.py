import numpy as np
from sklearn.linear_model import LogisticRegression
from collections import defaultdict, Counter
import random

num_layers = 12
target_layer = 11
num_hidden = 768

random.seed(1357)
np.random.seed(0)

parallel_passages = []
with open("parallel_passages.csv") as infile:
	parallel_passages = infile.readlines()[1:]
parallel_passages = [x.split(",") for x in parallel_passages]

indices_by_profile = defaultdict(list)

kr_numbers_by_sample_index = []
directions_by_sample_index = []
alignment_indices_by_sample_index = []
labels_by_index = []
target_counts = defaultdict(Counter)

for i, (profile, kr_number, direction, index, l_a, a, r_a, l_b, b, r_b) in enumerate(parallel_passages):
	indices_by_profile[profile].append(i)
	labels_by_index.append(b)
	kr_numbers_by_sample_index.append(kr_number)
	directions_by_sample_index.append(direction)
	alignment_indices_by_sample_index.append(index)
	target_counts[(profile, kr_number)].update(b)


embeddings = np.load("embeddings.npy")
assert(len(parallel_passages) * num_layers == len(embeddings))

regression = LogisticRegression(
	penalty = "l2",
	solver = "lbfgs",
	multi_class = "auto",
	n_jobs = -1,
	max_iter = 1000,
)

rsts = []

indices = indices_by_profile["厯:暦歴"] + indices_by_profile["歴:暦歴"]

target_chars = "暦歴"
num_targets = len(target_chars)

label_to_number = { l: i for i, l in enumerate(target_chars) }
number_to_label = { i: l for i, l in enumerate(target_chars) }
kr_numbers = ["KR2n0002", "KR2n0013", "KR3j0038", "KR3k0012", "KR4c0049",
	"KR4d0054", "KR4d0464", "KR4d0493", "KR4f0025", "KR4h0024", "KR4h0102",
	"KR4i0025", "KR4d0073", "KR4h0034"]

kr_numbers_shuffled = random.sample(set(kr_numbers), k = len(set(kr_numbers)))
partition = np.array_split(kr_numbers_shuffled, min(10, len(kr_numbers_shuffled)))

for test_index in range(len(partition)):
	print(f"Starting experiment {test_index + 1}/{len(partition)}")
	
	test_kr_numbers = partition[test_index]
	train_kr_numbers = [i for i in kr_numbers if not i in test_kr_numbers]
	
	train_indices = [i for i in indices if kr_numbers_by_sample_index[i] in train_kr_numbers]
	test_indices = [i for i in indices if kr_numbers_by_sample_index[i] in test_kr_numbers]
	
	train_layer_indices = [x * num_layers + target_layer for x in train_indices]
	train_labels = [labels_by_index[x] for x in train_indices]
	
	model = regression.fit(embeddings[train_layer_indices],
									[label_to_number[x] for x in train_labels])
	
	test_layer_indices = [x * num_layers + target_layer for x in test_indices]
	test_labels = [labels_by_index[x] for x in test_indices]
	
	for i, layer_index, label in zip(test_indices, test_layer_indices, test_labels):
		assert(kr_numbers_by_sample_index[i] in test_kr_numbers)
		probabilities = model.predict_proba([embeddings[layer_index]])
		for j in range(num_targets):
			rsts.append((kr_numbers_by_sample_index[i],
						 directions_by_sample_index[i], i,
						 profile, label,
						 number_to_label[j], probabilities[0][j]))

input("Press enter to start writing to file:")

with open("regression_predictions_li_li.csv", "w") as outfile:
	outfile.write("test_kr_number,direction,index,profile,target,prediction,probability\n")
	for r in rsts:
		outfile.write(",".join(str(x) for x in r) + "\n")

