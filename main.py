# main.py
import os
import json
from src.crawler import WikiCrawler  # 统一使用类名导入
from src.model_trainer import ModelTrainer
from src.inference_engine import Extractor
from src.knowledge_fusion import KnowledgeFusion
from src.visualizer import generate_graph

def run_pipeline():
    print("="*50)
    print(" 🚀 知识图谱大型工程 Pipeline 系统启动")
    print("="*50)

    # --- 1. 数据采集阶段 ---
    keywords = ["艾伦·图灵", "约翰·冯·诺伊曼", "计算机科学", "人工智能", 
                "恩尼格玛密码机", "剑桥大学", "普林斯顿大学", "图灵奖"]
    crawler = WikiCrawler()
    print(f"阶段 [1/5]: 正在通过 Wikipedia 构建大规模语料库...")
    for kw in keywords:
        file_path = f"data/raw/{kw}.txt"
        if not os.path.exists(file_path):
            crawler.fetch(kw)
    
    # --- 2. 模型训练阶段 ---
    print("\n阶段 [2/5]: 正在基于全量语料训练机器学习模型...")
    trainer = ModelTrainer()
    trainer.train() 

    # --- 3. 知识抽取阶段 ---
    print("\n阶段 [3/5]: 正在执行自动化知识挖掘...")
    extractor = Extractor()
    all_raw_triples = []
    
    if not os.path.exists("data/raw"):
        print("错误：data/raw 目录不存在，请检查爬虫。")
        return

    raw_files = [f for f in os.listdir("data/raw") if f.endswith(".txt")]
    for file_name in raw_files:
        with open(os.path.join("data/raw", file_name), 'r', encoding='utf-8') as f:
            text = f.read()
            triples = extractor.extract(text)
            all_raw_triples.extend(triples)
    print(f"   初步挖掘出 {len(all_raw_triples)} 个原始知识三元组。")

    # --- 4. 知识融合阶段 (处理 Mathison 等碎片) ---
    print("\n阶段 [4/5]: 执行知识融合与实体消歧...")
    fusion = KnowledgeFusion()
    final_triples = fusion.fuse(all_raw_triples)
    print(f"   清洗完成，保留高质量连接对: {len(final_triples)} 个。")

    # --- 5. 可视化阶段 ---
    print("\n阶段 [5/5]: 生成可视化图谱...")
    if len(final_triples) > 0:
        os.makedirs("data/processed", exist_ok=True)
        with open("data/processed/triples.json", 'w', encoding='utf-8') as f:
            json.dump(final_triples, f, ensure_ascii=False, indent=4)
        generate_graph(final_triples, "output/output_graph.html")
    else:
        print("警告：未提取到有效数据。")

    print("\n" + "="*50)
    print(" 任务圆满完成 请查看 output_graph.html")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()