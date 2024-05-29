import os, re, json, argparse
from tqdm import tqdm


def post_process(path, save_dir: str, doc_list_path: str):

    key_to_doc = {}
    doc_list = []

    with open(path, 'r') as fp:
        lines = fp.readlines()
    
    for line in tqdm(lines):
        ent = json.loads(line)
        for doc, v in ent.items():
            doc_list.append(doc)
            for k in v:
                if k not in key_to_doc:
                    key_to_doc[k] = []
                key_to_doc[k].append(doc)
    
    with open(save_dir, 'w') as fp:
        json.dump(key_to_doc, fp)
    doc_list.sort()
    with open(doc_list_path, 'w') as fp:
        doc_list = [str(d) + '\n' for d in doc_list]
        fp.writelines(doc_list)



def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/dataset/doc_to_key.json")
    parser.add_argument('--save-dir', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/dataset/key_to_doc.json")
    parser.add_argument('--doc-list-path', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/dataset/doc_list.txt")
    args = parser.parse_args()  
    return args

if __name__ == '__main__':
    args = parse()
    post_process(args.path, args.save_dir, args.doc_list_path)