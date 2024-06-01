import os, re, json
from tqdm import tqdm
import jieba

doc_ids_path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/test_ids.txt"
data_path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/Legal_data"

法条_path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/法条倒排.json"
审判长_path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/审判长倒排.json"
keyword_path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/keyword_ridx.json"

法条格式 = r'FT value="([^"]*)"'
审判长格式 = r'FGRYXM nameCN="法官人员姓名" value="([^"]*)"'
全文格式 = r'QW nameCN="全文" oValue="([^"]*)"'

keyword_remain_ratio = 0.1
remain_ths = 2



doc_ids = []
with open(doc_ids_path, 'r') as fp:
    lines = fp.readlines()
    doc_ids = [int(l.strip()) for l in lines]


法条倒排索引 = {}
审判长倒排索引 = {}
keyword_ridx = {}

for doc_id in tqdm(doc_ids):
    path = os.path.join(data_path, f"{doc_id}.xml")
    with open(path, 'r') as fp:
        lines = fp.readlines()
        content = "".join(lines)
    法条们 = re.findall(法条格式, content)
    审判长们 = re.findall(审判长格式, content)
    全文 = re.findall(全文格式, content)[0]

    
    for 法条 in 法条们:
        if 法条 not in 法条倒排索引:
            法条倒排索引[法条] = []
        法条倒排索引[法条].append(doc_id)
    
    for 审判长 in 审判长们:
        if 审判长 not in 审判长倒排索引:
            审判长倒排索引[审判长] = []
        审判长倒排索引[审判长].append(doc_id)

    keywords = list(jieba.cut_for_search(全文))
    for k in keywords:
        if k not in keyword_ridx:
            keyword_ridx[k] = []
        keyword_ridx[k].append(doc_id)

pruned_keyword_ridx = {}
for k in keyword_ridx.keys():
    if len(keyword_ridx[k]) < keyword_remain_ratio * len(doc_ids) and len(keyword_ridx[k]) > remain_ths: # 去掉类似”法院“之类的词
        pruned_keyword_ridx[k] = list(set(keyword_ridx[k]))
    
with open(法条_path, 'w') as fp:
    json.dump(法条倒排索引, fp)
with open(审判长_path, 'w') as fp:
    json.dump(审判长倒排索引, fp)
with open(keyword_path, 'w') as fp:
    json.dump(pruned_keyword_ridx, fp)
