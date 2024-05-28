# Legal Search Engine

> Code for lab of **legal search engine** in *Introduction to Search Engine* (24S) course by Prof. Qingyao Ai @ THU-CST

## 文件结构

将 `Legal_data` 目录放置在 `data/` 下

```
.
└── data
    ├── doc_list.txt
    ├── kw2ids.json
    ├── query2id_list.jsonl
    └── Legal_data
```

## 环境配置

```shell
conda create -n ise python=3.10 -y
conda install -c conda-forge openjdk=21 maven -y
conda install pytorch==2.2.2 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install -r requirements.txt
```

## 构建索引

为 **1000 篇测试文档**构建索引，先准备文档：

完整文档：
```shell
python src/build_fulltext_docs.py \
    --ids_fpath data/test_ids.txt \
    --output_doc_home data/docs/fulltext_test_docs
```

分段文档：
```shell
python src/build_fulltext_docs.py \
    --ids_fpath data/test_ids.txt \
    --output_doc_home data/docs/fulltext_test_seg_docs \
    --seg_len 512
```

### BM25 （中文）

```shell
bash src/build_bm25_idx_zh.sh
```

### FAISS

```shell
bash src/encode.sh
bash src/build_faiss_idx.sh
```

## 搜索

- 单关键词搜索：`src/search.ipynb`（测试结果为 BM25 最好，有待进一步验证）
- 自然语言查询搜索：`src/search_query.ipynb`（测试结果为 BM25+分段最好，有待进一步验证）