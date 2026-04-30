# main.py
import os
import json
import time
from src.crawler import WikiCrawler
from src.model_trainer import ModelTrainer
from src.inference_engine import Extractor
from src.knowledge_fusion import KnowledgeFusion
from src.visualizer import generate_graph

def run_pipeline():
    start_time = time.time()
    
    print("="*70)
    print(" 🚀 艾伦·图灵 领域知识图谱构建系统 (KG Pipeline) 启动")
    print("="*70)

    # --- 1. 数据采集阶段 ---
    print("\n[阶段 1/5]: 知识获取 (Data Acquisition) --------------------------")
    
    # 我们结合了你原版 crawler 中的词条，并补充了一些高质量的领域核心词
    # 这样模型能学到更多的语法特征，图谱也会更庞大
    keywords =[
        "艾伦·图灵", "约翰·冯·诺伊曼", "计算机科学", "人工智能", 
        "恩尼格玛密码机", "剑桥大学", "普林斯顿大学", "图灵奖",
        "布莱切利园", "密码学", "图灵机",
        "停机问题",  "库尔特·哥德尔", "曼彻斯特大学", "数理逻辑"
    ]
    
    crawler = WikiCrawler()
    
    for kw in keywords:
        file_path = f"data/raw/{kw}.txt"
        # 缓存机制：如果本地已经存在这个 txt 文件，就不再走网络请求，直接跳过
        # 这样即使中途网络断开，下次运行也能直接接着爬
        if not os.path.exists(file_path):
            crawler.fetch(kw)
            # 每次请求后稍微停顿 1 秒，防止被维基百科封 IP
            time.sleep(1)
        else:
            print(f"   [缓存] 词条 '{kw}' 已存在于 data/raw/，跳过爬取。")
    
    # --- 2. 模型训练阶段 ---
    print("\n[阶段 2/5]: 序列标注模型训练 (NER Training) --------------------")
    trainer = ModelTrainer()
    trainer.train() 

    # --- 3. 知识抽取阶段 ---
    print("\n[阶段 3/5]: 自动化信息挖掘 (Information Extraction) --------------")
    extractor = Extractor()
    all_raw_triples =[]
    
    if not os.path.exists("data/raw"):
        print("❌ 错误：data/raw 目录不存在，请检查爬虫。")
        return

    raw_files =[f for f in os.listdir("data/raw") if f.endswith(".txt")]
    for file_name in raw_files:
        with open(os.path.join("data/raw", file_name), 'r', encoding='utf-8') as f:
            text = f.read()
            triples = extractor.extract(text)
            all_raw_triples.extend(triples)
    print(f"   ✅ 初步扫描完成，共挖掘出 {len(all_raw_triples)} 个原始三元组（存在冗余）。")

    # --- 4. 知识融合阶段 ---
    print("\n[阶段 4/5]: 知识融合与消歧 (Knowledge Fusion & Alignment) ------")
    fusion = KnowledgeFusion()
    final_triples = fusion.fuse(all_raw_triples)
    print(f"   ✅ 清洗、去重、对齐完成，最终保留高质量核心关联对: {len(final_triples)} 个。")

    # --- 5. 可视化阶段 ---
    print("\n[阶段 5/5]: 动态图谱渲染 (Graph Visualization) -------------------")
    if len(final_triples) > 0:
        os.makedirs("output", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        
        with open("data/processed/triples.json", 'w', encoding='utf-8') as f:
            json.dump(final_triples, f, ensure_ascii=False, indent=4)
            
        generate_graph(final_triples, "output/output_graph.html")
    else:
        print("   ⚠️ 警告：未提取到任何有效数据。")

    # --- 结束 ---
    end_time = time.time()
    elapsed = end_time - start_time
    print("\n" + "="*70)
    print(f" 🎉 Pipeline 运行成功！(总耗时: {elapsed:.2f} 秒)")
    print(f" 📂 最终图谱已生成，请在浏览器中打开: output/output_graph.html")
    print("="*70)

if __name__ == "__main__":
    run_pipeline()