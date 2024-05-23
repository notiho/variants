import numpy as np
from sklearn.linear_model import LogisticRegression
from collections import defaultdict, Counter
import random

num_layers = 12
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

rsts = []

regression = LogisticRegression(
	penalty = "l2",
	solver = "lbfgs",
	multi_class = "auto",
	n_jobs = -1,
	max_iter = 1000,
)

for target_layer in range(num_layers):
	for profile, indices in indices_by_profile.items():
		print(f"Evaluating profile {profile}")
		
		target_chars = profile.split(":")[1]
		num_targets = len(target_chars)
		
		label_to_number = { l: i for i, l in enumerate(target_chars) }
		number_to_label = { i: l for i, l in enumerate(target_chars) }
		kr_numbers = [kr_numbers_by_sample_index[i] for i in indices]
		
		for kr_number in set(kr_numbers):
			print(f"Evaluating {kr_number}")
			
			indices_for_cur_kr_number = [i for i in indices if kr_numbers_by_sample_index[i] == kr_number]
			random.shuffle(indices_for_cur_kr_number)
			
			partition = np.array_split(indices_for_cur_kr_number, 10)
		
			for test_index in range(len(partition)):
				print(f"Starting experiment {test_index + 1}/{len(partition)}")
				test_indices = partition[test_index]
				train_indices = [i for i in indices_for_cur_kr_number if i not in test_indices]
				
				train_layer_indices = [x * num_layers + target_layer for x in train_indices]
				train_labels = [labels_by_index[x] for x in train_indices]
				
				model = regression.fit(embeddings[train_layer_indices],
									[label_to_number[x] for x in train_labels])
				
				test_layer_indices = [x * num_layers + target_layer for x in test_indices]
				test_labels = [labels_by_index[x] for x in test_indices]
				
				for i, layer_index, label in zip(test_indices, test_layer_indices, test_labels):
					assert(kr_numbers_by_sample_index[i] == kr_number)
					probabilities = model.predict_proba([embeddings[layer_index]])
					for j in range(num_targets):
						rsts.append((target_layer, kr_number, directions_by_sample_index[i], i,
										profile, label,
										number_to_label[j], probabilities[0][j]))

input("Press enter to start writing to file:")

with open("regression_predictions_by_document.csv", "w") as outfile:
	outfile.write("target_layer,kr_number,direction,index,profile,target,prediction,probability\n")
	for r in rsts:
		outfile.write(",".join(str(x) for x in r) + "\n")

