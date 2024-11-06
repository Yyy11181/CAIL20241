from collections import defaultdict
import json
import re
import ast

# 读取原始数据
with open("cpwsslsc/doc/generated_predictions-fu.jsonl", "r", encoding="utf-8") as f:
    data1 = [json.loads(line) for line in f]

with open("test_fu.json", "r", encoding="utf-8") as f:
    data2 = [json.loads(line) for line in f]
    data2 = {re.search(r"案件编号:(\d+)", item["instruction"]).group(1): item["input"] for item in data2}


# 使用defaultdict来暂存合并后的数据
merged_data = defaultdict(dict)

for item in data1:
    #使用正则表达式提取案件编号
    match = re.search(r"案件编号:(\d+)", item["prompt"])
    data_id = match.group(1)
    
    merged_data[data_id]["id"] = data_id
    merged_data[data_id]["fact"] = data2[data_id].split("事实部分：", 1)[-1]
    
    # 将每个部分的 predict 放入 answers 中对应的 key
    if "判决结果" in item["predict"]:
        merged_data[data_id]["judgement"] = item["predict"].split("判决结果部分：", 1)[-1]
    elif "案由部分" in item["predict"]:
        merged_data[data_id]["cause"] = ast.literal_eval(re.search(r"案由部分：(\[.*?\])", item["predict"]).group(1))
    elif "判决说理" in item["predict"]:
        merged_data[data_id]["reasoning"] = item["predict"].split("判决说理部分：", 1)[-1]
    elif "伦理或法理" in item["predict"]:
        merged_data[data_id]["ethics_or_jurisprudence"] = ast.literal_eval(item["predict"].split("伦理或法理部分：", 1)[-1])

# 转换为最终合并后的数据列表，且仅保留指定字段
final_data = []
for data_id, fields in merged_data.items():
    # 只保留需要的字段
    final_item = {
        "id": fields.get("id", ""),
        "fact": fields.get("fact", ""),
        "reasoning": fields.get("reasoning", ""),
        "judgement": fields.get("judgement", ""),
        "cause": fields.get("cause", ""),
        # "ethics_or_jurisprudence": fields.get("ethics_or_jurisprudence", "")
    }
    final_data.append(final_item)

#写入json文件
with open("cpwsslsc/doc/test-fu-new.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)
    
