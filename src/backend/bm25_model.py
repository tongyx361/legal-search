import os
import json
import random
import numpy as np
from collections import defaultdict

from pyserini.search.lucene import LuceneSearcher
from pyserini.search import FaissSearcher
from pyserini.search.faiss._searcher import AutoQueryEncoder

# from ..utils import *
import time

class BM25Model:
    def __init__(
        self,
        index_dir: str = None,
        n_threads: int = 16,
    ):
        self.index_dir = index_dir
        self.n_threads = n_threads

        self.searcher = LuceneSearcher(self.index_dir)
        self.searcher.set_language("zh")

    def batch_search(self, queries: str, k: int) -> dict[str, list]:
        print(f"Searching for {len(queries)} queries...")
        search_start = time.time()
        query2hits = self.searcher.batch_search(
            queries, queries, k=k, threads=self.n_threads
        )
        search_timecost = time.time() - search_start
        print(
            f"Time per query: {search_timecost / len(queries):.4f} s (= {search_timecost:.4f}/{len(queries)})"
        )
        return query2hits

    def retrieve(self, queries: list[str], k: int) -> list[tuple[str, list[str]]]:
        query2hits = self.batch_search(queries, k)
        query_hit_ids_pairs = []
        for query, hits in query2hits.items():
            hit_ids = [hit.docid for hit in hits]
            if len(hit_ids) > 0 and "-" in hit_ids[0]:
                hit_ids = [hit.docid.split("-")[0] for hit in hits]
                # Deduplicate but keep the order
                hit_ids = list(dict.fromkeys(hit_ids))
            query_hit_ids_pairs.append(hit_ids)

        return query_hit_ids_pairs

if __name__ == '__main__':
    model = BM25Model("/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/idxs/bm25_fulltext_zh_idxs")
    output = model.retrieve(["著作权", "土地"], 30)