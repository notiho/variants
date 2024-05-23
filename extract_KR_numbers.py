import regex
import glob
import tqdm

ids = []
id_to_title_dynasty_author = dict()


with open("KR-Catalog-master/general/sbck.org") as sbck_file:
	lines = sbck_file.readlines()
	
	for l in lines:
		if l.startswith(":KR_ID:"):
			ids.append(l.split()[1])

print(f"Found {len(ids)} in sbck file")

for kr_filename in glob.glob("KR-Catalog-master/KR/*.txt"):
	with open(kr_filename) as kr_file:
		lines = kr_file.readlines()
	
	cur_id = None
	has_wyg = False
	has_sbck = False
	
	for l in lines:
		if l.startswith("*** "):
			if cur_id and cur_id in ids:
				if not has_wyg:
					print("removing id with no WYG")
					ids.remove(cur_id)
			
			cur_id = l.split()[1]
			id_to_title_dynasty_author[cur_id] = l.split()[2]
			has_wyg = False
			has_sbck = False
		elif l.startswith("***** WYG"):
			has_wyg = True
		elif l.startswith("***** SBCK"):
			has_sbck = True
		
		if has_wyg and has_sbck:
			print("Found dual edition in KR file")
			if cur_id not in ids:
				ids.append(cur_id)

ids = set(ids)

with open("dual_kr_ids.txt", "w") as outfile:
	outfile.write("\n".join(ids))

with open("kr_number_to_title_dynasty_author.csv", "w") as outfile:
	outfile.write("kr_number,title,dynasty,author\n")
	for i in ids:
		outfile.write(i + "," + ",".join(id_to_title_dynasty_author[i].split("-")) + "\n")
