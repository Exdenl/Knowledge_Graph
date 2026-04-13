import os
import json
import networkx as nx
from pyvis.network import Network

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'triples.json')
OUTPUT_HTML_PATH = os.path.join(BASE_DIR, 'output', 'universal_kg.html')

# ==========================================
# 映射标准 NLP NER 标签到视觉样式
# LTP 标签说明: Nh(人名), Ni(机构), Ns(地名), CONCEPT(其他通用名词)
# ==========================================
TAG_STYLES = {
    "Nh": {"color": "#e74c3c", "size": 40, "shape": "dot", "label": "人物"}, 
    "Ni": {"color": "#3498db", "size": 30, "shape": "hexagon", "label": "机构"}, 
    "Ns": {"color": "#2ecc71", "size": 30, "shape": "square", "label": "地点"},
    "CONCEPT": {"color": "#f1c40f", "size": 20, "shape": "dot", "label": "概念/物品"}
}

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_universal_graph(data):
    G = nx.DiGraph()
    
    # 动态计算节点权重（连接度越高的节点越大）
    node_degrees = {}
    for item in data:
        node_degrees[item["head"]["name"]] = node_degrees.get(item["head"]["name"], 0) + 1
        node_degrees[item["tail"]["name"]] = node_degrees.get(item["tail"]["name"], 0) + 1

    for item in data:
        head = item["head"]
        tail = item["tail"]
        rel = item["relation"]
        
        # 获取样式配置
        h_style = TAG_STYLES.get(head["type"], TAG_STYLES["CONCEPT"])
        t_style = TAG_STYLES.get(tail["type"], TAG_STYLES["CONCEPT"])
        
        # 动态大小：基础大小 + 连接度加成
        h_size = h_style["size"] + (node_degrees.get(head["name"], 0) * 2)
        t_size = t_style["size"] + (node_degrees.get(tail["name"], 0) * 2)
        
        # 添加节点
        G.add_node(head["name"], title=f"AI识别类别: {h_style['label']}", color=h_style["color"], size=h_size, shape=h_style["shape"])
        G.add_node(tail["name"], title=f"AI识别类别: {t_style['label']}", color=t_style["color"], size=t_size, shape=t_style["shape"])
        
        # 添加边
        G.add_edge(head["name"], tail["name"], label=rel, color="#95a5a6", width=1.5)
        
    return G

def render_html(G, output_path):
    # 灰黑底色，突显科学感
    net = Network(height='100vh', width='100%', bgcolor='#1e272e', font_color='#d2dae2', directed=True)
    net.from_nx(G)
    
    # 通用的力导向图配置
    net.force_atlas_2based(
        gravity=-80,          
        central_gravity=0.01, 
        spring_length=150,    
        spring_strength=0.05, 
        damping=0.5           
    )
    
    net.toggle_physics(True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    net.write_html(output_path)
    print(f"🎉 泛化知识图谱渲染完成！\n👉 请在浏览器中打开: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    data = load_data(JSON_PATH)
    graph = build_universal_graph(data)
    render_html(graph, OUTPUT_HTML_PATH)