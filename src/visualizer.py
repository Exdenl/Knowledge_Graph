# src/visualizer.py
import networkx as nx
from pyvis.network import Network
import os

def generate_graph(triples_data, output_path="output_graph.html"):
    print("[可视化模块] 正在渲染知识图谱页面...")
    G = nx.DiGraph()
    
    for item in triples_data:
        h, r, t = item['head'], item['rel'], item['tail']
        
        # 针对主角特殊高亮
        h_color = "#e74c3c" if h == "艾伦·图灵" else "#3498db"
        t_color = "#e74c3c" if t == "艾伦·图灵" else "#2ecc71"
        h_size = 40 if h == "艾伦·图灵" else 20
        t_size = 40 if t == "艾伦·图灵" else 20

        G.add_node(h, color=h_color, size=h_size)
        G.add_node(t, color=t_color, size=t_size)
        G.add_edge(h, t, label=r, color="#7f8c8d")
        
    # 渲染配置
    net = Network(height='800px', width='100%', bgcolor='#1e272e', font_color='white', directed=True)
    net.from_nx(G)
    net.force_atlas_2based(gravity=-60, spring_length=150)
    
    # --- 修复 Bug 的核心逻辑 ---
    dir_name = os.path.dirname(output_path)
    if dir_name:  # 只有当路径不为空时才创建目录
        os.makedirs(dir_name, exist_ok=True)
    # -------------------------
    
    net.write_html(output_path)
    print(f"[可视化模块] 🎉 渲染成功！图谱文件已生成在当前目录下: {output_path}")