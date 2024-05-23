from collections import Counter, defaultdict
import tqdm
import numpy as np
import random
from multiprocessing import Pool
import sys

manual_normalizations = [
	("歷", "歴"),
	("曆", "暦")
]

ignore_profiles = set([
	"為:為爲",
	"所:所𫠦",
	"之:之巻",
	"出:出岀",
	"世:世丗",
	"將:将將",
	"爲:為爲",
	"能:䏻能",
	"於:扵於",
	"清:淸清",
	"與:与與",
	"數:数數",
	"無:无無",
	"隂:陰隂",
	"歸:㱕歸",
	"來:來来",
	"從:従從",
	"事:亊事",
	"傳:傳𫝊",
	"處:䖏處",
	"𤣥:玄𤣥",
	"樹:樹𣗳",
	"既:既旣",
	"闕:闕𨶕",
	"禮:礼禮",
	"畫:畫𦘕",
	"學:學斈",
	"國:囯國",
	"青:靑青",
	"髙:高髙",
	"侯:侯矦",
	"樂:楽樂",
	"羣:羣群",
	"變:変變",
	"郎:郎郞",
	"今:今仐",
	"勢:勢𫝑",
	"晉:晉𣈆",
	"發:發𤼵",
	"功:㓛功",
	"本:夲本",
	"卷:卷巻",
	"獲:獲𫉬",
	"兩:两兩",
	"哉:㢤哉",
	"土:土圡",
	"致:致𦤺",
	"或:㦯或",
	"葬:葬𦵏",
	"嘗:嘗甞",
	"世:世丗卋",
	"定:㝎定",
	"即:即卽",
	"黄:黃黄",
	"節:節莭",
	"去:厺去",
	"風:凬風",
	"凡:凡凢",
	"美:美羙",
	"内:內内",
	"啓:啓啟",
	"祭:祭𥙊",
	"徳:徳德",
	"雙:雙𩀱",
	"尚:尙尚",
	"哉:㢤㦲哉",
	"笑:笑𥬇",
	"石:䂖石",
	"逺:逺遠",
	"辭:辝辭",
	"别:別别",
	"乆:久乆",
	"教:敎教",
	"類:類𩔖",
	"再:再𠕅",
	"幾:㡬幾",
	"第:巻第",
	"飲:飮飲",
	"僞:偽僞",
	"留:留畱",
	"聽:聴聽",
	"養:飬養",
	"愛:愛爱",
	"刺:刺剌",
	"稱:称稱",
	"德:徳德",
	"陵:陵𨹧",
	"發:彂發",
	"富:冨富",
	"恩:㤙恩",
	"絶:絕絶",
	"尋:㝷尋",
	"辭:辞辭",
	"亂:乱亂",
	"吳:吳呉",
	"說:說説",
	"辭:辤辭",
	"因:囙因",
	"楚:椘楚",
	"器:噐器",
	"亡:亡亾",
	"告:吿告",
	"回:囘回",
	"熈:熈熙",
	"歸:帰歸",
	"鄉:郷鄕",
	"改:改攺",
	"秦:秦𥘿",
	"旣:既旣",
	"商:商啇",
	"惡:惡𢙣",
	"輕:䡖輕",
	"微:㣲微",
	"宜:冝宜",
	"首:首𩠐",
	"以:㠯以",
	"專:専專",
	"顧:頋顧",
	"舉:㪯舉",
	"豐:豊豐",
	"竒:奇竒",
	"深:㴱深湥",
	"高:高髙",
	"兊:兊兌",
	"宿:宿𪧐",
	"易:易昜",
	"隆:隆𨺚",
	"藏:蔵藏",
	"象:象𧰼",
	"關:闗關",
	"盖:盖葢",
	"坐:㘴坐",
	"爭:争爭",
	"忘:㤀忘",
	"鄉:郷鄉",
	"𨵿:闗關",
	"曉:暁曉",
	"袁:袁𡊮",
	"兒:児兒",
	"死:死𣦸",
	"劉:刘劉",
	"隱:隠隱",
	"𢎞:弘𢎞",
	"顯:顯𩔰",
	"戰:戰𢧐",
	"看:㸔看",
	"居:㞐居",
	"明:明朙",
	"久:久乆",
	"處:処處",
	"盖:盖葢蓋",
	"游:㳺游",
	"緑:綠緑",
	"真:眞真",
	"脉:脈脉",
	"畫:画畫",
	"略:略畧",
	"晩:晚晩",
	"裏:裏裡",
	"虚:虚虛",
	"斷:㫁斷",
	"著:着著",
	"邊:邉邊",
	"收:収收",
	"似:似佀",
	"遊:逰遊",
	"斷:断斷",
	"㡬:㡬幾",
	"蓋:盖蓋",
	"倚:倚𠋣",
	"賔:賓賔",
	"錢:銭錢",
	"貴:䝿貴",
	"屬:属屬",
	"關:關𨵿",
	"降:䧏降",
	"雖:虽雖",
	"隨:随隨",
	"笑:咲笑𥬇",
	"蓋:葢蓋",
	"從:徔從",
	"船:舩船",
	"歸:㱕帰歸",
	"興:㒷興",
	"禄:祿禄",
	"歳:嵗歲歳",
	"庶:庶庻",
	"辭:辞辤辭",
	"圖:圖圗",
	"賛:賛贊",
	"惠:恵惠",
	"榖:榖穀",
	"臺:䑓臺",
	"號:号號",
	"恱:恱悦",
	"樓:楼樓",
	"巻:卷巻",
	"吴:吳呉",
	"類:𩔖𩔗",
	"獻:献獻",
	"晉:晉晋𣈆",
	"歲:嵗歲",
	"𧷢:贓贜",
	"勅:勑𠡠",
	"雙:双雙𩀱",
	"録:錄録",
	"敕:敇敕",
	"况:况況",
	"奇:奇竒",
	"聽:聴聼聽",
	"鎮:鎭鎮",
	"闗:関闗",
	"哉:㢤㦲",
	"夢:夢梦",
	"夢:夢夣",
	"勑:勅敇",
	"来:來来",
	"狀:状狀",
	"窮:窮竆",
	"據:㩀據",
	"實:实實",
	"寳:寳寶",
	"鹽:塩鹽",
	"齊:斉齊",
	"備:備𤰅",
	"鄉:郷鄉鄕",
	"昜:易昜",
	"選:選𨕖",
	"備:俻備",
	"闗:關𨵿",
	"況:况況",
	"並:並竝",
	"懷:懐懷",
	"博:博愽",
	"靜:静靜",
	"輙:輒輙",
	"盖:葢蓋",
	"曽:曽曾",
	"晉:晉晋",
	"隠:隱𨼆",
	"刻:刻𠜇",
	"黃:黃黄",
	"歳:嵗歳",
	"嚴:嚴𫿞",
	"卒:䘚卒",
	"聽:聼聽",
	"勢:势𫝑",
	"寧:寕寧",
	"劒:劍劒",
	"柳:柳栁",
	"遠:逺遠",
	"登:登豋",
	"逹:逹達",
	"遥:遙遥",
	"歩:步歩",
	"陰:陰隂",
	"淵:淵渊",
	"勑:勑𠡠",
	"滅:㓕滅",
	"留:㽞留",
	"廟:庙廟",
	"顯:顕顯𩔰",
	"宫:宫宮",
	"回:回囬",
	"世:世卋",
	"隱:隱𨼆",
	"関:闗關",
	"廉:亷廉",
	"鬢:鬢𩯭",
	"没:沒没",
	"刺:刺刾",
	"闗:関𨵿",
	"廟:庿廟",
	"蘇:蘇蘓",
	"戸:户戸",
	"從:従徔從",
	"煙:烟煙",
	"醉:酔醉",
	"潜:潛潜",
	"吕:吕呂",
	"縱:縦縱",
	"護:䕶護",
	"兩:両兩",
	"宜:冝宐宜",
	"偽:偽僞",
	"舎:舍舎",
	"鄉:郷鄉鄊",
	"過:過𬨨",
	"從:从從",
	"風:凨風",
	"鄉:郷鄊",
	"虚:虗虚",
	"壽:壽夀",
	"助:助𦔳",
	"乾:乹乾",
	"畫:畫畵𦘕",
	"職:聀職軄",
	"斷:㫁断",
	"形:形形",
	"囬:囘回",
	"濟:済濟",
	"雄:䧺雄",
	"圓:圎圓",
	"覽:覧覽",
	"喪:䘮喪",
	"鄉:鄉鄕",
	"統:統綂",
	"獨:独獨",
	"變:变変變",
	"綠:綠緑",
	"寧:寕寜",
	"添:添𣷹",
	"逃:迯逃",
	"謚:諡謚",
	"増:増增",
	"隋:陏隋",
	"門:門门",
	"強:強强",
	"紫:紫𬗋",
	"散:㪚散",
	"强:強强",
	"離:離𩀌",
	"廵:巡廵",
	"彦:彥彦",
	"簡:簡𥳑",
	"帶:帯帶",
	"䇿:䇿策",
	"逰:逰遊",
	"隱:隐隠隱",
	"吳:吳吴呉",
	"峰:峯峰",
	"呉:吴呉",
	"急:急𢚩",
	"畫:畫畵",
	"每:毎每",
	"時:时時",
	"舍:舍舎",
	"參:参參",
	"篆:篆篆",
	"迴:廻迴",
	"嵗:歲歳",
	"深:㴱深",
	"壯:壮壯",
	"勞:劳勞",
	"多:多夛",
	"低:仾低",
	"鄉:鄉鄊",
	"木:木朩",
	"頼:賴頼",
	"眞:眞真",
	"修:修脩",
	"劫:刼劫",
	"莊:荘莊",
	"笑:咲笑",
	"曹:曹曺",
	"户:戶户",
	"苑:苑𫟍",
	"遲:遟遲",
	"諫:諌諫",
	"冊:冊册",
	"蕭:䔥蕭",
	"離:离離",
	"帆:㠶帆",
	"叔:叔𠦑",
	"聞:聞闻",
	"歳:嵗歲",
	"剥:剝剥",
	"䑓:䑓臺",
	"翠:翆翠",
	"闗:闗𨵿",
	"亡:亡兦",
	"雙:䨇𩀱",
	"嘗:嘗尝",
	"厎:厎底",
	"景:㬌景",
	"畀:畀𢌿",
	"泰:㤗泰",
	"繼:継繼",
	"曾:曽曾",
	"懐:懐懷",
	"㓜:㓜幼",
	"巢:巢巣",
	"䟽:䟽疏",
	"顔:顏顔",
	"趨:趍趨",
	"懼:愳懼",
	"禪:禅禪",
	"慎:愼慎",
	"黒:黑黒",
	"𦘕:畫畵",
	"夜:亱夜",
	"筋:䈥筋",
	"鶴:寉鶴",
	"雙:㕠双",
	"嵗:嵗歳",
	"晚:晚晩",
	"寧:寍寧",
	"據:拠據",
	"䘮:䘮喪",
	"簡:簡蕳",
	"鳯:鳯鳳",
	"夢:夢萝",
	"䆫:忩窻",
	"㑹:㑹會",
	"肯:肎肯",
	"惡:悪惡",
	"館:舘館",
	"兩:㒳兩",
	"廼:廼迺",
	"猶:犹猶",
	"擊:撃擊",
	"栁:栁桞",
	"法:㳒法",
	"禄:䘵禄",
	"恭:㳟恭",
	"盡:䀆盡",
	"畝:畝畞",
	"産:產産",
	"堯:堯尭",
	"廻:廻𢌞",
	"歳:歲歳",
	"畧:略畧",
	"傅:傅𫝊",
	"戯:戯戲",
	"面:面靣",
	"船:舡船",
	"吳:吴呉",
	"農:䢉農",
	"苗:苖苗",
	"夷:夷𡗝",
	"雙:㕠雙",
	"藥:薬藥",
	"鉄:鐡鐵",
	"㸃:㸃點",
	"類:類𩔗",
	"虛:虚虛",
	"變:变變",
	"關:関𨵿",
	"桑:桑桒",
	"晉:晋𣈆",
	"讓:譲讓",
	"聮:聨聫",
	"職:職軄",
	"彌:弥彌",
	"嵗:嵗歲",
	"寜:寍寧",
	"輒:輒輙",
	"霸:覇霸",
	"徵:徴徵",
	"横:横橫",
	"聦:聦聰",
	"集:註集",
	"雙:双雙",
	"減:减減",
	"還:还還",
	"輒:輒輙",
	"霸:覇霸",
	"徵:徴徵",
	"横:横橫",
	"聦:聦聰",
	"集:註集",
	"雙:双雙",
	"減:减減",
	"還:还還"
])

