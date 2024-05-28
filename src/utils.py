import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from tqdm import tqdm

PROJ_HOME = os.environ.get("PROJ_HOME", Path(__file__).resolve().parents[1])

DATA_HOME = PROJ_HOME / "data"

IDX_HOME = DATA_HOME / "idxs"

DOC_HOME = DATA_HOME / "docs"

LEGAL_DATA_DIRPATH = DATA_HOME / "Legal_data"

KW2IDS_FPATH = DATA_HOME / "kw2ids.json"
QUERY2ID_LIST_FPATH = DATA_HOME / "query2id_list.jsonl"


def load_ets(
    xml_dirpath: Path, xml_ids: list[int] = None
) -> list[tuple[int, ET.ElementTree]]:
    legal_id_et_pairs = []
    if xml_ids is None:
        legal_et_fpaths = list(xml_dirpath.glob("*.xml"))
    else:
        legal_et_fpaths = [xml_dirpath / f"{doc_id}.xml" for doc_id in xml_ids]

    for legal_et_fpath in tqdm(legal_et_fpaths, desc="Loading XMLs"):
        try:
            id = legal_et_fpath.stem
            et = ET.parse(legal_et_fpath)
            legal_id_et_pairs.append((id, et))
        except Exception:
            # print(f"Failed to load {legal_et_fpath}")
            pass

    print(f"Successfully loaded {len(legal_id_et_pairs)} ETs")
    return legal_id_et_pairs


def get_legal_id_fulltext_pairs(
    legal_id_et_pairs: list[tuple[str, ET.ElementTree]]
) -> list[tuple[str, str]]:
    legal_id_fulltext_pairs = []
    for legal_id, legal_et in tqdm(legal_id_et_pairs):
        root = legal_et.getroot()
        fulltext = None
        for child in root:
            if child.tag == "QW":
                fulltext = child.attrib["oValue"]
        if fulltext:
            legal_id_fulltext_pairs.append((legal_id, fulltext))
        else:
            print(f"Failed to find fulltext for {legal_id}")
    return legal_id_fulltext_pairs
