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
    ├── 法条倒排.json
    ├── 审判长倒排.json
    ├── keyword_ridx.json
    ├── docs
    ├── idxs
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

准备倒排索引：
```shell
python build_reverse_idx.py
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

https://cloud.tsinghua.edu.cn/d/c0f715a9078e4d38b36a/?p=%2F%E5%8F%B8%E6%B3%95%E6%90%9C%E7%B4%A2%E5%BC%95%E6%93%8E

## 后端样例

包含了后端所有功能的调用示例

```shell
python example_backend.py
```
