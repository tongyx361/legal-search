from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, re
# from .retriever import RetrieverConfig

DEVICE = 'mps'
MODEL_PATH = "Qwen/Qwen1.5-0.5B-Chat"

pattern = r'[\u4e00-\u9fff]+'

class RetrieverConfig:
    def __init__(self,
        doc_path: str = "",
        doc_ids_path: str = "",
        coarse_model_path: str = "",
        law_article_revert_index_path: str = "",
        judge_revert_index_path: str = "",
        expander_model_path: str = "",
        expander_device: str = "mps",
        max_doc_num: int = 100,
        seg_len: int = 512,
    ) -> None:
        self.doc_path = doc_path
        self.coarse_model_path = coarse_model_path
        self.max_doc_num = max_doc_num
        self.seg_len = seg_len
        self.doc_ids_path = doc_ids_path
        self.law_article_revert_index_path = law_article_revert_index_path
        self.judge_revert_index_path = judge_revert_index_path
        self.expander_model_path = expander_model_path
        self.expander_device = expander_device

class QueryExpander:
    def __init__(self) -> None:
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map=DEVICE, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    # def __init__(self, config: RetrieverConfig):
    #     breakpoint()
    #     self.model = AutoModelForCausalLM.from_pretrained(config.expander_model_path, device_map=config.expander_device, trust_remote_code=True)
    #     self.tokenizer = AutoTokenizer.from_pretrained(config.expander_model_path)
    #     breakpoint()
    
    def expand(self, query: list[str]):
        outputs = []
        for q in query:
            msg = [
                {
                    "role": "user",
                    "content": f'现在我会给你一个法律搜索引擎的搜索词。你需要扩展出最相关的5个法律词语。搜索词：{q}'
                }
            ]
            input_ids = self.tokenizer.apply_chat_template(msg, tokenize=True, return_tensors='pt').to(DEVICE)
            attention_mask = torch.ones_like(input_ids)
            input_len = input_ids.shape[-1]
            output = self.model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=128)
            output_str = self.tokenizer.decode(output[0, input_len:])
            matches = re.findall(pattern, output_str)
            outputs.append(
                [m for m in matches if m != q][:5]
            )
        return outputs

        


if __name__ == '__main__':
    query_expander = QueryExpander()
    output = query_expander.expand(
        ["武汉"]
    )
    print(output)
    output = query_expander.expand(
        ["土地"]
    )
    print(output)
    output = query_expander.expand(
        ["著作权"]
    )
    print(output)
    output = query_expander.expand(
        ["嫖娼"]
    )
    print(output)
    output = query_expander.expand(
        ["婚姻法"]
    )
    print(output)
    output = query_expander.expand(
        ["物权法"]
    )
    print(output)
    output = query_expander.expand(
        ["故意杀人罪"]
    )
    print(output)