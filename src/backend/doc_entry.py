try:
    from .retriever import RetrieverConfig
    from .keyword_extract import keyword_extract
except:
    from retriever import RetrieverConfig
    from keyword_extract import keyword_extract
import os, re


full_pattern = r'nameCN="全文" oValue="([^"]*)"'
法条格式 = r'FT value="([^"]*)"'
审判长格式 = r'FGRYXM nameCN="法官人员姓名" value="([^"]*)"'
title_pattern = r'WS nameCN="文首" value="([^"]*)"'


class DocEntry:
    # unsafe
    def __init__(self, config: RetrieverConfig, doc_id: int) -> None:
        doc_path = config.doc_path
        doc_path = os.path.join(doc_path, f"{doc_id}.xml")
        with open(doc_path, 'r') as fp:
            lines = fp.readlines()
            lines = "".join(lines)
        
        self.full = re.findall(full_pattern, lines)[0]
        self.title = re.findall(title_pattern, lines)[0]
        self.laws = re.findall(法条格式, lines)
        self.judges = re.findall(审判长格式, lines)
        self.keywords = keyword_extract(self.full)
        self.highlights = []
    

    def set_highlights(self, keys: list[str]):
        for k in keys:
            if k in self.full:
                self.highlights.append(k)

    def serialize(self):
        return {
            "full": self.full,
            "title": self.title,
            "laws": self.laws,
            "judges": self.judges,
            "keywords": self.keywords,
            "highlights": self.highlights,
        }


        