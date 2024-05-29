from openai import OpenAI
import argparse, re, os, json
from tqdm import tqdm

DOC_NUM = 1000

client = OpenAI()
template = "下面是一个法院判决书。请根据法院判决书，给出10个与案情本身相关的关键词，相关度从最相关到完全不相关排列。每个关键词以[S]开始，以换行结束。不需要输出序号。# 判决书：{query} # 关键词：\n"

key_temp = r'\[S\](.*?)(?=\n\[S\]|$)'


def generate_key_works(dir: str, save_file: str):

    file_list = os.listdir(dir)
    cnt = 0
    doc_key = {}
    pbar = tqdm(total=DOC_NUM)
    for file in file_list:
        path = os.path.join(dir, file)
        with open(path, 'r') as fp:
            try:
                lines = fp.readlines()
                line = lines[0]
            except:
                continue

            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个法院助手。请根据下面的要求完成回答。"},
                        {"role": "user", "content": template.format(query=line)}
                    ]
                )
            except:
                print(f"openai error on file {path}")
                continue

            gen_str = completion.choices[0].message.content
            extracetd_keywords = re.findall(key_temp, gen_str)
            key_words = [k.strip() for k in extracetd_keywords]
            if len(key_words) != 10:
                print(f"generation error on file {path}")
                continue
            doc_key = {}
            doc_key[int(file[:-4])] = key_words
            cnt += 1
            pbar.update(1)
            with open(save_file, 'a') as fp:
                ss = json.dumps(doc_key) + '\n'
                fp.writelines([ss])
            if cnt >= DOC_NUM:
                break
    return 

            




def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/Raw_data")
    parser.add_argument('--save', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/dataset/doc_to_key.json")
    args = parser.parse_args()  
    return args

if __name__ == '__main__':
    args = parse()
    generate_key_works(args.dir, args.save)