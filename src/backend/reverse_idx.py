import json
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import MatrixSimilarity
import jieba

class ReverseIndex:
    def __init__(self, json_path: str) -> None:
        print("create reverse index")
        with open(json_path, 'r') as fp:
            self.data = json.load(fp)
        self.keys = list(self.data.keys())
        texts = [[w for w in list(jieba.cut_for_search(doc))] for doc in self.keys]
        self.dic = Dictionary(texts)
        corpus = [self.dic.doc2bow(t) for t in texts]
        self.model_tfidf = TfidfModel(corpus)
        self.index = MatrixSimilarity(self.model_tfidf[corpus])
    
    def _query(self, query: list[str], k: int = 10) -> None:
        outputs = []
        for q in query:
            q = list(jieba.cut_for_search(q))
            q_bow = self.dic.doc2bow(q)
            similarities = self.index[
                self.model_tfidf[q_bow]
            ]
            similarities = sorted(
                enumerate(similarities),
                key=lambda x: x[1],
                reverse=True
            )
            similarities = similarities[:k]
            outputs.append([s[0] for s in similarities])
        return outputs

    def _retrieve_only_get_key_str(self, query: list[str], k: int = 5):
        keys = self._query(query, 10)
        outputs = []
        for i, ks in enumerate(keys):
            output = []
            for k in ks:
                key_str = self.keys[k]
                if key_str != query[i] and not set(query[i]).isdisjoint(set(key_str)):
                    # print(key_str)
                    output.append(key_str)
            outputs.append(output[:k])
        return outputs

    
    def retrieve(self, query: list[str], k: int = 20):
        keys = self._query(query)
        outputs = []
        for ks in keys:
            output = []
            for k in ks:
                key_str = self.keys[k]
                output += self.data[key_str]
                # print(key_str, self.data[key_str])
                if len(output) > k:
                    break
            outputs.append(output)
        return outputs

            


if __name__ == '__main__':
    ridx = ReverseIndex("/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/法条倒排.json")

    output = ridx.retrieve(["婚姻法 第十条"])
    print(output)
