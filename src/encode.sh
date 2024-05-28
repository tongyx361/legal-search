#! /bin/bash
device=$1
[ -z "${device}" ] && device="cuda:0"
batch_size=$2
[ -z "${batch_size}" ] && batch_size=64
model_id=$3
[ -z "${model_id}" ] && model_id="infgrad/stella-base-zh-v3-1792d"
model_dirname="${model_id//\//--}"
docs_dirpath=$4
[ -z "${docs_dirpath}" ] && docs_dirpath="data/docs/fulltext_test_seg_docs"
embed_dirpath=$5
[ -z "${embed_dirpath}" ] && embed_dirpath="data/embeds/faiss_fulltext_test_seg_${model_dirname}_embeds"

python -m pyserini.encode \
    input --corpus "${docs_dirpath}" \
    output --embeddings "${embed_dirpath}" \
    --to-faiss \
    encoder --encoder "${model_id}" \
    --encoder-class "auto" \
    --max-length 512 \
    --dimension 768 \
    --pooling "mean" \
    --batch-size "${batch_size}" \
    --device "${device}" \
    --fp16

# bs=64 -> 256seq/s
