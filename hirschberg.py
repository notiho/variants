import glob
from collections import defaultdict
from sequence_align.pairwise import hirschberg, needleman_wunsch
import tqdm
from multiprocessing import Pool


with open("texts.csv") as infile:
	lines = infile.readlines()[1:]

kr_numbers = []
text_by_kr_number_edition = {}

for l in lines:
	kr_number, edition, text = l.split(",")
	kr_numbers.append(kr_number)
	text_by_kr_number_edition[(kr_number, edition)] = text.strip()[:50_000]

kr_numbers = list(set(kr_numbers))
kr_numbers.sort(key = lambda x: max(len(text_by_kr_number_edition[(x, "WYG")]), len(text_by_kr_number_edition[(x, "SBCK")])),
				reverse = True)

def compute_alignment(kr_number):
	global text_by_kr_number_edition
	wyg_text = text_by_kr_number_edition[(kr_number, "WYG")]
	sbck_text = text_by_kr_number_edition[(kr_number, "SBCK")] 
	return (kr_number, hirschberg(
		wyg_text,
		sbck_text,
		match_score=1.0,
		mismatch_score=-1.0,
		indel_score=-1.0,
		gap="＿",
	))

with Pool(8) as pool:
	rsts = list(tqdm.tqdm(pool.imap(compute_alignment, kr_numbers, chunksize=1), total=len(kr_numbers)))

input("Press enter to start writing to file.")

with open("alignments.csv", "w") as outfile:
	outfile.write("kr_number,wyg_aligned,sbck_aligned\n")
	for kr_number, (wyg_aligned, sbck_aligned) in rsts:
		outfile.write(",".join((kr_number, "".join(wyg_aligned), "".join(sbck_aligned))) + "\n")