def normalize(text):
	for a, b in manual_normalizations:
		text = text.replace(a, b)
	return text

random.seed(123456789)

with open("alignments.csv") as infile:
	lines  = infile.readlines()[1:]

def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def get_targets_one_direction(x, y, kr_number, direction):
	substituted_by_something_not_in_x = []
	substituted_where = defaultdict(lambda: defaultdict(list))
	x_counter = Counter(x)
	occurs_more_than_once_in_x = set(c for c, n in x_counter.most_common() if n > 1)
	
	avg = moving_average(x == y, n = 21) 
	
	for index, (a, b, i) in enumerate(zip(x[10:-10], y[10:-10], avg)):
		if i > 0.5 and a != "＿" and b != "＿" and x_counter[a] >= 100:
			substituted_where[a][b].append(index + 10)
			if b not in occurs_more_than_once_in_x:
				substituted_by_something_not_in_x.append(a)
	
	substituted_by_something_not_in_x = set(substituted_by_something_not_in_x)
	
	substituted_where = { a: { b: indices for b, indices in subs.items() if len(indices) >= 20 }
		for a, subs in substituted_where.items() }
	
	return [(r, { c: [(kr_number, direction, x, y, index) for index in indices] 
		for c, indices in substituted_where[r].items()}) 
		for r in substituted_by_something_not_in_x if len(substituted_where[r]) > 1 
			and sum(c in occurs_more_than_once_in_x for c in substituted_where[r]) <= 1]

