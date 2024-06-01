from backend import Retriever, RetrieverConfig, keyword_extract
import time

# 设置config
config = RetrieverConfig(
    doc_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/Legal_data", # 所有.xml文档的文件夹
    doc_ids_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/test_ids.txt", # 包含文档id的文件
    coarse_model_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/idxs/bm25_fulltext_zh_idxs", # bm25 index
    law_article_revert_index_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/法条倒排.json", # 法条倒排.json
    judge_revert_index_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/审判长倒排.json", # 审判长倒排.json
    keyword_revert_index_path="/Users/huang-yx/Desktop/2024Spr/SearchEngine/legal-search/data/keyword_ridx.json",
    expander_model_path="Qwen/Qwen1.5-0.5B-Chat", # 查询扩展模型路径或hf标识
    expander_device="mps", # 查询扩展模型设备，建议cuda或mps
)



retriever = Retriever(config)
extractor = keyword_extract


# 检索推荐与扩展
output = retriever.query_expand(["土地"])
print(output)

# 关键词检索
output = retriever.retrieve(
    ["土地", "著作权"]
)
print(output)

# 精确检索
output = retriever.retrieve(
    ["许学江"], precise=True
)
print(output)

# 长文本检索
output = retriever.retrieve(
    ["歌曲创作的著作权被侵犯了"]
)
print(output)

# 类似案例检索
output = retriever.retrieve(
    ['许学江']
)
doc_id = output[0][0]
doc = retriever._get_doc_by_ids(doc_id)
output = retriever.retrieve(
    [doc]
)
print(output)

# 生成标签
key_words = extractor(doc)
print(key_words)


# 检索法官
output = retriever.query_judge(["姚兵兵"])
print(output)

# 检索法律
output = retriever.query_law_article(["婚姻法 十年"])
print(output)

# 高级检索
output = retriever.advanced_retrieve(["(土地 or 著作权) AND NOT 武汉"])
print(output)




