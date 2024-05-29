from bm25_model import BM25Model
import os, re
from collections import Counter

def reorder_ids(nums):
    count = Counter(nums)
    fo = {}
    for i, val in enumerate(nums):
        if val not in fo:
            fo[val] = i
    sorted_nums = sorted(set(nums), key=lambda x: (-count[x], fo[x]))
    breakpoint()
    return sorted_nums

pattern = r'nameCN="全文" oValue="([^"]*)"'
class RetrieverConfig:
    def __init__(self,
        doc_path: str = "",
        coarse_model_path: str = "",
        max_doc_num: int = 100,
        seg_len: int = 512,
    ) -> None:
        self.doc_path = doc_path
        self.coarse_model_path = coarse_model_path
        self.max_doc_num = max_doc_num
        self.seg_len = seg_len


class Retriever:
    def __init__(self, config: RetrieverConfig) -> None:
        self.config = config
        self.coarse_model = BM25Model(config.coarse_model_path)

        self.max_doc_num = config.max_doc_num
        self.doc_path = config.doc_path
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

    def _retrieve_text(self, query: list[str]) -> list[str]:
        outputs = self.retrieve(query)
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

    def retrieve(self, query: list[str]) -> list[str]:
        outputs = []
        for q in query:
            out = []
            for i in range(0, len(q), self.config.seg_len):
                out += self._retrieve_without_length_check([q[i: i+self.config.seg_len]])[0]
            out = reorder_ids(out)[:self.max_doc_num]
            outputs.append(out)
        return outputs
            


if __name__ == '__main__':
    config = RetrieverConfig(
        doc_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/Legal_data",
        coarse_model_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/idxs/bm25_fulltext_zh_idxs",
    )

    retriever = Retriever(config)

    # output = retriever._retrieve_text(["著作权", "土地"])
    output = retriever._retrieve_text(['''浙江省高级人民法院 民事判决书 （2011）浙知终字第143号 上诉人（原审原告）北京天籁印象文化传播有限公司。 法定代表人许琳。 委托代理人（特别授权代理）王潭海。 被上诉人（原审被告）杭州淞木文化艺术策划有限公司。 法定代表人华毅。 委托代理人（特别授权代理）施海寅、颜丹丹。 上诉人北京天籁印象文化传播有限公司（以下简称天籁公司）因不当得利纠纷一案，不服浙江省杭州市中级人民法院（2010）浙杭知初字第893号民事判决，向本院提起上诉。本院于2011年7月6日立案受理后，依法组成合议庭，并于同年8月23日公开开庭进行了审理。上诉人天籁公司的委托代理人王潭海、被上诉人杭州淞木文化艺术策划有限公司（以下简称淞木公司）的委托代理人颜丹丹到庭参加诉讼。本案现已审理终结。 原判认定：2010年4月25日，天籁公司和淞木公司签署《音乐作品授权使用协议》，约定的内容包括：1．淞木公司作为音乐内容的提供方，拥有《附件2》中所有歌曲独立、完整的词、曲全部著作财产权、录音录像邻接权及其他相关邻接权，拥有《附件2》中10首歌曲的录音录像邻接权及其他相关邻接权。现授权天籁公司在无线增值服务领域，互联网应用服务领域及终端内置服务领域进行宣传、推广和使用，达到互利互赢一事与天籁公司进行本协议的''', "土地征收"
    ])

    breakpoint()


