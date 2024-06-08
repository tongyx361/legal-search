import os

path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/Legal_data"

out_path = "/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/test_ids.txt"

file_list = os.listdir(path=path)

file_list = [f[:-4] + '\n' for f in file_list]
with open(out_path, 'w') as fp:
    fp.writelines(file_list)