def process_line(l):
	parts = l.split(",")
	x = normalize(parts[1])
	y = normalize(parts[2].strip())
	
	x_np = np.array([i for i in x], dtype = "U1")
	y_np = np.array([i for i in y], dtype = "U1")
	
	return get_targets_one_direction(x_np, y_np, parts[0], "WYG->SBCK") +\
		get_targets_one_direction(y_np, x_np, parts[0], "SBCK->WYG")

with Pool(8) as pool:
	rsts = list(tqdm.tqdm(pool.imap(process_line, lines), total=len(lines)))

profiles_sample_count = Counter()
indices_by_profile = defaultdict(list)

for i in rsts:
	for target, indices in i:
		profile = target + ":" + "".join(sorted(indices.keys()))
		profiles_sample_count[profile] += sum(len(i) for i in indices.values())
		indices_by_profile[profile].append(indices)

with open("parallel_passages.csv", "w") as outfile:
	outfile.write("profile,kr_number,direction,index,l_a,a,r_a,l_b,b,r_b\n")
	
	for profile, js in indices_by_profile.items():
		if profile in ignore_profiles:
			continue
		counter = 0
		for j in js:
			for indices in j.values():
				for kr_number, direction, x, y, i in indices:
					l_a = "".join(x[max(0, i - 200):i]).replace("＿", "")
					l_b = "".join(y[max(0, i - 200):i]).replace("＿", "")
					r_a = "".join(x[i + 1: i + 201]).replace("＿", "")
					r_b = "".join(y[i + 1: i + 201]).replace("＿", "")
					
					assert(x[i] == profile[0])
					assert(y[i] in profile[2:])
					
					outfile.write(",".join((profile, kr_number, direction, str(i),
											l_a, x[i], r_a,
											l_b, y[i], r_b)) + "\n")
					counter += 1
		print(f"Wrote {counter} lines for profile {profile}")

with open("substitution_profiles.csv", "w") as outfile:
	outfile.write("num_samples,profile\n")
	for profile, n in profiles_sample_count.most_common():
		outfile.write(f"{n},{profile}\n")