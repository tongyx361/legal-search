#! /bin/bash
docs_dirpath=$1
[ -z "${docs_dirpath}" ] && docs_dirpath="data/docs/fulltext_test_seg_docs"
idx_dirpath=$2
[ -z "${idx_dirpath}" ] && idx_dirpath="data/idxs/bm25_fulltext_zh_idxs"

if [ ! -d "${docs_dirpath}" ]; then
    python src/build_fulltext_docs.py
fi

python -m pyserini.index.lucene \
    --collection JsonCollection \
    --input "${docs_dirpath}" \
    --language zh \
    --index "${idx_dirpath}" \
    --generator DefaultLuceneDocumentGenerator \
    --threads 4 \
    --storePositions --storeDocvectors --storeRaw
