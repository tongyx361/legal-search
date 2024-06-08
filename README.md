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

# APIs

均为 GET 请求

全部使用json来传参，中文使用unicode-escape编码

### `/query`

综合检索的一个接口。可以支持高级检索表达式和过滤检索。支持分页。

- 输入：字典
    - `query`：字符串，检索字符串，可以是关键词或长文本，也可以是高级检索表达式
    - `mode`：字符串，只能为`accurate`或`blurred`，表示精准搜索或者模糊搜索
    - `judge`：字符串，法官名字，支持高级检索表达式，过滤功能。不过滤时传`""`
    - `law`：字符串，法条名字，支持高级检索表达式，过滤功能。不过滤时传`""`
    - `index`：整数，当前最后一条文书的过滤前标号
    - `ndoc`：整数，至多返回可用文书的条数

- 返回值：
    - `doc`：字典，输入 `index` 后第一条可用的文书的详情
        - `full`：字符串，全文
        - `title`：字符串，标题
        - `laws`：列表，其中每个元素都是字符串。法条
        - `judges`：列表，其中每个元素都是字符串。法官
        - `keywords`：列表，其中每个元素都是字符串。关键词
        - `highlights`：列表，其中每个元素都是字符串。需要高亮的词
    - `index`：整数，表示返回的文书在该搜索输入下精确过滤前的标号
    - `total_num`：整数，这个搜索在精确过滤前总共有多少个文书

- 例子
    - 语义：模糊搜索`婚姻法`，按照法官为`韦威助`来过滤，不过滤法条，返回过滤前标号从`20`开始（包括）`20` 的文书的下 10 条可用文书。
    ```json
    {
        "query": "婚姻法",
        "mode": "blurred",
        "judge": "韦威助",
        "law": "",
        "index": 20,
        "ndoc": 10
    }
    ```

### `/query-judge`

按照法官的名字检索，支持模糊检索，不支持高级检索，支持分页。

- 字段
    - `query`：字符串，法官名
    - `begin`：整数，用来分页。起始的编号
    - `end`：整数，用来分页。终止的编号

- 返回值
    - `results`：列表，每个法律文书的详情。每个元素是一个字典
        - `full`：字符串，全文
        - `title`：字符串，标题
        - `laws`：列表，其中每个元素都是字符串。法条
        - `judges`：列表，其中每个元素都是字符串。法官
        - `keywords`：列表，其中每个元素都是字符串。关键词
        - `highlights`：列表，其中每个元素都是字符串。需要高亮的词
    - `index`：列表，其中每个元素都是整数。表示返回的文书在该搜索输入下的标号，用来分页
    - `total_num`：整数，这个搜索总共有多少个文书

- 例子
    - 语义：模糊搜索法官为`韦威助`的法律文书。返回过滤前标号从`20`开始（包括）`20` 的文书的下 10 条可用文书。
    ```json
    {
        "query": "韦威助",
        "index": 20,
        "ndoc": 10
    }
    ```

### `/query-laws`

按照法条检索，支持模糊检索，不支持高级检索，支持分页。

- 字段
    - `query`：字符串，法条名
    - `begin`：整数，用来分页。起始的编号
    - `end`：整数，用来分页。终止的编号

- 返回值
    - `results`：列表，每个法律文书的详情。每个元素是一个字典
        - `full`：字符串，全文
        - `title`：字符串，标题
        - `laws`：列表，其中每个元素都是字符串。法条
        - `judges`：列表，其中每个元素都是字符串。法官
        - `keywords`：列表，其中每个元素都是字符串。关键词
        - `highlights`：列表，其中每个元素都是字符串。需要高亮的词
    - `index`：列表，其中每个元素都是整数。表示返回的文书在该搜索输入下的标号，用来分页
    - `total_num`：整数，这个搜索总共有多少个文书

- 例子
    - 语义：模糊搜索法条为`婚姻法`的法律文书。返回过滤前标号从`20`开始（包括）`20` 的文书的下 10 条可用文书。
    ```json
    {
        "query": "婚姻法",
        "index": 20,
        "ndoc": 10
    }
    ```

### `/expand`

搜索扩展和推荐

- 字段
    - `query`：字符串，需要扩展的检索

- 返回值
    - `results`：列表，每个元素是字符串，扩展出的搜索选项。

- 例子
    - 语义：扩展和推荐`婚姻`的检索词
    ```json
    {
        "query": "婚姻",
    }
    ```
    

