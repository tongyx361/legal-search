from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, re

DEVICE = 'mps'
MODEL_PATH = "Qwen/Qwen1.5-0.5B-Chat"

pattern = r'[\u4e00-\u9fff]+'

class QueryExpander:
    def __init__(self) -> None:
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map=DEVICE, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    
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