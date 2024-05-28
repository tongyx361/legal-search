#! /bin/bash
model_id=$1
[ -z "${model_id}" ] && model_id="infgrad/stella-base-zh-v3-1792d"
model_dirname="${model_id//\//--}"
input_embeds_dirpath=$2
[ -z "${input_embeds_dirpath}" ] && input_embeds_dirpath="data/embeds/faiss_fulltext_test_seg_${model_dirname}_embeds"
output_idx_dirpath=$3
[ -z "${output_idx_dirpath}" ] && output_idx_dirpath="data/idxs/faiss_fulltext_test_seg_${model_dirname}_idxs"

python -m pyserini.index.faiss \
    --input "${input_embeds_dirpath}" \
    --output "${output_idx_dirpath}" \
    --dim 768 \
    --pq-m 192 \
    --hnsw \
    --pq
