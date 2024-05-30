from bm25_model import BM25Model
from query_compile import QueryCompiler
import os, re
from collections import Counter

def reorder_ids(nums):
    count = Counter(nums)
    fo = {}
    for i, val in enumerate(nums):
        if val not in fo:
            fo[val] = i
    sorted_nums = sorted(set(nums), key=lambda x: (-count[x], fo[x]))
    return sorted_nums

pattern = r'nameCN="全文" oValue="([^"]*)"'
class RetrieverConfig:
    def __init__(self,
        doc_path: str = "",
        doc_ids_path: str = "",
        coarse_model_path: str = "",
        max_doc_num: int = 100,
        seg_len: int = 512,
    ) -> None:
        self.doc_path = doc_path
        self.coarse_model_path = coarse_model_path
        self.max_doc_num = max_doc_num
        self.seg_len = seg_len
        self.doc_ids_path = doc_ids_path


class Retriever:
    def __init__(self, config: RetrieverConfig) -> None:
        self.config = config
        self.coarse_model = BM25Model(config.coarse_model_path)

        self.max_doc_num = config.max_doc_num
        self.doc_path = config.doc_path
        with open(config.doc_ids_path, 'r') as fp:
            lines = fp.readlines()
            all_ids = [int(l.strip()) for l in lines]
        self.compiler = QueryCompiler(all_ids, self.retrieve)
        return
    
    def _get_doc_by_ids(self, doc_id: int) -> str:
        try:
            doc_path = os.path.join(self.doc_path, f"{doc_id}.xml")
            with open(doc_path, 'r') as fp:
                lines = fp.readlines()
                lines = "".join(lines)
            doc_str = re.findall(pattern, lines)
            if len(doc_str) == 0:
                return None
            else:
                return doc_str[0]
        except:
            print(f"cannot fine document {doc_id}")
            return None

    def _retrieve_text(self, query: list[str], precise=False, advance=False) -> list[str]:
        if not advance:
            outputs = self.retrieve(query, precise=precise)
        else:
            outputs = self.advanced_retrieve(query)
        docs = []
        for ids in outputs:
            dl = []
            for id in ids:
                doc_str = self._get_doc_by_ids(id)
                if doc_str is not None:
                    dl.append(doc_str)
            docs.append(dl)
        return docs

    def _retrieve_without_length_check(self, query: list[str]) -> list[str]:
        # coarse retrieve
        outputs = self.coarse_model.retrieve(query, self.max_doc_num)
        # rerank
        # TODO
        return outputs

    def retrieve(self, query: list[str], precise=False) -> list[str]:
        outputs = []
        for q in query:
            out = []
            for i in range(0, len(q), self.config.seg_len):
                out += self._retrieve_without_length_check([q[i: i+self.config.seg_len]])[0]
            out = reorder_ids(out)[:self.max_doc_num]
            if precise:
                _out = []
                for id in out:
                    doc_str = self._get_doc_by_ids(id)
                    if q in doc_str:
                        _out.append(id)
                out = _out
            outputs.append(out)
        return outputs

    def advanced_retrieve(self, query: list[str]) -> list[str]:
        outputs = []
        for q in query:
            outputs.append(self.compiler.execute(q))
        return outputs


            


if __name__ == '__main__':
    config = RetrieverConfig(
        doc_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/Legal_data",
        doc_ids_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/test_ids.txt",
        coarse_model_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/idxs/bm25_fulltext_zh_idxs",
    )

    retriever = Retriever(config)

    # output = retriever._retrieve_text(["著作权", "土地"])
    # 武汉 土地
    output = retriever._retrieve_text([
        "(土地 or 著作权) AND NOT 武汉"
    ], advance=True)

    breakpoint()


