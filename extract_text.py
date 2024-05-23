import glob
import regex
from multiprocessing import Pool
import tqdm
from collections import Counter, defaultdict
import scipy
import numpy as np
import os

non_hanzi_regex = regex.compile("\P{sc=Han}|䶻")
def only_hanzi(s):
	return regex.sub(non_hanzi_regex, "", s)

def process_file(filename):
	with open(filename) as raw:
		raw_text = raw.read()
	
	text = ""
	
	for l in raw_text.split("\n"):
		if l.startswith("#"):
			continue
		else:
			text += only_hanzi(l)
	
	juan = int(filename.split("/")[-1].split("_")[-1][:-4])
	
	return [text, filename.split("/")[-2].split("-")[0], filename.split("/")[-2].split("-")[1], juan]

filenames = glob.glob("corpus/*/*/KR*_[0-9][0-9][0-9].txt")

with Pool(8) as pool:
	rsts = list(tqdm.tqdm(pool.imap_unordered(process_file, filenames, chunksize=4), total=len(filenames)))

texts_by_kr_number_edition = defaultdict(list)
for text, kr_number, edition, juan in rsts:
	texts_by_kr_number_edition[(kr_number, edition)].append((text, kr_number, edition, juan))

other_edition = { "WYG": "SBCK", "SBCK": "WYG" }

text_by_kr_number_edition = dict()
for (kr_number, edition), texts in texts_by_kr_number_edition.items():
	combined_text = "".join(t for t, _, _, _ in sorted(texts, key = lambda x: x[3]))
	if len(combined_text) > 200:
		text_by_kr_number_edition[(kr_number, edition)] = combined_text

with open("texts.csv", "w") as outfile:
	outfile.write("kr_number,edition,text\n")
	for (kr_number, edition), text in text_by_kr_number_edition.items():
		if (kr_number, other_edition[edition]) in text_by_kr_number_edition:
			outfile.write(",".join((kr_number, edition, text)) + "\n")
