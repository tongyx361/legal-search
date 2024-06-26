from flask import Flask, request, jsonify
from backend import Retriever, RetrieverConfig, keyword_extract, DocEntry
import time, re
import multiprocessing

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


app = Flask(__name__)




@app.route('/query', methods=['GET'])
def query_process():
    try:
        data = request.json
        query: str = str(data.get('query')).strip()
        mode: str = str(data.get('mode')).strip() # accurate / blurred
        judge: str = str(data.get('judge')).strip() # 法官
        law: str = str(data.get('law')).strip() # 法条
        # 返回[beg, end)的记录
        beg: int = int(data.get('begin'))
        end: int = int(data.get('end'))
        if beg < 0:
            beg = 1000000
        if end < 0:
            end = 1000000
        

        precise = (mode == "accurate")

        buffer_key = (query, mode, judge, law)

        # process text query
        if len(query) > 0:
            doc_ids = retriever.advanced_retrieve([query], precise=precise)
        else:
            doc_ids = [[]]

        keywords = re.split(r'\s*(AND|OR|NOT)\s*', query)
        keywords = [p for p in keywords if p.strip()]

        # build DocEntry instances
        # filter judge and law
        query_results = []
        idxs = []

        for i, id in enumerate(doc_ids[0][beg:end]):
            try:
                res = DocEntry(config, id)
            except:
                print(f"building doc_entry error on id: {id}")
                continue
            if len(judge) > 0:
                judge_fit = retriever.compiler.filter(judge, res.judges)
                if not judge_fit:
                    continue
            if len(law) > 0:
                law_fit = retriever.compiler.filter(law, res.laws)
                if not law_fit:
                    continue
            res.set_highlights(keywords)
            query_results.append(res)
            idxs.append(i + beg)

        query_results = [q.serialize() for q in query_results]
        return jsonify({
            "results": query_results,
            "index": idxs,
            "total_num": len(doc_ids[0]),
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "unknown error"}), 401

@app.route('/query-judge')
def query_judge():
    try:
        data = request.json
        query: str = str(data.get('query')).strip()
        # 返回[beg, end)的记录
        beg: int = int(data.get('begin'))
        end: int = int(data.get('end'))
        if beg < 0:
            beg = 1000000
        if end < 0:
            end = 1000000

        doc_ids = retriever.query_judge([query])
        query_results = []
        idxs = []
        for i, id in enumerate(doc_ids[0][beg:end]):
            try:
                res = DocEntry(config, id)
            except:
                print(f"building doc_entry error on id: {id}")
                continue
            res.set_highlights([query])
            query_results.append(res)
            idxs.append(i + beg)

        query_results = [q.serialize() for q in query_results]
        return jsonify({
            "results": query_results,
            "index": idxs,
            "total_num": len(doc_ids[0]),
        }), 200 

    except Exception as e:
        print(e)
        return jsonify({"message": "unknown error"}), 401

@app.route('/query-laws')
def query_laws():
    try:
        data = request.json
        query: str = str(data.get('query')).strip()
        # 返回[beg, end)的记录
        beg: int = int(data.get('begin'))
        end: int = int(data.get('end'))
        if beg < 0:
            beg = 1000000
        if end < 0:
            end = 1000000

        doc_ids = retriever.query_law_article([query])
        query_results = []
        idxs = []
        for i, id in enumerate(doc_ids[0][beg:end]):
            try:
                res = DocEntry(config, id)
            except:
                print(f"building doc_entry error on id: {id}")
                continue
            res.set_highlights([query])
            query_results.append(res)
            idxs.append(i + beg)

        query_results = [q.serialize() for q in query_results]
        return jsonify({
            "results": query_results,
            "index": idxs,
            "total_num": len(doc_ids[0]),
        }), 200 

    except Exception as e:
        print(e)
        return jsonify({"message": "unknown error"}), 401

@app.route('/expand')
def expand():
    try:
        data = request.json
        query: str = str(data.get('query')).strip()
        output = retriever.query_expand([query])
        return jsonify({"results": output[0]}), 200

    except Exception as e:
        print(e)
        return jsonify({"message": "unknown error"}), 401






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678)
