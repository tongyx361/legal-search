import argparse, re, os
import xml.etree.ElementTree as ET
from tqdm import tqdm


pattern = r'nameCN="全文" oValue="([^"]*)"'
def process(from_path: str, to_path: str):

    os.makedirs(to_path, exist_ok=True)

    file_list = os.listdir(from_path)

    for file in tqdm(file_list):
        file_path = os.path.join(from_path, file)
        if not file.endswith(".xml"):
            continue
        with open(file_path, 'r') as fp:
            lines = fp.readlines()
        for line in lines:
            match = re.findall(pattern, line)
            if len(match) > 0:
                break
        save_path = os.path.join(to_path, file[:-4] + ".txt")
        with open(save_path, 'w') as fp:
            fp.writelines(match)


    return


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-path', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/Legal_data")
    parser.add_argument('--to-path', type=str, default="/Users/huang-yx/Desktop/2024Spr/SearchEngine/Project/Raw_data")
    args = parser.parse_args()  
    return args

if __name__ == "__main__":
    args = parse()
    process(args.from_path, args.to_path)
