import os
import json
import networkx as nx
from pyvis.network import Network

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'triples.json')
OUTPUT_HTML_PATH = os.path.join(BASE_DIR, 'output', 'turing_kg.html')

def load_triples(file_path):
    """读取前面抽取出来的三元组数据"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到数据文件：{file_path}。请先运行 src/extract.py")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_knowledge_graph(triples):
    """使用 NetworkX 构建有向图"""
    G = nx.DiGraph()
    for subject, predicate, obj in triples:
        # 添加节点
        G.add_node(subject, title=subject, color="#00a8ff" if subject=="艾伦·图灵" else "#9c88ff")
        G.add_node(obj, title=obj, color="#fbc531")
        # 添加边（关系）
        G.add_edge(subject, obj, label=predicate)
    return G

def visualize_graph(G, output_path):
    """使用 PyVis 生成交互式网页图谱"""
    # 初始化网络，设置暗色主题显得高级
    net = Network(height='800px', width='100%', bgcolor='#222222', font_color='white', directed=True)
    net.from_nx(G)
    
    # 优化物理引擎布局，使节点展开更好看
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200, spring_strength=0.05, damping=0.09)
    
    # 确保存储输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    net.write_html(output_path)
    print(f"知识图谱已成功生成！\n请用浏览器打开此文件查看: {os.path.abspath(output_path)}")

def main():
    print("开始构建知识图谱...")
    triples = load_triples(JSON_PATH)
    kg_graph = create_knowledge_graph(triples)
    visualize_graph(kg_graph, OUTPUT_HTML_PATH)

if __name__ == "__main__":
    main()