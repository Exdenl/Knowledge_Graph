import os
import json
import re

# 获取当前脚本所在目录的上一级目录（项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'turing_raw.txt')
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, 'data', 'triples.json')

def read_corpus(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_information(text):
    """
    模拟NLP流水线进行实体、关系抽取和实体消歧
    """
    triples = []
    
    # 1. 实体抽取 & 关系抽取 (使用正则和规则匹配模拟)
    # 抽取出生和死亡日期
    birth_death_match = re.search(r'（.*?，(.*?)—(.*?)）', text)
    if birth_death_match:
        triples.append(["艾伦·图灵", "出生日期", birth_death_match.group(1)])
        triples.append(["艾伦·图灵", "逝世日期", birth_death_match.group(2)])

    # 抽取头衔
    if "计算机科学之父" in text:
        triples.append(["艾伦·图灵", "被誉为", "计算机科学之父"])
    if "人工智能之父" in text:
        triples.append(["艾伦·图灵", "被誉为", "人工智能之父"])
        
    # 抽取教育经历
    if "剑桥大学国王学院" in text:
        triples.append(["艾伦·图灵", "本科就读", "剑桥大学国王学院"])
    if "普林斯顿大学" in text:
        triples.append(["艾伦·图灵", "博士就读", "普林斯顿大学"])
        
    # 抽取成就
    if "Enigma" in text:
        triples.append(["艾伦·图灵", "破解系统", "Enigma (恩尼格玛)"])
        triples.append(["Enigma (恩尼格玛)", "归属", "德国军方"])
    if "图灵测试" in text:
        triples.append(["艾伦·图灵", "提出理论", "图灵测试"])
        
    # 2. 实体消歧 (Entity Disambiguation) 展示逻辑
    # 文本中出现了“苹果”，需要判断是“苹果公司”还是“水果苹果”
    if "苹果" in text:
        context_around_apple = text[text.find("苹果")-10 : text.find("苹果")+10]
        # 根据上下文包含“食用”、“氰化物”等词来进行消歧
        if "食用" in context_around_apple or "氰化物" in context_around_apple:
            resolved_entity = "含有氰化物的毒苹果(水果)"
        elif "公司" in context_around_apple or "手机" in context_around_apple:
            resolved_entity = "苹果公司(企业)"
        else:
            resolved_entity = "苹果(未知实体)"
            
        triples.append(["艾伦·图灵", "死因", f"食用{resolved_entity}"])

    return triples

def main():
    print("1. 读取原始语料...")
    text = read_corpus(DATA_PATH)
    
    print("2. 执行实体抽取、关系抽取与消歧...")
    triples = extract_information(text)
    
    print(f"3. 抽取完成，共获得 {len(triples)} 个知识三元组。")
    for t in triples:
        print(f"   - {t}")
        
    print("4. 将结构化数据保存为 JSON...")
    # 确保 data 目录存在
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(triples, f, ensure_ascii=False, indent=4)
    print(f"保存成功：{OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()