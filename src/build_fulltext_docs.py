import argparse
import json
from pathlib import Path

from tqdm import tqdm

from utils import *

parser = argparse.ArgumentParser()
parser.add_argument("-x", "--xml_home", type=str, default=LEGAL_DATA_DIRPATH)
parser.add_argument("-i", "--ids_fpath", type=str, default=None)
parser.add_argument(
    "-o", "--output_doc_home", type=str, default=DOC_HOME / "fulltext_seg_docs"
)
parser.add_argument("-s", "--seg_len", type=int, default=0)
args = parser.parse_args()


if args.ids_fpath:
    with open(args.ids_fpath, "r") as f:
        doc_ids = [int(line.strip()) for line in f]
else:
    doc_ids = None

legal_id_et_pairs = load_ets(args.xml_home, xml_ids=doc_ids)
legal_id_fulltext_pairs = get_legal_id_fulltext_pairs(legal_id_et_pairs)
legal_id2fulltext = dict(legal_id_fulltext_pairs)


args.output_doc_home = Path(args.output_doc_home)

args.output_doc_home.mkdir(exist_ok=True)


for legal_id, fulltext in tqdm(legal_id_fulltext_pairs, desc="Writing docs"):
    segs = [
        fulltext[i : i + args.seg_len] for i in range(0, len(fulltext), args.seg_len)
    ]
    for i, seg in enumerate(segs):
        seg_id = f"{legal_id}-{i}"
        with open(args.output_doc_home / f"{seg_id}.json", "w") as f:
            f.write(json.dumps({"id": seg_id, "contents": seg}))
