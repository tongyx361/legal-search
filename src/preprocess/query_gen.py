import os, re, argparse
from openai import OpenAI
import json
from tqdm import tqdm


client = OpenAI()
template = "下面是一个法院判决书。请根据法院判决书，概括出两个句子。第一个句子是陈述句，第二个句子是疑问句。句子中不应该涉及案例中的具体详情，而是与法律知识结合。不能从原文中照抄，需要抓住重点。每个句子以[S]开始，以换行结束。不需要输出序号。再次注意，你是新手律师。# 判决书：{query} # 句子：\n"

query_temp = r'\[S\](.*?)(?=\n\[S\]|$)'

def gen_query(doc_list: list, doc_idxs: list, save_file: str):
    pbar = tqdm(total=len(doc_list))
    for doc, idx in zip(doc_list, doc_idxs):
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个新手律师，正在通过搜索引擎搜索相关案例。请根据下面的要求完成回答。"},
                    {"role": "user", "content": template.format(query=doc)}
                ]
            )
        except:
            print(f"openai error")
            continue
        try:
            gen_str = completion.choices[0].message.content
            extracetd_queries = re.findall(query_temp, gen_str)
            queries = [k.strip() for k in extracetd_queries]
            wlines = [{q: idx} for q in queries]
            wlines = [json.dumps(q) + '\n' for q in wlines]
            with open(save_file, 'a') as fp:
                fp.writelines(wlines)
        except:
            print("process error")
            pass
        pbar.update(1)

    
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--doc-list-path', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/dataset/doc_list.txt")
    parser.add_argument('--dataset-path', default='/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/Raw_data')
    parser.add_argument('--save', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/dataset/query_to_doc.json")
    args = parser.parse_args()  
    return args

if __name__ == '__main__':
    args = parse()

    doc_list = []
    doc_idxs = []
    with open(args.doc_list_path, 'r') as fp:
        doc_idxs = fp.readlines()
    
    for d in doc_idxs:
        path = os.path.join(args.dataset_path, f"{d[:-1]}.txt")
        with open(path, 'r') as fp:
            line = fp.readlines()[0]
        doc_list.append(line)
    doc_idxs = [int(d[:-1]) for d in doc_idxs]

    # doc_list = doc_list[:3]
    # doc_idxs = doc_idxs[:3]
    gen_query(doc_list, doc_idxs, args.save)